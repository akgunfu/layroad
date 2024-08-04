import json

from .point import Point
from .shape import Shape


class Rectangle(Shape):
    def __init__(self, idx: int, x: int, y: int, w: int, h: int):
        """Initialize a Rectangle with given attributes."""
        super().__init__(Point(x, y), w, h)
        self.id = idx
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.cluster = None

    def __iter__(self):
        """Allow unpacking rectangle attributes."""
        return iter((self.x, self.y, self.w, self.h))

    def size(self) -> int:
        """Calculate the size of the rectangle."""
        return self.w * self.h

    def center(self) -> 'Point':
        """Calculate the centroid (middle point) of the rectangle."""
        return Point(self.x + self.w // 2, self.y + self.h // 2)

    def set_cluster(self, cluster):
        """Set the cluster ID for the rectangle."""
        self.cluster = cluster

    def to_json(self) -> str:
        """Return a JSON string representation of the rectangle."""
        return json.dumps({
            'type': 'rectangle',
            'id': self.id,
            'x': self.x,
            'y': self.y,
            'w': self.w,
            'h': self.h
        })
