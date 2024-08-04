import json

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

    def length(self) -> int:
        return ((self.end.x - self.start.x) ** 2 + (self.end.y - self.start.y) ** 2) ** 0.5

    def to_json(self) -> str:
        """Return a JSON string representation of the line."""
        return json.dumps({
            'type': 'line',
            'id': self.id,
            'length': self.length()
        })
