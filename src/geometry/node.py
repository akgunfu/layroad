import json

from .point import Point
from .shape import Shape


class Node(Shape):
    _id_counter = 1

    def __init__(self, point: Point):
        super().__init__(point, 0, 0)
        self.id = Node._id_counter
        Node._id_counter += 1
        self.links = {}  # Dictionary of connected node id and distance
        self.connection = None

    def __str__(self):
        connections_str = ', '.join([f"Node {nid} (distance: {dist})" for nid, dist in self.links.items()])
        return f"Node {self.id} at {self.pos}, Connected to: {connections_str}"

    def identifier(self):
        return f'N{self.id}'

    def add_link(self, other: 'Node'):
        if other.id not in self.links:
            distance = self.distance(other)
            self.links[other.id] = distance

    def set_connection(self, connection: 'Shape'):
        self.connection = connection.identifier()

    def to_json(self) -> str:
        """Return a JSON string representation of the node."""
        return json.dumps({
            'type': 'node',
            'id': self.id,
            'x': self.pos.x,
            'y': self.pos.y,
            'links': self.links.__str__(),
            'connection': self.connection
        })
