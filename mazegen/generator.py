import random
from typing import List, Tuple, Dict, Optional


class MazeGenerator:
    """
    Class to generate perfect mazes using DFS or Prim.

    Attributes:
        width (int): Width of the maze.
        height (int): Height of the maze.
        grid (List[List[int]]): Matrix representing the walls of cells.
    """

    def __init__(self, width: int, height: int) -> None:
        """
        Initialize the MazeGenerator with the given dimensions.

        Args:
            width (int): Width of the maze.
            height (int): Height of the maze.
        """
        self.width: int = width
        self.height: int = height
        self.grid: List[List[int]] = [
            [0 for _ in range(width)] for _ in range(height)
        ]

        # N=1, E=2, S=4, W=8 (Per Chapter IV.5 of PDF)
        self.directions: Dict[str, Tuple[int, int, int]] = {
            'N': (0, -1, 1),
            'E': (1, 0, 2),
            'S': (0, 1, 4),
            'W': (-1, 0, 8)
        }

        self.opposite: Dict[str, str] = {
            'N': 'S', 'E': 'W', 'S': 'N', 'W': 'E'
        }
        self._prim_visited: List[List[bool]] = []
        self._prim_frontier: List[Tuple[int, int, int, int, int]] = []
        self._prim_active: bool = False

    def _reset_grid(self) -> List[List[bool]]:
        """Reset internal maze grid and return a fresh visited matrix."""
        self.grid = [
            [0 for _ in range(self.width)] for _ in range(self.height)
        ]
        return [
            [False for _ in range(self.width)] for _ in range(self.height)
        ]

    def _find_start_cell(
        self,
        visited: List[List[bool]],
        start_x: int = 0,
        start_y: int = 0,
    ) -> Tuple[int, int]:
        """Pick a valid start cell, skipping blocked 42 cells when needed."""
        if self.is_valid(start_x, start_y) and not visited[start_y][start_x]:
            return start_x, start_y

        candidates = [
            (x, y)
            for y in range(self.height)
            for x in range(self.width)
            if not visited[y][x]
        ]
        if not candidates:
            raise ValueError("Maze size does not allow generation.")
        return random.choice(candidates)

    def _opposite_bit(self, bit: int) -> int:
        """Return the opposite wall bit for the given direction bit."""
        opposites: Dict[int, int] = {1: 4, 2: 8, 4: 1, 8: 2}
        return opposites[bit]

    def _carve_passage(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        bit: int,
    ) -> None:
        """Open the wall between two adjacent cells."""
        self.grid[y1][x1] |= bit
        self.grid[y2][x2] |= self._opposite_bit(bit)

    def _add_prim_frontier(
        self,
        x: int,
        y: int,
        frontier: List[Tuple[int, int, int, int, int]],
        visited: List[List[bool]],
    ) -> None:
        """Add frontier walls for Prim generation."""
        for _, (dx, dy, bit) in self.directions.items():
            nx, ny = x + dx, y + dy
            if self.is_valid(nx, ny) and not visited[ny][nx]:
                frontier.append((x, y, nx, ny, bit))

    def _prepare_prim_state(
        self,
        start_x: int = 0,
        start_y: int = 0,
    ) -> Tuple[int, int]:
        """Prepare internal state for a step-by-step Prim generation."""
        visited = self._reset_grid()
        self._apply_42_pattern(visited)

        start_x, start_y = self._find_start_cell(visited, start_x, start_y)
        visited[start_y][start_x] = True

        self._prim_visited = visited
        self._prim_frontier = []
        self._prim_active = True
        self._add_prim_frontier(start_x, start_y, self._prim_frontier, visited)
        return start_x, start_y

    def is_valid(self, x: int, y: int) -> bool:
        """
        Check if coordinates are within maze bounds.

        Args:
            x (int): X coordinate.
            y (int): Y coordinate.

        Returns:
            bool: True if valid, False otherwise.
        """
        return 0 <= x < self.width and 0 <= y < self.height

    def _apply_42_pattern(self, visited: List[List[bool]]) -> None:
        """
        Draw the '42' pattern using fully closed cells (0).
        """

        if self.width < 15 or self.height < 7:
            print("Error: Maze too small to draw '42' pattern.")
            return

        pattern = [
            # Drawing of digit 4
            (0, 0), (0, 1), (0, 2), (1, 2),
            (2, 0), (2, 1), (2, 2), (2, 3), (2, 4),
            # Drawing of digit 2
            (4, 0), (5, 0), (6, 0), (6, 1),
            (6, 2), (5, 2), (4, 2), (4, 3), (4, 4), (5, 4), (6, 4)
        ]
        # Center the drawing in the maze.
        offset_x = (self.width // 2) - 3
        offset_y = (self.height // 2) - 2

        for dx, dy in pattern:
            nx, ny = offset_x + dx, offset_y + dy
            if self.is_valid(nx, ny):
                visited[ny][nx] = True
                self.grid[ny][nx] = 0

    def get_unvisited_neighbors(
        self, x: int, y: int, visited: List[List[bool]]
    ) -> List[Tuple[int, int, str, int]]:
        """
        Find neighbors that have not been visited yet.

        Args:
            x (int): Current X coordinate.
            y (int): Current Y coordinate.
            visited (List[List[bool]]): Matrix of visited cells.

        Returns:
            List[Tuple[int, int, str, int]]: List of available neighbors.
        """
        neighbors: List[Tuple[int, int, str, int]] = []
        for direction, (dx, dy, bit) in self.directions.items():
            nx, ny = x + dx, y + dy
            if self.is_valid(nx, ny) and not visited[ny][nx]:
                neighbors.append((nx, ny, direction, bit))
        return neighbors

    def _generate_dfs(
        self,
        start_x: int = 0,
        start_y: int = 0,
    ) -> List[List[int]]:
        """
        Generate maze using Recursive Backtracker algorithm.

        Args:
            start_x (int): Starting X.
            start_y (int): Starting Y.

        Returns:
            List[List[int]]: The generated maze matrix.
        """
        visited = self._reset_grid()

        # 3. APPLY 42 PATTERN (Mandatory Chapter IV.4)
        self._apply_42_pattern(visited)

        # 4. Safety check: if start falls on '42', move to (0,0)
        # If (0,0) is also part of 42, the code will find the next free cell.
        start_x, start_y = self._find_start_cell(visited, start_x, start_y)

        stack: List[Tuple[int, int]] = [(start_x, start_y)]
        visited[start_y][start_x] = True

        # 5. Generation algorithm (DFS)
        while stack:
            current_x, current_y = stack[-1]

            neighbors = self.get_unvisited_neighbors(
                current_x, current_y, visited
            )

            if neighbors:
                next_x, next_y, direction, bit = random.choice(neighbors)

                # Open the wall in the current cell
                self._carve_passage(current_x, current_y, next_x, next_y, bit)

                visited[next_y][next_x] = True
                stack.append((next_x, next_y))
            else:
                stack.pop()

        return self.grid

    def _generate_prim(
        self,
        start_x: int = 0,
        start_y: int = 0,
    ) -> List[List[int]]:
        """Generate maze using randomized Prim's algorithm."""
        self._prepare_prim_state(start_x, start_y)

        while self.prim_step():
            pass

        return self.grid

    def start_prim_animation(
        self,
        start_x: int = 0,
        start_y: int = 0,
    ) -> List[List[int]]:
        """Prepare Prim generation so it can be advanced one step at a time."""
        self._prepare_prim_state(start_x, start_y)
        return self.grid

    def prim_step(self) -> Optional[Tuple[int, int]]:
        """Advance Prim generation by one carved passage and return cell."""
        if not self._prim_active:
            return None

        while self._prim_frontier:
            index = random.randrange(len(self._prim_frontier))
            x1, y1, x2, y2, bit = self._prim_frontier.pop(index)

            if self._prim_visited[y2][x2]:
                continue

            self._carve_passage(x1, y1, x2, y2, bit)
            self._prim_visited[y2][x2] = True
            self._add_prim_frontier(
                x2, y2, self._prim_frontier, self._prim_visited
            )
            if not self._prim_frontier:
                self._prim_active = False
            return (x2, y2)

        self._prim_active = False
        return None

    def generate(
        self,
        algorithm: str = "dfs",
        start_x: int = 0,
        start_y: int = 0,
    ) -> List[List[int]]:
        """Generate maze using the selected algorithm."""
        algorithm = algorithm.strip().lower()

        if algorithm == "prim":
            return self._generate_prim(start_x, start_y)
        if algorithm == "dfs":
            return self._generate_dfs(start_x, start_y)

        msg = f"Unknown maze generation algorithm: {algorithm}"
        raise ValueError(msg)
