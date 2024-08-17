import itertools

import matplotlib.pyplot as plt


def calculate_tsp_path(distances, selected_ids, terminal_id):
    """
    Calculate the shortest closed path (TSP) for the selected nodes, starting and ending at a specific node.

    Parameters:
    - distances: A dictionary with keys as tuples of node pairs and values as distances between them. ex (1,2): 8
    - selected_ids: A list of rectangle IDs to visit.
    - terminal_id: The ID of the rectangle where the path should start and end.

    Returns:
    - min_path: The shortest path found that starts and ends at terminal_id.
    - min_distance: The total distance of the shortest path.
    """
    min_path = None
    min_distance = float('inf')
    # Filter out the terminal_id from selected_ids since it will be fixed at the start and end
    remaining_ids = [rid for rid in selected_ids if rid != terminal_id]
    # Sort permutations by the distance of the first step from terminal_id
    # So that we can pick the closest node when traversing the loop
    permutations = sorted(itertools.permutations(remaining_ids), key=lambda perm: distances[(terminal_id, perm[0])])
    # Loop
    for perm in permutations:
        # Start the path with the distance from terminal_id to the first node in perm
        first_leg_distance = distances[(terminal_id, perm[0])]
        # Calculate the distance for all consecutive legs in the permutation
        internal_leg_distances = [
            distances[(perm[i], perm[i + 1])] for i in range(len(perm) - 1)
        ]
        # Calculate the distance to return to the terminal_id from the last node
        last_leg_distance = distances[(perm[-1], terminal_id)]
        # Sum up all distances for this permutation
        current_distance = first_leg_distance + sum(internal_leg_distances) + last_leg_distance
        # Check if this is the shortest path found so far
        if current_distance < min_distance:
            min_distance = current_distance
            min_path = (terminal_id,) + perm + (terminal_id,)
    return min_path, min_distance


def visualize_tsp_path(grid_size, rectangles, obstacles, tsp_path, paths):
    _, ax = plt.subplots()
    ax.set_xlim(0, grid_size)
    ax.set_ylim(0, grid_size)
    ax.set_xticks(range(0, grid_size + 1, 5))
    ax.set_yticks(range(0, grid_size + 1, 5))
    ax.grid(True, linewidth=0.25)
    # Hide axis labels and ticks but keep the grid
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.tick_params(left=False, bottom=False)
    # Plot rectangles
    for rect in rectangles:
        color = 'lightgreen' if rect.id in tsp_path else 'lightblue'
        patch = plt.Rectangle(
            (rect.pos.x, rect.pos.y), rect.width, rect.height,
            color=color
        )
        ax.add_patch(patch)
        ax.text(
            rect.pos.x + rect.width // 2, rect.pos.y + rect.height // 2, str(rect.id),
            ha='center', va='center', fontsize=10, color='black', weight='bold'
        )
    # Plot rectangles
    for obstacle in obstacles:
        patch = plt.Rectangle(
            (obstacle.pos.x, obstacle.pos.y), obstacle.width, obstacle.height,
            color="red"
        )
        ax.add_patch(patch)
        ax.text(
            obstacle.pos.x + obstacle.width // 2, obstacle.pos.y + obstacle.height // 2, "E",
            ha='center', va='center', fontsize=10, color='black', weight='bold'
        )
    # Plot the TSP path using actual paths
    path_ids = list(tsp_path) + [tsp_path[0]]  # Closing the loop
    for i in range(len(path_ids) - 1):
        rect1_id = path_ids[i]
        rect2_id = path_ids[i + 1]
        # Retrieve the actual path between the two rectangles
        actual_path = paths.get((rect1_id, rect2_id))
        if actual_path:
            xs, ys = zip(*actual_path)
            ax.plot(xs, ys, linewidth=2)

    plt.title("->".join(map(str, tsp_path)))
    plt.gca().invert_yaxis()
    plt.show()
