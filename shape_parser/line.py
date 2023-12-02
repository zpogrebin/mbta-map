# MBTA MAP
# @Author: Zev Pogrebin
# 2023

"""Contains classes for representing lines."""

import pandas as pd
import svgwrite

class Line:

    """Represents a line."""

    shape_df: pd.DataFrame = None
    line_width: float = 1

    route_id: str = None
    route_name: str = None
    route_type: str = None
    route_color: str = None
    route_text_color: str = None
    direction_id: str = None
    direction_name: str = None
    shape_id: str = None

    def __init__(self, shape_df: pd.DataFrame):
        self.shape_df = shape_df
        self.route_id = shape_df["route_id"].iloc[0]
        self.route_name = shape_df["route_name"].iloc[0]
        self.route_type = shape_df["route_type"].iloc[0]
        self.route_color = f"#{shape_df["route_color"].iloc[0]}"
        self.route_text_color = f"#{shape_df["route_text_color"].iloc[0]}"
        self.direction_id = shape_df["direction_id"].iloc[0]
        self.direction_name = shape_df["direction_name"].iloc[0]
        self.shape_id = shape_df["shape_id"].iloc[0]

    def render(self, dwg: svgwrite.Drawing, map_bounds: tuple):
        """Renders the line on a drawing."""
        shape = self.shape_df
        points = shape[["x", "y"]].values.tolist()
        # Shift points by the minimum x and y values
        points = [
            (point[0] - map_bounds[0], point[1] - map_bounds[2])
            for point in points
        ]
        line = dwg.polyline(
            points, 
            stroke=self.route_color,
            stroke_width=self.line_width,
            fill="none"
        )
        dwg.add(line)

class LightRail(Line):

    """Represents a light rail line."""

    line_width = 0.25

class Subway(Line):
    
    """Represents a subway line."""

    line_width = 0.5

class Rail(Line):

    """Represents a rail line."""

    line_width = 0.5

class Bus(Line):

    """Represents a bus line."""

    line_width = 0.1

class Ferry(Line):

    """Represents a ferry line."""

    line_width = 0.25

class CableCar(Line):
    
    """Represents a cable car line."""

    line_width = 0.25

class Gondola(Line):

    """Represents a gondola line."""

    line_width = 0.25

class Funicular(Line):
    
    """Represents a funicular line."""
    
    line_width = 0.25

class TrolleyBus(Line):

    """Represents a trolleybus line."""

    line_width = 0.15

class Monorail(Line):

    """Represents a monorail line."""

    line_width = 0.4

_LINE_TYPES = {
    0: LightRail,
    1: Subway,
    2: Rail,
    3: Bus,
    4: Ferry,
    5: CableCar,
    6: Gondola,
    7: Funicular,
    11: TrolleyBus,
    12: Monorail
}

def make_line(shape_df: pd.DataFrame) -> Line:
    """Makes a line from a shape dataframe."""
    return _LINE_TYPES[shape_df["route_type"].iloc[0]](shape_df)