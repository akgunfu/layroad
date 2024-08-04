from abc import ABC, abstractmethod
from typing import Tuple

from .point import Point


class Shape(ABC):
    def __init__(self, pos: Point, width: int, height: int):
        self.pos = pos
        self.width = width
        self.height = height

    def __eq__(self, other):
        return (self.pos.x == other.pos.x and self.pos.y == other.pos.y and
                self.width == other.width and self.height == other.height)

    def __hash__(self):
        return hash((self.pos.x, self.pos.y, self.width, self.height))

    def bounds(self) -> Tuple[int, int, int, int]:
        return self.pos.x, self.pos.x + self.width, self.pos.y, self.pos.y + self.height

    def has_spanning_axis(self, other: 'Shape') -> Tuple[bool, str]:
        if max(self.pos.x, other.pos.x) < min(self.pos.x + self.width, other.pos.x + other.width):
            return True, 'x'
        elif max(self.pos.y, other.pos.y) < min(self.pos.y + self.height, other.pos.y + other.height):
            return True, 'y'
        else:
            return False, None

    def get_spanning_axis_range(self, other: 'Shape') -> Tuple[int, int]:
        """Get the overlapping range on the specified axis."""
        intersects, axis = self.has_spanning_axis(other)
        if not intersects:
            raise Exception("Not intersecting rectangle")

        if axis == 'x':
            start = max(self.pos.x, other.pos.x)
            end = min(self.pos.x + self.width, other.pos.x + other.width)
        else:
            start = max(self.pos.y, other.pos.y)
            end = min(self.pos.y + self.height, other.pos.y + other.height)
        return start, end

    def get_bounding_range(self, other: 'Shape', discontinuity: int) -> Tuple[int, int]:
        intersects, axis = self.has_spanning_axis(other)
        if not intersects:
            raise Exception("Not intersecting rectangle")

        if axis == 'x':
            bound_start = min(self.pos.y + self.height, other.pos.y + other.height) + discontinuity
            bound_end = max(self.pos.y, other.pos.y) - discontinuity
        else:
            bound_start = min(self.pos.x + self.width, other.pos.x + other.width) + discontinuity
            bound_end = max(self.pos.x, other.pos.x) - discontinuity
        return bound_start, bound_end

    def is_nested_within(self, other: 'Shape') -> bool:
        return (self.pos.x >= other.pos.x and self.pos.y >= other.pos.y and
                self.pos.x + self.width <= other.pos.x + other.width and
                self.pos.y + self.height <= other.pos.y + other.height)

    @abstractmethod
    def to_json(self) -> str:
        """Abstract method to convert a shape to a JSON string."""
        pass
