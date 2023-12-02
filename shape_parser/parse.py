# MBTA MAP
# @Author: Zev Pogrebin
# 2023

"""
Parses shapes from a shape SVG file and returns a list of shapes.
"""

import pathlib

import svg
import pandas as pd

# CONSTANTS
_SHAPE_FILE = pathlib.Path("./shape_parser/shapes.txt")
_OUTPUT_FILE = pathlib.Path("./shape_parser/shapes.svg")

class MapMaker:

    def __init__(self, shape_file=_SHAPE_FILE):
        self.load_shapes(shape_file)

    def load_shapes(self, shape_file=_SHAPE_FILE):
        self.shapes = []
        