import os
import sys
import random

from mlx import Mlx  # type: ignore

from mazegen.generator import MazeGenerator
from mazegen.solver import solve
from mazegen.utils import parse_config, save_maze, get_path_letters
from mazegen.validator import validate_maze_structure

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# --- HELPER FUNCTIONS ---


def build_pattern_42(cols, rows):
    """Create coordinates for '42' pattern centered on the map."""
    pattern = [
        # Digit 4
        (0, 0), (0, 1), (0, 2), (1, 2),
        (2, 0), (2, 1), (2, 2), (2, 3), (2, 4),
        # Digit 2
        (4, 0), (5, 0), (6, 0), (6, 1),
        (6, 2), (5, 2), (4, 2), (4, 3), (4, 4), (5, 4), (6, 4),
    ]
    # Mathematical centering
    offset_x = (cols // 2) - 3
    offset_y = (rows // 2) - 2
    coords = []
    for dx, dy in pattern:
        nx, ny = offset_x + dx, offset_y + dy
        if 0 <= nx < cols and 0 <= ny < rows:
            coords.append((nx, ny))
    return coords


# --- MAIN CLASS ---


class MazeApp:
    def __init__(self, maze_file):
        self.maze_file = maze_file
        self.project_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..")
        )
        self.config_file = os.path.join(self.project_root, "config.txt")
        self.margin = 30
        self.animating_generation = False
        self.generation_generator = None
        self.generation_output_file = ""
        self.generation_entry = (0, 0)
        self.generation_exit = (0, 0)
        self.generation_perfect = True
        self.generation_algorithm = "dfs"
        self.generation_timer = 0
        # Speed of Prim animation (adjust here):
        # lower interval + more steps per cycle = faster.
        self.generation_interval = 0.0
        self.generation_steps_per_tick = 15

        # 1. MiniLibX connection
        self.m = Mlx()
        self.mlx_ptr = self.m.mlx_init()

        # 2. Read file (Parser)
        self.parse_file(maze_file)

        # 3. Window settings
        self.tile = 40
        self.maze_w = self.cols * self.tile + (self.margin * 2)
        self.maze_h = self.rows * self.tile + (self.margin * 2)
        self.win_ptr = self.m.mlx_new_window(
            self.mlx_ptr, self.maze_w, self.maze_h, "A-Maze-Ing 42 - Porto"
        )
        self.img_ptr = self.m.mlx_new_image(
            self.mlx_ptr, self.maze_w, self.maze_h
        )
        self.data, self.bpp, self.sl, self.fmt = (
            self.m.mlx_get_data_addr(self.img_ptr)
        )

        # 4. Initial state
        self.show_path = False
        self.pato_x, self.pato_y = self.start_pos
        self.pato_dir = 'S'
        self.pato_frame = 0
        self.duck_step = 0
        self.duck_timer = 0
        self.pattern_coords = build_pattern_42(self.cols, self.rows)

        # 5. Neon color palette
        self.palette = [
            0xFF000000, 0xFFFFFFFF, 0xFF39FF14, 0xFF00FFFF,
            0xFFFF00FF, 0xFFFAED27, 0xFFFF5F1F, 0xFF9D00FF,
            0xFFFF0000, 0xFF34495E
        ]
        self.idx_wall, self.idx_bg, self.idx_42 = 0, 1, 9

        # 6. Load XPM sprites
        self.sprites = self.load_all_sprites()

        # 7. Hooks (Events)
        self.m.mlx_hook(self.win_ptr, 33, 0, self.clean_exit, None)
        self.m.mlx_key_hook(self.win_ptr, self.handle_key, None)
        self.m.mlx_expose_hook(self.win_ptr, self.render_all, None)
        self.m.mlx_loop_hook(self.mlx_ptr, self.on_loop, None)

        self.print_menu()

    def load_config(self):
        """Load base configuration used to generate new mazes."""
        config = parse_config(self.config_file)
        required_keys = [
            "WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"
        ]
        for key in required_keys:
            if key not in config:
                msg = f"Required config key missing: {key}"
                raise ValueError(msg)
        return config

    def is_prim_selected(self):
        """Return True when config selects Prim as generation algorithm."""
        config = self.load_config()
        algo = config.get("ALGORITHM", "dfs").strip().lower()
        return algo == "prim"

    def generate_new_maze_file(self):
        """Generate new maze, overwrite configured file and return path."""
        config = self.load_config()
        width = int(config["WIDTH"])
        height = int(config["HEIGHT"])
        entry = tuple(map(int, config["ENTRY"].split(",")))
        exit_coords = tuple(map(int, config["EXIT"].split(",")))
        perfect = config["PERFECT"].strip().lower() == "true"
        algorithm = config.get("ALGORITHM", "dfs").strip().lower()

        if algorithm not in {"dfs", "prim"}:
            raise ValueError("ALGORITHM must be 'dfs' or 'prim'.")

        seed = random.SystemRandom().randint(1, 2**32 - 1)
        random.seed(seed)

        generator = MazeGenerator(width, height)
        grid = generator.generate(algorithm)
        validate_maze_structure(grid, entry, exit_coords, perfect)

        path = solve(grid, entry, exit_coords)
        path_letters = get_path_letters(path)

        output_file = os.path.join(
            self.project_root, config["OUTPUT_FILE"]
        )
        save_maze(output_file, grid, entry, exit_coords, path_letters)
        return output_file

    def reload_maze(self):
        """Generate new maze in configured file and reload visual state."""
        self.maze_file = self.generate_new_maze_file()
        self.parse_file(self.maze_file)
        self.show_path = False
        self.pato_x, self.pato_y = self.start_pos
        self.pato_dir = 'S'
        self.pato_frame = 0
        self.duck_step = 0
        self.duck_timer = 0
        self.pattern_coords = build_pattern_42(self.cols, self.rows)
        self.render_all()
        self.print_menu()

    def start_generation_animation(self):
        """Start animated Prim generation using current configuration file."""
        config = self.load_config()
        width = int(config["WIDTH"])
        height = int(config["HEIGHT"])
        entry = tuple(map(int, config["ENTRY"].split(",")))
        exit_coords = tuple(map(int, config["EXIT"].split(",")))
        perfect = config["PERFECT"].strip().lower() == "true"
        algorithm = config.get("ALGORITHM", "dfs").strip().lower()

        if algorithm != "prim":
            self.reload_maze()
            return

        self.generation_algorithm = algorithm
        output_file = config["OUTPUT_FILE"]
        self.generation_output_file = os.path.join(
            self.project_root, output_file
        )
        self.generation_entry = entry
        self.generation_exit = exit_coords
        self.generation_perfect = perfect

        self.generation_generator = MazeGenerator(width, height)
        self.generation_generator.start_prim_animation()

        self.animating_generation = True
        self.generation_timer = 0
        self.show_path = False
        self.pato_x, self.pato_y = entry
        self.pato_dir = 'S'
        self.pato_frame = 0
        self.duck_step = 0
        self.duck_timer = 0
        self.rows = height
        self.cols = width
        self.start_pos = entry
        self.end_pos = exit_coords
        self.pattern_coords = build_pattern_42(self.cols, self.rows)
        self.grid = self.generation_generator.grid
        self.render_all()
        self.print_menu()

    def animate_generation(self):
        """Advance one step of animated Prim generation."""
        if not self.animating_generation or self.generation_generator is None:
            return

        self.generation_timer += 1
        if self.generation_timer < self.generation_interval:
            return
        self.generation_timer = 0

        self.grid = self.generation_generator.grid
        finished = False
        for _ in range(self.generation_steps_per_tick):
            carved = self.generation_generator.prim_step()
            if carved is None:
                finished = True
                break

        if not finished:
            self.render_all()
            return

        path = solve(self.grid, self.generation_entry, self.generation_exit)
        path_letters = get_path_letters(path)
        save_maze(
            self.generation_output_file,
            self.grid,
            self.generation_entry,
            self.generation_exit,
            path_letters,
        )
        self.animating_generation = False
        self.generation_generator = None
        self.maze_file = self.generation_output_file
        self.parse_file(self.maze_file)
        self.show_path = False
        self.pattern_coords = build_pattern_42(self.cols, self.rows)
        self.render_all()
        self.print_menu()

    def on_loop(self, *args):
        """Main MLX loop for generation animation and path animation."""
        if self.animating_generation:
            self.animate_generation()
            return

        self.animate_duck()

    def parse_file(self, filename):
        """Read maze.txt file and extract Grid, Start/End and Solution."""
        try:
            with open(filename, 'r') as f:
                lines = [
                    line.strip() for line in f.readlines() if line.strip()
                ]
        except FileNotFoundError:
            print(f"❌ Error: File '{filename}' not found.")
            sys.exit(1)

        self.grid = []
        coords = []
        self.solution = ""

        for line in lines:
            if ',' in line:
                coords.append(tuple(map(int, line.split(','))))
            elif all(c in "SWEN" for c in line) and len(line) > 2:
                self.solution = line
            else:
                self.grid.append(line)

        self.rows = len(self.grid)
        self.cols = len(self.grid[0])
        self.start_pos = coords[0] if coords else (0, 0)
        self.end_pos = (
            coords[1] if len(coords) > 1 else (self.cols - 1, self.rows - 1)
        )

    def load_all_sprites(self):
        """Load duck XPMs."""
        def load_xpm(name):
            base_path = os.path.join(os.path.dirname(__file__), name)
            res = self.m.mlx_xpm_file_to_image(self.mlx_ptr, base_path)
            return res[0] if res else None

        return {
            'N': [load_xpm("duck_n_1.xpm"), load_xpm("duck_n_2.xpm")],
            'S': [load_xpm("duck_s_1.xpm"), load_xpm("duck_s_2.xpm")],
            'E': [load_xpm("duck_e_1.xpm"), load_xpm("duck_e_2.xpm")],
            'W': [load_xpm("duck_w_1.xpm"), load_xpm("duck_w_2.xpm")]
        }

    # --- DRAWING AND RENDERING ---

    def put_pixel(self, x, y, color):
        if 0 <= x < self.maze_w and 0 <= y < self.maze_h:
            offset = (y * self.sl) + (x * (self.bpp // 8))
            self.data[offset:offset+4] = color.to_bytes(4, 'little')

    def draw_rect(self, x, y, w, h, color):
        for i in range(h):
            for j in range(w):
                self.put_pixel(x + j, y + i, color)

    def render_all(self, *args):
        """Draw maze using bitwise logic from requirements."""
        w_color = self.palette[self.idx_wall]
        b_color = self.palette[self.idx_bg]
        p_color = self.palette[self.idx_42]

        self.draw_rect(0, 0, self.maze_w, self.maze_h, w_color)
        t = 1
        miolo = 40 - 2 * t

        for y, row in enumerate(self.grid):
            for x, char in enumerate(row):
                px = self.margin + (x * self.tile)
                py = self.margin + (y * self.tile)
                if (x, y) in self.pattern_coords:
                    self.draw_rect(px, py, self.tile, self.tile, p_color)
                    continue

                open_bits = self._cell_open_bits(char)
                f_color = b_color
                if (x, y) == self.start_pos:
                    f_color = 0xFF2ECC71
                elif (x, y) == self.end_pos:
                    f_color = 0xFFE74C3C
                elif (
                    self.animating_generation
                    and isinstance(char, int)
                    and open_bits == 0
                ):
                    f_color = w_color

                self.draw_rect(px + t, py + t, miolo, miolo, f_color)

                # Bit 0:N, 1:E, 2:S, 3:W (0=Open, 1=Closed)
                val = open_bits
                if val & 1:
                    self.draw_rect(px + t, py, miolo, t, f_color)
                if val & 2:
                    x_off = self.tile - t
                    self.draw_rect(px + x_off, py + t, t, miolo, f_color)
                if val & 4:
                    y_off = self.tile - t
                    self.draw_rect(px + t, py + y_off, miolo, t, f_color)
                if val & 8:
                    self.draw_rect(px, py + t, t, miolo, f_color)

        if self.show_path:
            self.draw_path()
        self.m.mlx_put_image_to_window(
            self.mlx_ptr, self.win_ptr, self.img_ptr, 0, 0
        )
        self.draw_duck()

    def draw_path(self):
        cx, cy = self.start_pos
        thick = 14
        path_color = 0xFF3498DB
        for step in self.solution:
            old_px = self.margin + (cx * self.tile) + 20
            old_py = self.margin + (cy * self.tile) + 20
            if step == 'E':
                cx += 1
            elif step == 'W':
                cx -= 1
            elif step == 'S':
                cy += 1
            elif step == 'N':
                cy -= 1
            new_px = self.margin + (cx * self.tile) + 20
            new_py = self.margin + (cy * self.tile) + 20
            x_s = min(old_px, new_px) - 7
            y_s = min(old_py, new_py) - 7
            w = abs(old_px - new_px) + thick
            h = abs(old_py - new_py) + thick
            self.draw_rect(x_s, y_s, w, h, path_color)

    def draw_duck(self):
        if self.show_path:
            img = self.sprites[self.pato_dir][self.pato_frame]
            if img:
                self.m.mlx_put_image_to_window(
                    self.mlx_ptr,
                    self.win_ptr,
                    img,
                    self.margin + (self.pato_x * self.tile) + 5,
                    self.margin + (self.pato_y * self.tile) + 5,
                )

    def _cell_open_bits(self, cell):
        """Convert cell (internal int or file hex) to open bits."""
        if isinstance(cell, int):
            return cell
        return int(cell, 16) ^ 0xF

    # --- LOGIC AND EVENTS ---

    def animate_duck(self, *args):
        if not self.show_path:
            return
        self.duck_timer += 1
        if self.duck_timer < 6:
            return
        self.duck_timer = 0

        if self.duck_step < len(self.solution):
            step_dir = self.solution[self.duck_step]
            self.pato_dir = step_dir
            if step_dir == 'E':
                self.pato_x += 1
            elif step_dir == 'W':
                self.pato_x -= 1
            elif step_dir == 'S':
                self.pato_y += 1
            elif step_dir == 'N':
                self.pato_y -= 1
            self.pato_frame = 1 - self.pato_frame
            self.duck_step += 1
            self.render_all()

    def handle_key(self, key, *args):
        if key == 65307:
            self.clean_exit()
        elif key == 32:
            self.show_path = not self.show_path
            self.pato_x, self.pato_y = self.start_pos
            self.duck_step = 0
        elif key == 114:
            cfg = self.load_config()
            is_prim = cfg.get("ALGORITHM", "dfs").strip().lower() == "prim"
            if self.generation_algorithm == "prim" or is_prim:
                self.start_generation_animation()
            else:
                self.reload_maze()
        elif key == 99:
            self.idx_wall = (self.idx_wall + 1) % len(self.palette)
        elif key == 98:
            self.idx_bg = (self.idx_bg + 1) % len(self.palette)
        elif key == 112:
            self.idx_42 = (self.idx_42 + 1) % len(self.palette)
        self.render_all()

    def clean_exit(self, *args):
        self.m.mlx_destroy_window(self.mlx_ptr, self.win_ptr)
        os._exit(0)

    import os

    import os

    def print_menu(self):
        os.system("clear")
        width = 44 
        
    
        header_border = "╔" + "═" * (width - 2) + "╗"
        footer_border = "╚" + "═" * (width - 2) + "╝"
        divider = "╟" + "─" * (width - 2) + "╢"

        title = " A-MAZE-ING 42"
        print(f"\n{header_border}")
        print(f"║{title.center(width - 3)} ║") 
        print(f"{divider}")

        options = [
            "[ESC]   Exit",
            "[SPACE] Solution",
            "[R]     New maze",
            "[C]     Walls",
            "[B]     Background",
            "[P]     color 42"
        ]

        max_opt_len = max(len(opt) for opt in options)
        
        padding = (width - 2 - max_opt_len) // 2

        print("║" + " " * (width - 2) + "║")
        for opt in options:
            content = opt.ljust(max_opt_len)
            left_spaces = " " * padding
            right_spaces = " " * (width - 2 - padding - max_opt_len)
            print(f"║{left_spaces}{content}{right_spaces}║")

        print("║" + " " * (width - 2) + "║")
        print(f"{footer_border}\n")

    def run(self):
        if self.is_prim_selected():
            self.start_generation_animation()
        else:
            self.render_all()
        self.m.mlx_loop(self.mlx_ptr)


# --- EXECUTION ---

if __name__ == "__main__":
    target_file = sys.argv[1] if len(sys.argv) > 1 else "maze.txt"
    MazeApp(target_file).run()
