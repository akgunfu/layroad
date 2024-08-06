from typing import List, Set

from .geometry import Node, Line, Rectangle


class NodeGenerator:
    def __init__(self, rects: List[Rectangle], lines: List[Line]):
        self.rects = rects
        self.lines = lines
        self.nodes = set()

    def generate(self):
        self._find_intersections()
        self._connect_nodes_along_lines()
        return list(self.nodes)

    def _find_intersections(self) -> Set[Node]:
        for i in range(len(self.lines)):
            for j in range(i + 1, len(self.lines)):
                if self.lines[i].intersects(self.lines[j]):
                    intersection = self.lines[i].intersection_point(self.lines[j])
                    if intersection:
                        self.nodes.add(Node(intersection))
        return self.nodes

    def _connect_nodes_along_lines(self) -> None:
        for line in self.lines:
            line_nodes = [node for node in self.nodes if line.is_point_on_line(node.pos)]
            line_nodes.sort(key=lambda n: n.distance(line))
            # Handle regular node connections
            for i in range(len(line_nodes) - 1):
                node = line_nodes[i]
                next_node = line_nodes[i + 1]
                node.add_link(next_node)
                next_node.add_link(node)
            # Handle rectangle node connections (terminal nodes)
            self._handle_rectangle_node_connections(line, line_nodes)

    def _handle_rectangle_node_connections(self, line: Line, line_nodes: List[Node]) -> None:
        start_connected = any(node.pos == line.start for node in line_nodes)
        end_connected = any(node.pos == line.end for node in line_nodes)

        if not start_connected and line_nodes:
            for rect in self.rects:
                if rect.contains(line.start):
                    terminal_node = Node(rect.center())
                    terminal_node.add_link(line_nodes[0])
                    terminal_node.set_connection(rect)
                    line_nodes[0].add_link(terminal_node)
                    self.nodes.add(terminal_node)
                    break

        if not end_connected and line_nodes:
            for rect in self.rects:
                if rect.contains(line.end):
                    terminal_node = Node(rect.center())
                    terminal_node.add_link(line_nodes[-1])
                    terminal_node.set_connection(rect)
                    line_nodes[-1].add_link(terminal_node)
                    self.nodes.add(terminal_node)
                    break
