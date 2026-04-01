from typing import List, Tuple


def to_hex(grid: List[List[int]]) -> List[str]:
    """converte a grid de inteiros para uma lista de strings hexadecimais."""
    hex_grid = []
    for row in grid:
        # converte cada número para hex (0-f)
        hex_row = "".join([f"{cell:x}" for cell in row])
        hex_grid.append(hex_row)
    return hex_grid


def get_path_letters(path: List[Tuple[int, int]]) -> str:
    """
    Converte uma lista de coordenadas em direções cardinais (N, E, S, W).
    Requisito do Capítulo IV.5 do PDF.
    """
    if not path or len(path) < 2:
        return ""

    letters = ""
    for i in range(len(path) - 1):
        curr_x, curr_y = path[i]
        next_x, next_y = path[i + 1]

        # Lógica de movimento baseada na diferença de coordenadas
        if next_y < curr_y:
            letters += "N"
        elif next_y > curr_y:
            letters += "S"
        elif next_x > curr_x:
            letters += "E"
        elif next_x < curr_x:
            letters += "W"

    return letters
