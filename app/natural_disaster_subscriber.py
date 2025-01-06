#!/usr/bin/env python
# coding: utf-8

# -----------------------------------------------------------------------------
# Module: natural_disaster_subscriber.py
#
# Description: This module provides a Flask application for subscribing to
# natural disaster event data. It includes functionality to retrieve system
# coordinates dynamically using IP and to process event data from a pickled file.
#
# Copyright (c) 2025 Niloy Debnath
# -----------------------------------------------------------------------------


import os
import time
from dotenv import load_dotenv
import queue
import threading
from glob import glob
import pickle

from flask import Flask, jsonify
from openai import OpenAI

import pygame
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import redis
import requests

from config import AFFECTED_DISTANCE, AUDIO_DIR, EVENT_TYPE_DESCRIPTIONS, DATA_DIR

# Retrieve OpenAI API key from .env file
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
REDIS_CLIENT = redis.StrictRedis(host="localhost", port=6379, db=0)

# OpenAI API Configuration
client = OpenAI()
TTS_MODEL = "tts-1"


def get_system_coordinates():
    """Get the latitude and longitude of the system dynamically using IP."""

    try:
        response = requests.get("https://ipinfo.io/json")
        if response.status_code == 200 and response.json().get("loc"):
            lat, lng = map(float, response.json()["loc"].split(","))
            return lat, lng
    except Exception as e:
        print(f"Error fetching system coordinates: {e}")
    return None, None


def generate_audio(text, voice="alloy"):
    """Generate audio using OpenAI API."""

    speech_file_path = os.path.join(
        AUDIO_DIR,
        "disaster_audio_response.mp3",
    )
    response = client.audio.speech.create(model=TTS_MODEL, voice=voice, input=text)
    response.stream_to_file(speech_file_path)
    return str(speech_file_path)


def generate_disaster_response(event_type, event_description, event_city):
    """Generate a disaster response using OpenAI GPT."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.7,
        messages=[
            {
                "role": "system",
                "content": "You are a news reporter and a new disaster event has happened:\n\n"
                f"- Event Type: {event_type} ({event_description})\n"
                f"- Location: {event_city}\n\n"
                "Provide a concise and clear response for affected individuals."
                f"Also mention that they are receiving this message because they are within the affected area {AFFECTED_DISTANCE} kms.",
            }
        ],
    )
    return response.choices[0].message.content


def process_event(event_data):
    """Process the event data and notify if it's within AFFECTED_DISTANCE in kms."""

    event_type = event_data.get("event_type")
    event_description = EVENT_TYPE_DESCRIPTIONS.get(event_type)
    event_city = event_data.get("city")
    reported_lat = event_data.get("lat")
    reported_lng = event_data.get("lng")

    # Get system's current location
    system_lat, system_lng = get_system_coordinates()

    # Check if the reported location is within AFFECTED_DISTANCE km of the system's location
    if (
        geodesic((reported_lat, reported_lng), (system_lat, system_lng)).km
        >= AFFECTED_DISTANCE
    ):
        return None, None

    # Generate response text and audio
    response_text = generate_disaster_response(
        event_type,
        event_description,
        event_city,
    )
    audio_file_path = generate_audio(response_text)

    return response_text, audio_file_path


def delete_files(folder_path):
    """Delete all files in the given folder except ".gitkeep"."""

    try:
        # List all files and directories in the given folder
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            # Check if it is a file and not ".gitkeep"
            if os.path.isfile(file_path) and filename != ".gitkeep":
                os.remove(file_path)
                print(f"Deleted: {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

def play_audio(file_path):
    """Play audio."""
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

    # Wait for the audio to finish playing
    while pygame.mixer.music.get_busy():
        pygame.time.wait(100)

    # Stop and unload the file
    pygame.mixer.music.stop()
    pygame.mixer.quit()


def consume_messages():
    """Continuously consume messages by reading pickle files from the data directory."""

    while True:
        files_processed = False

        for file_path in glob(os.path.join(DATA_DIR, "*.pkl")):
            files_processed = True

            with open(file_path, "rb") as file:
                event_data = pickle.load(file)

            response_text, audio_file_path = process_event(event_data)

            if response_text and audio_file_path:
                msg = "Speaking Now!"
                print(
                    "*" * len(msg),
                    msg,
                    "*" * len(msg),
                    sep="\n",
                )
                play_audio(audio_file_path)

        delete_files(AUDIO_DIR)
        delete_files(DATA_DIR)

        if not files_processed:
            time.sleep(5)  # Wait 5 second before checking again


@app.route("/start_consumer", methods=["GET"])
def start_consumer():
    """API endpoint to start the consumer thread."""

    consumer_thread = threading.Thread(target=consume_messages, daemon=True)
    consumer_thread.start()
    return jsonify(
        {
            "message": "Consumer started!",
        }
    )


if __name__ == "__main__":
    delete_files(AUDIO_DIR)
    delete_files(DATA_DIR)
    app.run(host="localhost", port=5002, debug=True)
