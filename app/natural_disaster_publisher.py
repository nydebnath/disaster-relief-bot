#!/usr/bin/env python
# coding: utf-8

# -----------------------------------------------------------------------------
# Module: natural_disaster_publisher.py
#
# Description: This module provides a Flask application for publishing natural
# disaster event data. It includes functionality to get coordinates from a
# location and to publish event data to a pickled file.
#
# Since I couldn’t find a decent free one to use and the good ones
# apparently come with a price tag ://
#
# Copyright (c) 2025 Niloy Debnath
# -----------------------------------------------------------------------------

import os
import pickle

from flask import Flask, jsonify, request
import redis
import json
from geopy.geocoders import Nominatim

from config import EVENT_TYPE_DESCRIPTIONS, DATA_DIR

app = Flask(__name__)


def get_coordinates_from_location(city, state, country):
    """Get the latitude and longitude of a location."""

    geolocator = Nominatim(user_agent="geoapi")
    location = geolocator.geocode(f"{city}, {state}, {country}")
    if location:
        return location.latitude, location.longitude
    else:
        return None, None


def publish_message(event_data):
    """Serialize event data and save to a pickle file."""

    file_path = os.path.join(
        DATA_DIR,
        f"event_{event_data['event_type']}_{event_data['city']}.pkl",
    )
    with open(file_path, "wb") as file:
        pickle.dump(event_data, file)


@app.route("/publish", methods=["POST"])
def publish():
    """API endpoint to publish an event.

    Excepts a JSON payload:
    {
        "event_type": "EQ",
        "city": "San Francisco",
        "state": "California",
        "country": "USA"
    }
    """

    event_data = request.get_json()
    lat, lng = get_coordinates_from_location(
        event_data.get("city"),
        event_data.get("state"),
        event_data.get("country"),
    )
    if lat is None or lng is None:
        return (
            jsonify(
                {
                    "error": "Invalid location provided.",
                }
            ),
            400,
        )

    event_data.update(
        {
            "lat": lat,
            "lng": lng,
        }
    )
    publish_message(event_data)

    return jsonify(
        {
            "message": "Event published successfully!",
            "event": {
                "event_type": event_data.get("event_type"),
                "city": event_data.get("city"),
                "state": event_data.get("state"),
                "country": event_data.get("country"),
                "description": EVENT_TYPE_DESCRIPTIONS.get(
                    event_data.get("event_type")
                ),
                "lat": lat,
                "lng": lng,
            },
        }
    )


if __name__ == "__main__":
    app.run(host="localhost", port=5001, debug=True)
