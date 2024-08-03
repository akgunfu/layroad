from abc import ABC, abstractmethod
from typing import Tuple


class Shape(ABC):

    @abstractmethod
    def bounds(self) -> Tuple[int, int, int, int]:
        pass

    @abstractmethod
    def get_intersection_range(self, other: 'Shape', axis) -> Tuple[int, int]:
        pass

    @abstractmethod
    def get_bounding_range(self, other: 'Shape', axis, discontinuity: int) -> Tuple[int, int]:
        pass

    @abstractmethod
    def to_json(self) -> str:
        """Abstract method to convert a shape to a JSON string."""
        pass
