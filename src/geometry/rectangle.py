import json

from .point import Point
from .shape import Shape


class Rectangle(Shape):
    _id_counter = 1

    def __init__(self, x: int, y: int, w: int, h: int):
        """Initialize a Rectangle with given attributes."""
        super().__init__(Point(x, y), w, h)
        self.id = Rectangle._id_counter
        Rectangle._id_counter += 1
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.cluster = None

    def __iter__(self):
        """Allow unpacking rectangle attributes."""
        return iter((self.x, self.y, self.w, self.h))

    def identifier(self):
        return f'R{self.id}'

    def size(self) -> int:
        """Calculate the size of the rectangle."""
        return self.w * self.h

    def center(self) -> 'Point':
        """Calculate the centroid (middle point) of the rectangle."""
        return Point(self.x + self.w // 2, self.y + self.h // 2)

    def contains(self, point: Point) -> bool:
        """Check if the rectangle contains the given point."""
        return self.x <= point.x <= self.x + self.w and self.y <= point.y <= self.y + self.h

    def set_cluster(self, cluster):
        """Set the cluster ID for the rectangle."""
        self.cluster = cluster

    def to_json(self) -> str:
        """Return a JSON string representation of the rectangle."""
        return json.dumps({
            'type': 'rectangle',
            'id': self.id,
            'x': self.pos.x,
            'y': self.pos.y,
            'w': self.w,
            'h': self.h
        })
