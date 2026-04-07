*This project has been created as part of the 42 curriculum by febraga-, yande-ol.*

# A-Maze-ing

## Description
A-Maze-ing is a Python project that generates random mazes from a configuration file,
validates structural constraints, computes a shortest path from entry to exit, and
exports the result in the hexadecimal format required by the subject.

The project also includes a graphical visualizer (MiniLibX) with user interactions for:
- regenerating the maze,
- toggling path visibility,
- changing wall/background colors,
- changing the "42" pattern color.

## Features
- Maze generation with reusable `MazeGenerator` class
- Multiple generation algorithms (`dfs`, `prim`)
- Seed-based reproducibility (`SEED` in config)
- Structural validation (symmetry, connectivity, no isolated cells, 3x3 open-area check)
- Shortest-path export (`N`, `E`, `S`, `W`)
- Output encoding in hexadecimal wall format
- Optional MiniLibX visualization

## Repository Structure
```
.
├── a_maze_ing.py
├── config.txt
├── Makefile
├── maze.txt
├── pyproject.toml
├── setup.py
├── mazegen/
│   ├── __init__.py
│   ├── generator.py
│   ├── solver.py
│   ├── utils.py
│   └── validator.py
└── visualizer/
		└── graphical.py
```

## Instructions

### Requirements
- Python `3.10+`
- `venv` support
- MiniLibX wheel available in repo (`mlx-2.2-py3-none-any.whl`) for graphical mode

### Setup and Main Commands
```bash
make install
make run
make debug
make lint
make lint-strict
make clean
```

Main execution:
```bash
python3 a_maze_ing.py config.txt
```

Graphical viewer:
```bash
make viz
```

## Configuration File Format
The configuration file uses one `KEY=VALUE` pair per line.
Comments start with `#`.

### Mandatory keys
- `WIDTH=<int>`
- `HEIGHT=<int>`
- `ENTRY=<x,y>`
- `EXIT=<x,y>`
- `OUTPUT_FILE=<filename>`
- `PERFECT=<True|False>`

### Optional keys implemented
- `ALGORITHM=<dfs|prim>`
- `SEED=<int>`

`SEED` behavior:
- If `SEED` is omitted, generation is random.
- If `SEED=0`, generation is random (same behavior as omitted).
- If `SEED` is a non-zero integer (for example `SEED=42`), generation is reproducible.

### Example
```txt
# Maze Configuration
WIDTH=20
HEIGHT=20
ENTRY=0,0
EXIT=18,18
OUTPUT_FILE=maze.txt
PERFECT=True
ALGORITHM=prim
SEED=42
```

## Output File Format
The maze is written row-by-row as hexadecimal digits (one per cell).
Each bit represents a **closed** wall:
- Bit 0: North
- Bit 1: East
- Bit 2: South
- Bit 3: West

After an empty line, the file also includes:
1. Entry coordinates (`x,y`)
2. Exit coordinates (`x,y`)
3. Shortest valid path using `N`, `E`, `S`, `W`

## Maze Generation Algorithm
Current supported algorithms:
- `dfs` (Recursive Backtracker style)
- `prim` (Randomized Prim)

Why these choices:
- Both algorithms are classic and reliable for maze generation.
- `dfs` is simple and fast, producing long corridors.
- `prim` produces a more organic branching structure and supports animation naturally.
- Both fit well with the perfect-maze requirement when enabled.

## Reusable Module
Reusable code is in the `mazegen` package:
- `mazegen.generator.MazeGenerator`
- `mazegen.solver.solve`
- `mazegen.validator.validate_maze_structure`
- `mazegen.utils` helpers for config parsing and output writing

Basic example:
```python
from mazegen.generator import MazeGenerator
from mazegen.solver import solve

generator = MazeGenerator(width=20, height=20)
grid = generator.generate("prim")
path = solve(grid, (0, 0), (19, 19))
```

Packaging notes:
- Build metadata is provided in `pyproject.toml` and `setup.py`.
- The package is designed to be installable via standard Python packaging tools.

## Team & Project Management

### Team roles
- `febraga-`: core generation flow, validation integration, output handling
- `yande-ol`: architecture support, visual layer integration, quality checks

### Planned timeline vs. actual evolution
- Initial plan: implement parser + generator + output first, then visualization.
- Evolution: validation and structural checks became a larger effort than expected,
	and part of visualization work was done in parallel to keep feedback loops short.

### What worked well
- Modular split (`mazegen`) kept the code reusable.
- Separate validator logic improved confidence in generated mazes.
- Makefile improved consistency for install/run/lint workflows.

### What can be improved
- Increase automated tests coverage (unit + integration).
- Improve strict typing coverage in visualization module.
- Add CI pipeline for automatic lint/type checks on each push.

### Tools used
- Python `3.10+`
- `flake8`, `mypy`
- MiniLibX Python binding (`mlx` wheel)
- Git/GitHub workflow

## Resources
- Python docs: https://docs.python.org/3/
- `abc` module: https://docs.python.org/3/library/abc.html
- `typing` module: https://docs.python.org/3/library/typing.html
- Maze algorithms overview:
	https://en.wikipedia.org/wiki/Maze_generation_algorithm
- MiniLibX bindings used in project context (local wheel in repository)

### AI Usage Disclosure
AI tools were used as assistants for:
- brainstorming algorithm alternatives,
- checking wording and structure for documentation,
- reviewing edge cases and validation ideas.

All generated suggestions were manually reviewed, adapted, and tested before use.
