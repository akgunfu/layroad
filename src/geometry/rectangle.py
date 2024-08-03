import json
from typing import Tuple

from .point import Point
from .shape import Shape


class Rectangle(Shape):
    def __init__(self, idx: int, x: int, y: int, w: int, h: int):
        """Initialize a Rectangle with given attributes."""
        self.id = idx
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.cluster = None
        self.links = []

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

    def add_links(self, links):
        self.links.update(links)

    def is_identical(self, other: 'Rectangle') -> bool:
        """Check if two rectangles have the same dimensions and position."""
        return (self.x == other.x and self.y == other.y and
                self.w == other.w and self.h == other.h)

    def is_nested_within(self, other: 'Rectangle') -> bool:
        """Check if this rectangle is nested within another rectangle."""
        return (self.x >= other.x and self.y >= other.y and
                self.x + self.w <= other.x + other.w and
                self.y + self.h <= other.y + other.h)

    def intersects(self, other: 'Rectangle', axis) -> bool:
        """Check if ranges of two rectangles intersect based on the specified axis."""
        if axis == 'x':
            return max(self.x, other.x) < min(self.x + self.w, other.x + other.w)
        else:
            return max(self.y, other.y) < min(self.y + self.h, other.y + other.h)

    def get_intersection_range(self, other: 'Rectangle', axis) -> Tuple[int, int]:
        """Get the overlapping range on the specified axis."""
        if axis == 'x':
            start = max(self.x, other.x)
            end = min(self.x + self.w, other.x + other.w)
        else:
            start = max(self.y, other.y)
            end = min(self.y + self.h, other.y + other.h)
        return start, end

    def get_bounding_range(self, other: 'Rectangle', axis, discontinuity: int) -> Tuple[int, int]:
        """Get the bounding range between two rectangles on the specified axis."""
        if axis == 'x':
            bound_start = min(self.y + self.h, other.y + other.h) + discontinuity
            bound_end = max(self.y, other.y) - discontinuity
        else:
            bound_start = min(self.x + self.w, other.x + other.w) + discontinuity
            bound_end = max(self.x, other.x) - discontinuity
        return bound_start, bound_end

    def to_json(self):
        """Return a JSON string representation of the rectangle."""
        return json.dumps({
            'type': 'rectangle',
            'id': self.id,
            'x': self.x,
            'y': self.y,
            'w': self.w,
            'h': self.h,
            'links': self.links
        })
