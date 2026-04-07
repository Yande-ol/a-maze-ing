from collections import deque
from typing import Dict, List, Set, Tuple


DIRECTIONS: Dict[str, Tuple[int, int, int, int]] = {
    "N": (0, -1, 1, 4),
    "E": (1, 0, 2, 8),
    "S": (0, 1, 4, 1),
    "W": (-1, 0, 8, 2),
}


def build_pattern_42_cells(width: int, height: int) -> Set[Tuple[int, int]]:
    """Return expected 42-pattern cells when maze dimensions allow it."""
    if width < 15 or height < 7:
        return set()

    pattern = [
        (0, 0), (0, 1), (0, 2), (1, 2),
        (2, 0), (2, 1), (2, 2), (2, 3), (2, 4),
        (4, 0), (5, 0), (6, 0), (6, 1),
        (6, 2), (5, 2), (4, 2), (4, 3), (4, 4), (5, 4), (6, 4),
    ]
    offset_x = (width // 2) - 3
    offset_y = (height // 2) - 2

    cells: Set[Tuple[int, int]] = set()
    for dx, dy in pattern:
        x = offset_x + dx
        y = offset_y + dy
        if 0 <= x < width and 0 <= y < height:
            cells.add((x, y))
    return cells


def validate_wall_consistency(grid: List[List[int]]) -> None:
    """Validate that shared walls are symmetric between neighboring cells."""
    height = len(grid)
    width = len(grid[0])

    for y in range(height):
        for x in range(width):
            cell = grid[y][x]
            for direction, (dx, dy, bit, opposite_bit) in DIRECTIONS.items():
                nx, ny = x + dx, y + dy
                if not (0 <= nx < width and 0 <= ny < height):
                    continue

                current_open = bool(cell & bit)
                neighbor_open = bool(grid[ny][nx] & opposite_bit)
                if current_open != neighbor_open:
                    msg = (
                        f"Wall inconsistency between ({x},{y})[{direction}] "
                        f"and ({nx},{ny})."
                    )
                    raise ValueError(msg)


def validate_no_3x3_open_area(grid: List[List[int]]) -> None:
    """Reject any 3x3 block fully open internally."""
    height = len(grid)
    width = len(grid[0])

    if width < 3 or height < 3:
        return

    for y in range(height - 2):
        for x in range(width - 2):
            all_internal_open = True

            for yy in range(y, y + 3):
                for xx in range(x, x + 2):
                    if not (grid[yy][xx] & 2 and grid[yy][xx + 1] & 8):
                        all_internal_open = False
                        break
                if not all_internal_open:
                    break

            if all_internal_open:
                for yy in range(y, y + 2):
                    for xx in range(x, x + 3):
                        if not (grid[yy][xx] & 4 and grid[yy + 1][xx] & 1):
                            all_internal_open = False
                            break
                    if not all_internal_open:
                        break

            if all_internal_open:
                raise ValueError(f"3x3 open area detected at ({x},{y}).")


def count_edges_and_reachable(
    grid: List[List[int]],
    entry: Tuple[int, int],
    walkable: Set[Tuple[int, int]],
) -> Tuple[int, Set[Tuple[int, int]]]:
    """Return graph edge count and BFS-reachable nodes from entry."""
    edges = 0

    for x, y in walkable:
        cell = grid[y][x]
        if x + 1 < len(grid[0]) and (x + 1, y) in walkable:
            if cell & 2:
                edges += 1
        if y + 1 < len(grid) and (x, y + 1) in walkable:
            if cell & 4:
                edges += 1

    visited: Set[Tuple[int, int]] = set()
    queue: deque[Tuple[int, int]] = deque([entry])

    while queue:
        cx, cy = queue.popleft()
        if (cx, cy) in visited:
            continue
        visited.add((cx, cy))

        for dx, dy, bit, _ in DIRECTIONS.values():
            if not (grid[cy][cx] & bit):
                continue
            nx, ny = cx + dx, cy + dy
            if (nx, ny) in walkable and (nx, ny) not in visited:
                queue.append((nx, ny))

    return edges, visited


def validate_maze_structure(
    grid: List[List[int]],
    entry: Tuple[int, int],
    exit_coords: Tuple[int, int],
    perfect: bool,
) -> None:
    """Validate maze structure, connectivity, and perfect-maze property."""
    height = len(grid)
    width = len(grid[0])
    pattern_cells = build_pattern_42_cells(width, height)

    validate_wall_consistency(grid)
    validate_no_3x3_open_area(grid)

    walkable: Set[Tuple[int, int]] = set()
    for y in range(height):
        for x in range(width):
            if grid[y][x] == 0:
                if (x, y) not in pattern_cells:
                    raise ValueError(
                        f"Fully closed cell outside 42 pattern at ({x},{y})."
                    )
                continue
            walkable.add((x, y))

    if entry not in walkable:
        raise ValueError("ENTRY is in a blocked cell.")
    if exit_coords not in walkable:
        raise ValueError("EXIT is in a blocked cell.")

    edge_count, reachable = count_edges_and_reachable(grid, entry, walkable)
    if reachable != walkable:
        raise ValueError("Invalid maze: unreachable connected cells exist.")

    if perfect and edge_count != len(walkable) - 1:
        msg = "PERFECT=True requires tree structure."
        msg += " (unique path between cells)."
        raise ValueError(msg)
