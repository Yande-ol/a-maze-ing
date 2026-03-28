import random


class MazeGenerator:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.grid = [[0 for _ in range(width)] for _ in range(height)]

        self.directions = {
            'N': (0, -1, 1),
            'L': (1, 0, 2),
            'S': (0, 1, 4),
            'O': (-1, 0, 8)
        }

        self.opposite = {'N': 'S', 'L': 'O', 'S': 'N', 'O': 'L'}

    def is_valid(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

    def get_unvisited_neighbors(self, x, y, visited):
        neighbors = []
        for direction, (dx, dy, bit) in self.directions.items():
            nx, ny = x + dx, y + dy
            if self.is_valid(nx, ny) and not visited[ny][nx]:
                neighbors.append((nx, ny, direction, bit))
        return neighbors

    def generate(self, start_x=0, start_y=0):
        visited = [[False for _ in range(self.width)]
                   for _ in range(self.height)]

        stack = [(start_x, start_y)]
        visited[start_y][start_x] = True

        while stack:
            current_x, current_y = stack[-1]

            neighbors = self.get_unvisited_neighbors
            (current_x, current_y, visited)

            if neighbors:
                next_x, next_y, direction, bit = random.choice(neighbors)

                self.grid[current_y][current_x] |= bit

                opp_direction = self.opposite[direction]
                opp_bit = self.directions[opp_direction][2]
                self.grid[next_y][next_x] |= opp_bit

                visited[next_y][next_x] = True
                stack.append((next_x, next_y))
            else:
                stack.pop()

        return self.grid
