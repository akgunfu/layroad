import json
from typing import Optional

from .point import Point
from .shape import Shape


class Line(Shape):
    _id_counter = 1

    def __init__(self, start: Point, end: Point):
        super().__init__(start, end.x - start.x, end.y - start.y)
        self.id = Line._id_counter
        Line._id_counter += 1
        self.start = start
        self.end = end

    def identifier(self):
        return f'L{self.id}'

    def length(self) -> int:
        return ((self.end.x - self.start.x) ** 2 + (self.end.y - self.start.y) ** 2) ** 0.5

    def intersects(self, other: 'Line') -> bool:
        # Check if one line is vertical and the other is horizontal
        if ((self.start.x == self.end.x and other.start.y == other.end.y) or
                (self.start.y == self.end.y and other.start.x == other.end.x)):
            # Check if they intersect
            return (min(self.start.x, self.end.x) <= other.start.x <= max(self.start.x, self.end.x) and
                    min(other.start.y, other.end.y) <= self.start.y <= max(other.start.y, other.end.y)) or \
                (min(other.start.x, other.end.x) <= self.start.x <= max(other.start.x, other.end.x) and
                 min(self.start.y, self.end.y) <= other.start.y <= max(self.start.y, self.end.y))
        return False

    def intersection_point(self, other: 'Line') -> Optional[Point]:
        if self.intersects(other):
            if self.start.x == self.end.x:  # self is vertical, other is horizontal
                return Point(self.start.x, other.start.y)
            else:  # self is horizontal, other is vertical
                return Point(other.start.x, self.start.y)
        return None

    def is_point_on_line(self, point: Point) -> bool:
        if self.start.x == self.end.x:  # Vertical line
            return point.x == self.start.x and min(self.start.y, self.end.y) <= point.y <= max(self.start.y, self.end.y)
        else:  # Horizontal line
            return point.y == self.start.y and min(self.start.x, self.end.x) <= point.x <= max(self.start.x, self.end.x)

    def to_json(self) -> str:
        """Return a JSON string representation of the line."""
        return json.dumps({
            'type': 'line',
            'id': self.id,
            'x': self.pos.x,
            'y': self.pos.y,
            'w': self.width,
            'h': self.height
        })
