import random

import numpy as np

from src.geometry import Rectangle


def create_grid(grid_size, shapes):
    grid = np.zeros((grid_size, grid_size), dtype=int)
    for rect in shapes:
        for x in range(rect.pos.x, rect.pos.x + rect.width):
            for y in range(rect.pos.y, rect.pos.y + rect.height):
                grid[y][x] = rect.id  # Mark the rectangle area with the rectangle ID
    return grid


def generate_random_shapes(grid_size, num_rectangles, num_obstacles):
    rectangles = []
    obstacles = []
    start_rect = Rectangle(0, 0, 5, 5)  # simulate a fixed start position
    rectangles.append(start_rect)

    # function to check intersections, we don't want intersecting shapes in poc
    def intersects_any(existing_rectangles, _new_rect):
        return any(rect.pos.x <= _new_rect.pos.x + _new_rect.width and
                   rect.pos.x + rect.width >= _new_rect.pos.x and
                   rect.pos.y <= _new_rect.pos.y + _new_rect.height and
                   rect.pos.y + rect.height >= _new_rect.pos.y
                   for rect in existing_rectangles)

    # rectangles
    for _ in range(num_rectangles):
        while True:
            new_rect = _preview_new_shape(grid_size)
            # Check for intersection with existing rectangles
            if not intersects_any(rectangles, new_rect):
                rectangles.append(new_rect)
                break

    #  obstacles
    for _ in range(num_obstacles):
        while True:
            new_obstacle = _preview_new_shape(grid_size)
            # Check for intersection with existing rectangles or obstacles
            if not intersects_any(rectangles + obstacles, new_obstacle):
                obstacles.append(new_obstacle)
                break

    return start_rect, rectangles, obstacles


def _preview_new_shape(grid_size):
    width = random.randint(5, 15)
    height = random.randint(5, 15)
    x = random.randint(0, grid_size - width)
    y = random.randint(0, grid_size - height)
    new_rect = Rectangle(x, y, width, height)
    return new_rect
