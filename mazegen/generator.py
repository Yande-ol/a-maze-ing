import random
from typing import List, Tuple, Dict


class MazeGenerator:
    """
    Clase para gerar labirintos perfeitos usando o algoritmo DFS.

    Atributos:
        width (int): Largura do labirinto.
        height (int): Altura do labirinto.
        grid (List[List[int]]): Matriz representando as paredes das células.
    """

    def __init__(self, width: int, height: int) -> None:
        """
        Inicializa o MazeGenerator com as dimensões dadas.

        Args:
            width (int): Largura do labirinto.
            height (int): Altura do labirinto.
        """
        self.width: int = width
        self.height: int = height
        self.grid: List[List[int]] = [
            [0 for _ in range(width)] for _ in range(height)
        ]

        # N=1, E=2, S=4, W=8 (Conforme Capítulo IV.5 do PDF)
        self.directions: Dict[str, Tuple[int, int, int]] = {
            'N': (0, -1, 1),
            'E': (1, 0, 2),
            'S': (0, 1, 4),
            'W': (-1, 0, 8)
        }

        self.opposite: Dict[str, str] = {
            'N': 'S', 'E': 'W', 'S': 'N', 'W': 'E'
        }

    def is_valid(self, x: int, y: int) -> bool:
        """
        Verifica se as coordenadas estão dentro dos limites do labirinto.

        Args:
            x (int): Coordenada X.
            y (int): Coordenada Y.

        Returns:
            bool: True se for válido, False caso contrário.
        """
        return 0 <= x < self.width and 0 <= y < self.height

    def _apply_42_pattern(self, visited: List[List[bool]]) -> None:
        """"
        Desenha o padrão '42' usando células totalmente fechadas (0).
        """

        if self.width < 15 or self.height < 7:
            print("Error: Maze too small to draw '42' parttern.")
            return

        pattern = [
            # Desenho do numeor 4
            (0, 0), (0, 1), (0, 2), (1, 2),
            (2, 0), (2, 1), (2, 2), (2, 3), (2, 4),
            # Desenho do numero 2
            (4, 0), (5, 0), (6, 0), (6, 1),
            (6, 2), (5, 2), (4, 2), (4, 3), (4, 4), (5, 4), (6, 4)
        ]
        # Centralizar o desenho no labirinto.
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
        Encontra vizinhos que ainda não foram visitados.

        Args:
            x (int): Coordenada X atual.
            y (int): Coordenada Y atual.
            visited (List[List[bool]]): Matriz de células visitadas.

        Returns:
            List[Tuple[int, int, str, int]]: Lista de vizinhos disponíveis.
        """
        neighbors: List[Tuple[int, int, str, int]] = []
        for direction, (dx, dy, bit) in self.directions.items():
            nx, ny = x + dx, y + dy
            if self.is_valid(nx, ny) and not visited[ny][nx]:
                neighbors.append((nx, ny, direction, bit))
        return neighbors

    def generate(self, start_x: int = 0, start_y: int = 0) -> List[List[int]]:
        """
        Gera o labirinto usando o algoritmo de Recursive Backtracker.

        Args:
            start_x (int): X inicial.
            start_y (int): Y inicial.

        Returns:
            List[List[int]]: A matriz do labirinto gerada.
        """
        visited: List[List[bool]] = [
            [False for _ in range(self.width)]
            for _ in range(self.height)
        ]

        stack: List[Tuple[int, int]] = [(start_x, start_y)]
        visited[start_y][start_x] = True

        while stack:
            current_x, current_y = stack[-1]

            neighbors = self.get_unvisited_neighbors(
                current_x, current_y, visited
            )

            if neighbors:
                next_x, next_y, direction, bit = random.choice(neighbors)

                # Abre a parede na célula atual
                self.grid[current_y][current_x] |= bit

                # Abre a parede correspondente na célula vizinha
                opp_direction = self.opposite[direction]
                opp_bit = self.directions[opp_direction][2]
                self.grid[next_y][next_x] |= opp_bit

                visited[next_y][next_x] = True
                stack.append((next_x, next_y))
            else:
                stack.pop()

        return self.grid
