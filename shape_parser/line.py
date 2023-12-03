# MBTA MAP
# @Author: Zev Pogrebin
# 2023

"""Contains classes for representing lines."""

import pandas as pd
import svgwrite
import svgpathtools

class Line:

    """Represents a line."""

    shape_df: pd.DataFrame = None
    line_width: float = 1
    opacity: float = 1

    route_id: str = None
    route_name: str = None
    route_type: str = None
    route_color: str = None
    route_text_color: str = None
    shape_id: str = None

    def __init__(self, shape_df: pd.DataFrame):
        self.shape_df = shape_df
        self.route_id = shape_df["route_id"].iloc[0]
        self.route_name = shape_df["route_name"].iloc[0]
        self.route_type = shape_df["route_type"].iloc[0]
        self.route_color = f"#{shape_df["route_color"].iloc[0]}"
        self.route_text_color = f"#{shape_df["route_text_color"].iloc[0]}"
        self.shape_ids = shape_df["shape_id"].unique()

    def render(self, dwg: svgwrite.Drawing, map_bounds: tuple):
        """Renders the line on a drawing."""
        self.render_direction(0, dwg, map_bounds)
        self.render_direction(1, dwg, map_bounds)
        print(f"Rendered line {self.route_id}")

    def render_direction(
            self, direction, dwg: svgwrite.Drawing, map_bounds: tuple
    ):
        """Renders the line's direction on a drawing."""
        shape = self.shape_df[self.shape_df.direction_id == direction]
        for shape_id in shape.shape_id.unique():
            this_shape = self.shape_df[self.shape_df.shape_id == shape_id]
            self.render_shapes(direction, dwg, map_bounds, this_shape)
    
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
        if direction == "0":
            path = self.offset_curve(path, self.line_width)
        elif direction == "1":
            path = self.offset_curve(path, -self.line_width)

        points = [(float(segment.start.real), float(segment.start.imag)) for segment in path]
        # Convert the path to an svgwrite.shapes.Path object
        line = dwg.polyline(
            points=points, 
            stroke=self.route_color,
            stroke_width=self.line_width,
            fill="none",
            opacity=self.opacity
        )
        return line

    def offset_curve(path, offset_distance, steps=1000):
        """
        Takes in a Path object, `path`, and a distance,
        `offset_distance`, and outputs an piecewise-linear approximation 
        of the 'parallel' offset curve.
        """
        nls = []
        for seg in path:
            ct = 1
            for k in range(steps):
                t = k / steps
                offset_vector = offset_distance * seg.normal(t)
                nl = Line(seg.point(t), seg.point(t) + offset_vector)
                nls.append(nl)
        connect_the_dots = [
            Line(nls[k].end, nls[k+1].end) for k in range(len(nls)-1)
        ]
        if path.isclosed():
            connect_the_dots.append(Line(nls[-1].end, nls[0].end))
        offset_path = svgpathtools.Path(*connect_the_dots)
        return offset_path

class LightRail(Line):

    """Represents a light rail line."""

    line_width = 0.25
    opacity = 0.5

class Subway(Line):
    
    """Represents a subway line."""

    line_width = 0.5
    opacity = 0.7

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

def make_line(shape_df: pd.DataFrame) -> Line:
    """Makes a line from a shape dataframe."""
    return _LINE_TYPES[shape_df["route_type"].iloc[0]](shape_df)