def solve(grid, start=(0, 0), end=None):
    height = len(grid)
    width = len(grid[0])
    if end is None:
        end = (width - 1, height - 1)

    stack = [start]
    visited = {start}
    parent_map = {start: None}

    directions = {
        'N': (0, -1, 1),
        'L': (1, 0, 2),
        'S': (0, 1, 4),
        'O': (-1, 0, 8)
    }

    while stack:
        curr_x, curr_y = stack.pop()

        if (curr_x, curr_y) == end:
            break

        cell_value = grid[curr_y][curr_x]

        for move, (dx, dy, bit) in directions.items():
            if cell_value & bit:
                nx, ny = curr_x + dx, curr_y + dy
                if (nx, ny) not in visited:
                    visited.add((nx, ny))
                    parent_map[(nx, ny)] = (curr_x, curr_y)
                    stack.append((nx, ny))

    path = []
    curr = end
    while curr is not None:
        path.append(curr)
        curr = parent_map.get(curr)
    return path[::-1]
