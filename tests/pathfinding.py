import heapq
import math


class Pathfinding:

    @staticmethod
    def _find_terminal_point(rect):
        # For poc simply use center, but we can implement facing sides as terminal points for edge cases etc
        center_x = rect.pos.x + rect.width // 2
        center_y = rect.pos.y + rect.height // 2
        return center_x, center_y

    @staticmethod
    def dijkstra(grid, start_rect, end_rect):
        """
        Dijkstra's algorithm to find the shortest path from start_rect to end_rect on the grid.

        The distance represents the number of grid cells between the start and goal positions,
        considering both horizontal, vertical, and diagonal moves.

        Parameters:
        - grid: A 2D array representing the grid. Each cell is either 0 (empty) or an ID of a rectangle.
        - start_rect: The rectangle from which to start.
        - end_rect: The rectangle at which to end.

        Returns:
        - path: A list of tuples representing the grid cells in the shortest path from start to goal.
        - distance: The total distance in the shortest path.
        """
        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1),  # Horizontal and vertical
            (-1, -1), (-1, 1), (1, -1), (1, 1)  # Diagonal
        ]
        start = Pathfinding._find_terminal_point(start_rect)
        goal = Pathfinding._find_terminal_point(end_rect)

        stack = [(0, start)]
        distances = {start: 0}
        previous_nodes = {start: None}

        while stack:
            current_distance, current_position = heapq.heappop(stack)
            if current_position == goal:
                return (Pathfinding._reconstruct_path(previous_nodes, start, current_position),
                        math.floor(current_distance))

            if current_distance > distances.get(current_position, float('inf')):
                continue

            for neighbor in Pathfinding._get_neighbors(current_position, len(grid), directions):
                if Pathfinding._is_valid_neighbor(neighbor, grid, start_rect.id, end_rect.id):
                    if abs(neighbor[0] - current_position[0]) + abs(neighbor[1] - current_position[1]) == 2:
                        # Diagonal move
                        distance = current_distance + math.sqrt(2)
                    else:
                        # Horizontal or vertical move
                        distance = current_distance + 1

                    if distance < distances.get(neighbor, float('inf')):
                        distances[neighbor] = distance
                        previous_nodes[neighbor] = current_position
                        heapq.heappush(stack, (distance, neighbor))

        return [], float('inf')

    @staticmethod
    def _get_neighbors(position, grid_size, directions):
        x, y = position
        neighbors = []
        for dx, dy in directions:
            neighbor = (x + dx, y + dy)
            if 0 <= neighbor[0] < grid_size and 0 <= neighbor[1] < grid_size:
                neighbors.append(neighbor)
        return neighbors

    @staticmethod
    def _is_valid_neighbor(neighbor, grid, start_id, end_id):
        x, y = neighbor
        cell_value = grid[y][x]
        return cell_value == 0 or cell_value in [start_id, end_id]

    @staticmethod
    def _reconstruct_path(previous_nodes, start, goal):
        # backtrack the actual path
        path = []
        current_node = goal
        while current_node and current_node != start:
            path.append(current_node)
            current_node = previous_nodes.get(current_node)
        if current_node == start:
            path.append(start)
        return path[::-1]  # reverse the path, since we constructed from the last node

    @staticmethod
    def calculate_all_distances(rectangles, grid):
        distances = {}
        paths = {}
        for i in range(len(rectangles)):
            for j in range(i + 1, len(rectangles)):
                start_rect = rectangles[i]
                end_rect = rectangles[j]
                path, distance = Pathfinding.dijkstra(grid, start_rect, end_rect)
                if path:  # Ensure the path is valid
                    distances[(start_rect.id, end_rect.id)] = distance
                    distances[(end_rect.id, start_rect.id)] = distance  # Symmetric
                    paths[(start_rect.id, end_rect.id)] = path
                    paths[(end_rect.id, start_rect.id)] = path[::-1]  # Reverse for symmetry
                else:
                    print(f"Warning: No valid path found between {start_rect.id} and {end_rect.id}")
        return distances, paths
