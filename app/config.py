#!/usr/bin/env python
# coding: utf-8

# -----------------------------------------------------------------------------
# Module: config.py
#
# Copyright (c) 2025 Niloy Debnath
# -----------------------------------------------------------------------------

import os

EVENT_TYPE_DESCRIPTIONS = {
    "TN": "Large waves caused by underwater disturbances or seismic activity.",
    "EQ": "Sudden ground shaking from tectonic movements or volcanic activity.",
    "TC": "Powerful rotating storms like hurricanes, cyclones, or typhoons.",
    "WF": "Uncontrolled fires spreading in forested or grassland areas.",
    "FL": "Overflowing water from rivers, lakes, or heavy rainfall causing flooding.",
    "ET": "Extreme weather events including heatwaves, cold spells, or severe temperatures.",
    "DR": "Prolonged dry periods leading to water scarcity and agricultural challenges.",
    "SW": "Severe atmospheric disturbances such as thunderstorms or hailstorms.",
    "SI": "Hazardous conditions caused by the presence or movement of sea ice.",
    "VO": "Volcanic eruptions emitting lava, ash, and gases from the Earth's crust.",
    "LS": "Mass movement of soil, rocks, or debris triggered by gravity or other factors."
}


DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data",
)

AUDIO_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "audio",
)

AFFECTED_DISTANCE = 200  # km