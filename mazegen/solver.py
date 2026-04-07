from typing import List, Tuple, Dict, Optional


def solve(
    grid: List[List[int]],
    start: Tuple[int, int] = (0, 0),
    end: Optional[Tuple[int, int]] = None,
) -> List[Tuple[int, int]]:
    """
    Find path between two points using DFS and bitwise logic.

    Args:
        grid (List[List[int]]): The maze matrix in bitwise format.
        start (Tuple[int, int]): Starting coordinate (x, y).
        end (Optional[Tuple[int, int]]): End coordinate, or None for corner.

    Returns:
        List[Tuple[int, int]]: List of coordinates forming the path.
    """
    height: int = len(grid)
    width: int = len(grid[0])

    if end is None:
        end = (width - 1, height - 1)

    stack: List[Tuple[int, int]] = [start]
    visited: set[Tuple[int, int]] = {start}
    parent_map: Dict[Tuple[int, int],
                     Optional[Tuple[int, int]]] = {start: None}

    # Standard directions according to PDF (N, E, S, W)
    directions: Dict[str, Tuple[int, int, int]] = {
        'N': (0, -1, 1),
        'E': (1, 0, 2),
        'S': (0, 1, 4),
        'W': (-1, 0, 8)
    }

    while stack:
        curr_x, curr_y = stack.pop()

        if (curr_x, curr_y) == end:
            break

        cell_value: int = grid[curr_y][curr_x]

        for _, (dx, dy, bit) in directions.items():
            # 1. Check if wall is open using bit
            if cell_value & bit:
                nx, ny = curr_x + dx, curr_y + dy

                # 2. Check bounds and if already visited
                if (
                    0 <= nx < width and 0 <= ny < height
                    and (nx, ny) not in visited
                ):
                    visited.add((nx, ny))
                    parent_map[(nx, ny)] = (curr_x, curr_y)
                    stack.append((nx, ny))

    # Path reconstruction (Backtracking)
    path: List[Tuple[int, int]] = []

    # If the destination was never reached, return empty list
    if end not in parent_map:
        return []

    curr: Optional[Tuple[int, int]] = end
    while curr is not None:
        path.append(curr)
        curr = parent_map.get(curr)

    return path[::-1]
