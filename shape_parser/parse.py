# MBTA MAP
# @Author: Zev Pogrebin
# 2023

"""
Parses shapes from a shape SVG file and returns a list of shapes.
"""

import pathlib

import svgwrite
import pandas as pd

from . import line

# CONSTANTS
_SHAPE_FILE = pathlib.Path("./shape_parser/shapes.txt")
_ROUTE_FILE = pathlib.Path("./shape_parser/shapes_by_route.csv")
_OUTPUT_FILE = pathlib.Path("./shape_parser/shapes.svg")

_BOSTON_ORIGIN = (42.3601, -71.0589)
_LAT_LONG_SCALE = 1000

class MapMaker:

    shapes = {}
    verbosity = 10

    shape_file = None
    route_file = None
    force = None

    map_bounds = None

    def __init__(
            self, shape_file=_SHAPE_FILE, route_file=_ROUTE_FILE,
            force_reanalysis=False
    ):
        self.force = force_reanalysis
        self.shape_file = shape_file
        self.route_file = route_file
        self.load_shapes()

    def _print(self, message, level=1):
        """Prints a message if the verbosity is greater than the level."""
        if self.verbosity >= level:
            print("   " * level + message)

    def load_shapes(self,):
        """Loads shapes from a shape file and adds them to the shapes list."""
        self._print("Loading shapes")
        self.shapes = []
        df = pd.read_csv(self.shape_file)
        self.analyze(df)
        for route_id in df.route_id.unique():
            self._print(f"Loading shape {route_id}", 3)
            points = df[df.route_id == route_id]
            shape_line = line.make_line(points)
            self.shapes.append(shape_line)

    def analyze(self, df: pd.DataFrame, save=True):
        """Analyzes the shapes dataframe."""
        self.add_route_data(df, save=True)
        self.convert_lat_long_to_points(df, save=True)
        self.get_map_bounds(df)
    
    def get_map_bounds(self, df: pd.DataFrame):
        self.map_bounds = []
        absolute_max_x = abs(df.x).max()
        absolute_max_y = abs(df.y).max()
        self.map_bounds = [
            -absolute_max_x, absolute_max_x, -absolute_max_y, absolute_max_y
        ]
    
    def add_route_data(self, df: pd.DataFrame, save=True):
        """Adds route data to the shapes dataframe based on the shape_id."""
        self._print("Adding route data")
        routes = pd.read_csv(self.route_file)
        routes.columns = [i.lower() for i in routes.columns]
        # Check if route columns are in the df, if so, return
        if self._check_df_for_columns(df, routes):
            return
        # Re-index the dataframe
        routes = routes.loc[~routes.shape_id.duplicated()]
        # Remove shape_ids that are not in the routes dataframe
        df = df[df.shape_id.isin(routes.shape_id)]
        # Remove duplicate columns
        routes = routes.set_index("shape_id")
        columns = routes.columns
        # Convert routes to a dictionary
        routes = routes.to_dict(orient="index")
        for column in columns:
            self._print(f"Adding {column} to shapes dataframe", 2)
            if column == "shape_id":
                continue
            df[column] = [
                routes[shape_id][column] for shape_id in df.shape_id
            ]
        # Save the dataframe
        if save:
            df.to_csv(self.shape_file, index=False)

    def convert_lat_long_to_points(self, df: pd.DataFrame, save=True):
        """Converts lat and long to x and y coordinates."""
        self._print("Converting lat and long to points")
        # Check if the columns are already in the dataframe
        if self._check_df_for_columns(df, pd.DataFrame({"x": [], "y": []})):
            return
        # Convert lat and long to x and y
        df["x"], df["y"] = zip(*df.apply(
            lambda row: self._lat_long_to_xy(
                row["shape_pt_lat"], 
                row["shape_pt_lon"]),
            axis=1
        ))
        # Save the dataframe
        if save:
            df.to_csv(self.shape_file, index=False)

    def _check_df_for_columns(self, df: pd.DataFrame, new: pd.DataFrame):
        """Checks if the new_df columns are in the df."""
        if self.force:
            return False
        if isinstance(new, pd.DataFrame):
            new = new.columns
        if all([i in df.columns for i in new]):
            self._print("Data already in dataframe :)", 2)
            return True
        return False

    def _lat_long_to_xy(self, lat, long):
        """Converts lat and long to x and y coordinates."""
        x = (long - _BOSTON_ORIGIN[1]) * _LAT_LONG_SCALE
        y = - (lat - _BOSTON_ORIGIN[0]) * _LAT_LONG_SCALE
        return x, y
    
    def make_svg(self, output_file=_OUTPUT_FILE):
        """Makes an SVG file from the shapes."""
        self._print("Making SVG")
        svgwrite.AUTHOR_EMAIL = "zpogrebin111@gmail.com"
        svgwrite.AUTHOR_NAME = "Zev Pogrebin"
        drawing: svgwrite.Drawing = svgwrite.Drawing(
            str(output_file), 
            size=(
                f"{self.map_bounds[1] - self.map_bounds[0]}px", 
                f"{self.map_bounds[3] - self.map_bounds[2]}px"
            )
        )
        for shape in self.shapes:
            shape: line.Line
            shape.render(drawing, map_bounds=self.map_bounds)
            self._print(f"Rendered shape {shape}", 3)
        drawing.save()