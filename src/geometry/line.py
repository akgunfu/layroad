import json

from .point import Point
from .rectangle import Rectangle
from .shape import Shape


class Line(Shape):
    def __init__(self, start: Point, end: Point):
        self.start = start
        self.end = end

    def length(self) -> int:
        return ((self.end.x - self.start.x) ** 2 + (self.end.y - self.start.y) ** 2) ** 0.5

    def intersects(self, other: 'Line') -> bool:
        """Check if this line intersects with another line."""

        def ccw(point1: Point, point2: Point, point3: Point) -> bool:
            """Check if the points point1, point2, and point3 are listed in a counter-clockwise order."""
            return (point3.y - point1.y) * (point2.x - point1.x) > (point2.y - point1.y) * (point3.x - point1.x)

        p1, p2 = self.start, self.end
        p3, p4 = other.start, other.end
        # Two lines intersect if and only if the points p1, p2 are separated by line p3-p4 and vice versa
        return ccw(p1, p3, p4) != ccw(p2, p3, p4) and ccw(p1, p2, p3) != ccw(p1, p2, p4)

    def intersects_rectangle(self, rect: 'Rectangle') -> bool:
        """Check if this line intersects with a given rectangle."""
        # Check if either endpoint of the line is inside the rectangle
        if (rect.x <= self.start.x <= rect.x + rect.w and rect.y <= self.start.y <= rect.y + rect.h) or \
                (rect.x <= self.end.x <= rect.x + rect.w and rect.y <= self.end.y <= rect.y + rect.h):
            return True
        # Check for intersection with rectangle edges
        return (self.intersects(Line(Point(rect.x, rect.y), Point(rect.x + rect.w, rect.y))) or
                self.intersects(Line(Point(rect.x, rect.y), Point(rect.x, rect.y + rect.h))) or
                self.intersects(Line(Point(rect.x + rect.w, rect.y), Point(rect.x + rect.w, rect.y + rect.h))) or
                self.intersects(Line(Point(rect.x, rect.y + rect.h), Point(rect.x + rect.w, rect.y + rect.h))))

    def to_json(self) -> str:
        """Return a JSON string representation of the line."""
        return json.dumps({
            'type': 'line',
            'id': 1,  # todo add id to class later
            'start_x': self.start.x,
            'start_y': self.start.y,
            'end_x': self.end.x,
            'end_y': self.end.y
        })
