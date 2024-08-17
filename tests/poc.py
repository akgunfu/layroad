import random

import matplotlib.pyplot as plt
import networkx as nx

from grid_manager import create_grid, generate_random_shapes
from pathfinding import Pathfinding
from tsp_solver import calculate_tsp_path, visualize_tsp_path


def visualize_graph(_rectangles, _distances, _grid_size):
    graph = nx.Graph()
    # Add nodes with positions
    positions = {}
    for rect in _rectangles:
        x_center = (rect.pos.x + rect.width) // 2
        y_center = (rect.pos.y + rect.height) // 2
        positions[rect.id] = (x_center, _grid_size - y_center)  # networkx graph is inverted so we revert it back
        graph.add_node(rect.id, pos=positions[rect.id])
    # Add edges with distances as weights
    for (start_id, end_id), distance in _distances.items():
        graph.add_edge(start_id, end_id, weight=distance)
    # Get positions of nodes and edges for visualization
    positions = nx.get_node_attributes(graph, 'pos')
    edge_labels = nx.get_edge_attributes(graph, 'weight')
    # Draw
    plt.figure(figsize=(10, 10))
    plt.gca().set_aspect('equal', adjustable='box')  # keeps aspect ratio
    #
    nx.draw(graph, positions, with_labels=True, node_color='lightblue', node_size=500, font_size=10)
    nx.draw_networkx_edge_labels(graph, positions, edge_labels=edge_labels, font_size=8)
    plt.show()


def tsp_for_an_order(_rectangles, _obstacles, _distances, _grid_size):
    # HERE is the actual shortest path calculation, since we already precalculated each static distance once
    # now we can simply find corresponding nodes and run tsp on it immediately
    # Randomly select some nodes for POC calculations, in the real scenario we will find those nodes by checking items
    selected_rectangles = random.sample(_rectangles, random.randint(2, 5))
    selected_ids = [rect.id for rect in selected_rectangles]
    # TSP calculation is O((N-1)! * N)
    # This calculation will be handled by OrTools since it is permutation based
    # But up to N=7,8 it can still be handled internally very effectively (up to 40320 permutations easy for a loop)
    tsp_path, tsp_distance = calculate_tsp_path(_distances, selected_ids, terminal_rect.id)
    print(f"Shortest closed path: {tsp_path} with distance {tsp_distance:.2f}")
    visualize_tsp_path(_grid_size, _rectangles, _obstacles, tsp_path, paths)


if __name__ == "__main__":
    grid_size = 100  # G
    num_rectangles = 10  # N
    num_obstacles = 10
    # FOLLOWING steps will only be calculated once per layout and results will be saved
    # Generate shapes, in the real scenario we will know these beforehand since they will be saved
    terminal_rect, rectangles, obstacles = generate_random_shapes(grid_size, num_rectangles, num_obstacles)
    # Create the grid filled with rect ids and obstacles so that we can run dijkstra on it
    grid = create_grid(grid_size, rectangles + obstacles)
    # Calculate all distances between each node combination to represent layout as graph
    distances, paths = Pathfinding.calculate_all_distances(rectangles, grid)
    #
    visualize_graph(rectangles, distances, grid_size)
    # UNTIL HERE complexity is O(N^2 * G^2 * log G) => this will only be calculated once
    # G is expected to be up to 100-200, N is expected to be 10-200
    # For phase 1 the numbers will be much smaller, but in the case we really use image processing the represent
    # every real shelf as rectangles numbers should be around G:200 and N:200-250
    # Still passable as one time only loading phase
    tsp_for_an_order(rectangles, obstacles, distances, grid_size)
