import sys
from typing import List, Tuple


def to_hex(grid: List[List[int]]) -> List[str]:
    """Convert integer grid to list of hexadecimal strings."""
    hex_grid = []
    for row in grid:
        # Convert each number to hex (0-f)
        hex_row = "".join([f"{15 - cell:X}" for cell in row])
        hex_grid.append(hex_row)
    return hex_grid


def save_maze(
    filename: str,
    grid: List[List[int]],
    entry: Tuple[int, int],
    exit_coords: Tuple[int, int],
    path_letters: str
) -> None:
    """Save the maze in the format required by the subject."""
    try:
        with open(filename, 'w') as f:
            for row in to_hex(grid):
                f.write(f"{row}\n")

            f.write("\n")  # Mandatory empty line
            f.write(f"{entry[0]},{entry[1]}\n")
            f.write(f"{exit_coords[0]},{exit_coords[1]}\n")
            f.write(f"{path_letters}\n")
    except IOError as e:
        print(f"Error saving file: {e}")


def parse_config(filename: str) -> dict:
    """
    Read configuration file (KEY=VALUE).
    Ignore comments (#) and whitespace.
    """
    config = {}
    try:
        with open(filename, 'r') as f:
            for line in f:
                # Clear spaces and ignore comments
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                if '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()
        return config
    except FileNotFoundError:
        print(f"Error: Configuration file '{filename}' not found.")
        sys.exit(1)


def get_path_letters(path: List[Tuple[int, int]]) -> str:
    """
    Convert a list of coordinates into cardinal directions (N, E, S, W).
    Requirement of Chapter IV.5 of PDF.
    """
    if not path or len(path) < 2:
        return ""

    letters = ""
    for i in range(len(path) - 1):
        curr_x, curr_y = path[i]
        next_x, next_y = path[i + 1]

        # Movement logic based on coordinate difference
        if next_y < curr_y:
            letters += "N"
        elif next_y > curr_y:
            letters += "S"
        elif next_x > curr_x:
            letters += "E"
        elif next_x < curr_x:
            letters += "W"

    return letters
