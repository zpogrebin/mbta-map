# MBTA MAP
# @Author: Zev Pogrebin
# 2023

"""Contains classes for representing lines."""

import pandas as pd
import svgwrite
import svgpathtools

from . import shape_tools

class Line:

    """Represents a line."""

    shape_df: pd.DataFrame = None

    line_width: float = 1
    opacity: float = 1
    offset_curves = False

    route_id: str = None
    route_name: str = None
    route_type: str = None
    route_color: str = None
    route_text_color: str = None
    shape_id: str = None

    drawing: svgwrite.Drawing = None

    def __init__(self, shape_df: pd.DataFrame):
        self.shape_df = shape_df
        self.route_id = shape_df["route_id"].iloc[0]
        self.route_name = shape_df["route_name"].iloc[0]
        self.route_type = shape_df["route_type"].iloc[0]
        self.route_color = f"#{shape_df["route_color"].iloc[0]}"
        self.route_text_color = f"#{shape_df["route_text_color"].iloc[0]}"
        self.shape_ids = shape_df["shape_id"].unique()

    def render_route(self, dwg: svgwrite.Drawing, map_bounds: tuple):
        """Renders the line on a drawing."""
        if dwg is None:
            self.drawing = dwg
        route_group = self.group(dwg, id=self.route_id)
        self.render_direction(0, route_group, map_bounds)
        self.render_direction(1, route_group, map_bounds)

    def render_direction(
            self, direction, dwg: svgwrite.Drawing, map_bounds: tuple
    ):
        """Renders the line's direction on a drawing."""
        shape = self.shape_df[self.shape_df.direction_id == direction]
        group = dwg.add(self.group(dwg, id=f"{self.route_id}-{direction}"))
        # for shape_id in shape.shape_id.unique():
        shape = shape.copy()
        shape.sort_values("shape_pt_sequence", inplace=True)
        # this_shape = self.shape_df[self.shape_df.shape_id == shape_id]
        self.render_shapes(direction, group, map_bounds, shape)
    
    def render_shapes(
            self, direction, dwg: svgwrite.Drawing, map_bounds: tuple,
            shape: pd.DataFrame
    ):
        points = shape[["x", "y"]].values.tolist()
        # Shift points by the minimum x and y values
        points = [
            (point[0] - map_bounds[0], point[1] - map_bounds[2])
            for point in points
        ]
        line = self.process_line(dwg, points, direction)
        if line.points != []:
            dwg.add(line)

    def process_line(self, dwg, points, direction=None):
        # Create a list of Line objects connecting the points
        lines = [
            svgpathtools.Line(start=complex(x1, y1), end=complex(x2, y2))
            for (x1, y1), (x2, y2) in zip(points[:-1], points[1:])
        ]

        # Create a Path object from the lines
        path = svgpathtools.Path(*lines)

        # Offset the path basedon the direction
        path = self.offset_curve_wrapper(path, direction)

        points = [
            (float(segment.start.real), float(segment.start.imag))
            for segment in path
        ]
        # Convert the path to an svgwrite.shapes.Path object
        line = self.drawing.polyline(
            points=points, 
            stroke=self.route_color,
            stroke_width=self.line_width,
            fill="none",
        )
        return line

    def offset_curve_wrapper(self, path, direction):
        """Wraps the offset_curve function."""
        if not self.offset_curves:
            return path
        path = shape_tools.offset_curve(path, -self.line_width)
        return path

    ############################################################################
    # Helper functions                                                         #
    ############################################################################

    def group(self, add_to: svgwrite.Drawing, id: str):
        """Adds a group to a drawing."""
        return add_to.add(self.drawing.g(id=id))
    
    ############################################################################
    # Dunders                                                                  #
    ############################################################################

    def __str__(self):
        return f"{self.route_name} ({self.route_id})"
    
    def __repr__(self):
        return f"{self.route_name} ({self.route_id})"

class LightRail(Line):

    """Represents a light rail line."""

    line_width = 0.35
    opacity = 0.5
    offset_curves = True

class Subway(Line):
    
    """Represents a subway line."""

    line_width = 0.5
    opacity = 0.7
    offset_curves = True

class Rail(Line):

    """Represents a rail line."""

    line_width = 0.5
    opacity = 0.5

class Bus(Line):

    """Represents a bus line."""

    line_width = 0.1
    opacity = 0.2

class Ferry(Line):

    """Represents a ferry line."""

    line_width = 0.25
    opacity = 0.3

class CableCar(Line):
    
    """Represents a cable car line."""

    line_width = 0.25
    opacity = 0.5

class Gondola(Line):

    """Represents a gondola line."""

    line_width = 0.25
    opacity = 0.3

class Funicular(Line):
    
    """Represents a funicular line."""
    
    line_width = 0.25
    opacity = 0.3

class TrolleyBus(Line):

    """Represents a trolleybus line."""

    line_width = 0.15
    opacity = 0.2

class Monorail(Line):

    """Represents a monorail line."""

    line_width = 0.4
    opacity = 0.5

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

_MODE_NAMES = {
    0: "Light Rail",
    1: "Subway",
    2: "Rail",
    3: "Bus",
    4: "Ferry",
    5: "Cable Car",
    6: "Gondola",
    7: "Funicular",
    11: "Trolleybus",
    12: "Monorail"

}

_LINE_OPACITIES = {
    0: 1,
    1: 1,
    2: 0.5,
    3: 0.2,
    4: 0.3,
    5: 0.5,
    6: 0.3,
    7: 0.3,
    11: 0.2,
    12: 0.5
}

_MODE_PRIORITY = [3, 5, 11, 6, 7, 4, 12, 2, 0, 1]

def make_line(shape_df: pd.DataFrame) -> Line:
    """Makes a line from a shape dataframe."""
    return _LINE_TYPES[shape_df["route_type"].iloc[0]](shape_df)