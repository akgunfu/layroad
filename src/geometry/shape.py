from abc import ABC, abstractmethod


class Shape(ABC):
    @abstractmethod
    def to_json(self) -> str:
        """Abstract method to convert a shape to a JSON string."""
        pass
