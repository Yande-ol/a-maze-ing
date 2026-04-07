import sys
import random
from typing import Dict, Any, Tuple

from mazegen.generator import MazeGenerator
from mazegen.solver import solve
from mazegen.utils import parse_config, save_maze, get_path_letters
from mazegen.validator import validate_maze_structure


def parse_coords(coords_str: str) -> Tuple[int, int]:
    try:
        parts = coords_str.split(",")
        if len(parts) != 2:
            raise ValueError
        return int(parts[0]), int(parts[1])
    except ValueError:
        msg = f"Invalid coordinate format: '{coords_str}'."
        raise ValueError(msg)


def validate_config(config: Dict[str, str]) -> Dict[str, Any]:
    """Validates required configuration keys and data types."""
    required_keys = ["WIDTH", "HEIGHT", "ENTRY", "EXIT",
                     "OUTPUT_FILE", "PERFECT"]
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Required config key missing: {key}")
    try:
        width = int(config["WIDTH"])
        height = int(config["HEIGHT"])
    except ValueError:
        raise ValueError("WIDTH and HEIGHT must be integers.")
    if width <= 0 or height <= 0:
        raise ValueError("Maze dimensions must be greater than zero.")

    # Validate Coordinates
    entry = parse_coords(config["ENTRY"])
    exit_coords = parse_coords(config["EXIT"])

    if entry == exit_coords:
        raise ValueError("ENTRY and EXIT cannot be in the same cell.")
    # Check bounds
    if not (0 <= entry[0] < width and 0 <= entry[1] < height):
        msg = f"ENTRY {entry} is out of bounds {width}x{height}."
        raise ValueError(msg)
    if not (0 <= exit_coords[0] < width and 0 <= exit_coords[1] < height):
        msg = f"EXIT {exit_coords} is out of bounds {width}x{height}."
        raise ValueError(msg)
    perfect_value = config["PERFECT"].strip().lower()
    if perfect_value not in {"true", "false"}:
        raise ValueError("PERFECT must be 'True' or 'False'.")

    algorithm = config.get("ALGORITHM", "dfs").strip().lower()
    if algorithm not in {"dfs", "prim"}:
        raise ValueError("ALGORITHM must be 'dfs' or 'prim'.")

    try:
        seed = int(config.get("SEED", 0))
    except ValueError as exc:
        raise ValueError("SEED must be an integer.") from exc

    return {
        "width": width,
        "height": height,
        "entry": entry,
        "exit": exit_coords,
        "output_file": config["OUTPUT_FILE"],
        "perfect": perfect_value == "true",
        "algorithm": algorithm,
        "seed": seed,
    }


def main() -> None:
    """Main function orchestrating maze generation."""
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py <config_file>")
        sys.exit(1)

    try:
        # Parse and Validation
        raw_config = parse_config(sys.argv[1])
        cfg = validate_config(raw_config)

        # Setup Random Seed
        if cfg["seed"] != 0:
            random.seed(cfg["seed"])

        # Generate Maze
        generator = MazeGenerator(cfg["width"], cfg["height"])
        maze_grid = generator.generate(cfg["algorithm"])

        # Validate maze structure before solving/saving
        validate_maze_structure(
            maze_grid,
            cfg["entry"],
            cfg["exit"],
            cfg["perfect"],
        )

        # Solve (Pathfinding)
        path = solve(maze_grid, cfg["entry"], cfg["exit"])
        if not path:
            msg = "⚠️  Warning: No path found between entry and exit."
            print(msg)
            path_letters = ""
        else:
            path_letters = get_path_letters(path)

        # Save Result
        save_maze(
            cfg["output_file"],
            maze_grid,
            cfg["entry"],
            cfg["exit"],
            path_letters
        )

        # Visual summary for user
        print("\n" + "═" * 40)
        print("🎯 MAZE GENERATED SUCCESSFULLY!")
        print("═" * 40)
        print(f"📂 File saved:  {cfg['output_file']}")
        print(f"📏 Size:        {cfg['width']}x{cfg['height']}")
        print(f"🚪 Entry:       {cfg['entry']}")
        print(f"🏁 Exit:        {cfg['exit']}")
        print(f"🛣️ Path length: {len(path)} steps")
        print("═" * 40 + "\n")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
