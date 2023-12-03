# MBTA MAP
# @Author: Zev Pogrebin
# 2023

import svgpathtools
import svgwrite

def offset_curve(path: svgpathtools.Path, offset_distance: int, steps=10):
    """
    Takes in a Path object, `path`, and a distance,
    `offset_distance`, and outputs an piecewise-linear approximation 
    of the 'parallel' offset curve.

    From 
    [readme.md](https://github.com/mathandy/svgpathtools/tree/master)
    """
    nls = []
    for seg in path:
        ct = 1
        for k in range(steps):
            t = k / steps
            if seg.start == seg.end:
                continue
            offset_vector = offset_distance * seg.normal(t)
            nl = svgpathtools.Line(
                seg.point(t), seg.point(t) + offset_vector
            )
            nls.append(nl)
    connect_the_dots = [
        svgpathtools.Line(nls[k].end, nls[k+1].end)
        for k in range(len(nls)-1)
    ]
    if path.isclosed():
        connect_the_dots.append(svgpathtools.Line(nls[-1].end, nls[0].end))
    offset_path = svgpathtools.Path(*connect_the_dots)
    return offset_path