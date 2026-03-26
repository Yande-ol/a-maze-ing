import sys
import random
from mlx import Mlx

# 1. Configuração de Dados (Lado do Membro A)
HEX_GRID = [
    "D3D153951795153", "BC383AC3E947ABA", "87AAAC3A9693AAA",
    "856EABAC696C6AA", "C539684556D152A", "B96AFAFBFFFABC6",
    "AA96FEF857FA83B", "AC6BFFFAFFFC6AA", "813853FAFD513C2",
    "EAC6D6FAFFFEA96", "9695555415552AB", "83AD513969556C2",
    "AC693EAABA95556", "A956A92AC6AD553", "C6D546EC5545556"
]
SOLUTION = "ESESSWWSEESWSSENENNENNNWNEESSESSEEENENESENNNEESSSSSWNWWSSSENESSESWSSESWWWWSSEEEE"
TILE = 40
SIDEBAR_W = 250

# Coordenadas do Padrão "42" ajustadas para o centro (Y + 1)
PATTERN_42 = [
    # Dígito 4
    (4,5), (4,6), (4,7), (5,7), (6,5), (6,6), (6,7), (6,8), (6,9),
    # Dígito 2
    (8,5), (9,5), (10,5), (10,6), (10,7), (9,7), (8,7), (8,8), (8,9), (9,9), (10,9)
]

class MazeApp:
    def __init__(self):
        # Inicializa a conexão com a MiniLibX
        self.m = Mlx()
        self.mlx_ptr = self.m.mlx_init()
        
        self.cols, self.rows = len(HEX_GRID[0]), len(HEX_GRID)
        self.maze_w = self.cols * TILE
        self.win_w, self.win_h = self.maze_w + SIDEBAR_W, self.rows * TILE
        
        # Variáveis de Estado
        self.show_path = False
        self.wall_color = 0xFF000000  # Paredes começam Pretas
        self.bg_color = 0xFFFFFFFF    # Fundo começa Branco
        
        # Criação da Janela e Buffer de Imagem
        self.win_ptr = self.m.mlx_new_window(self.mlx_ptr, self.win_w, self.win_h, "A-Maze-Ing 42 - Porto")
        self.img_ptr = self.m.mlx_new_image(self.mlx_ptr, self.win_w, self.win_h)
        
        # Acesso direto à memória para performance (Yoga)
        self.data, self.bpp, self.sl, self.fmt = self.m.mlx_get_data_addr(self.img_ptr)

        # Configuração de Hooks (Eventos)
        self.m.mlx_hook(self.win_ptr, 33, 0, self.clean_exit, None)
        self.m.mlx_key_hook(self.win_ptr, self.handle_key, None)
        self.m.mlx_expose_hook(self.win_ptr, self.refresh, None)

    def clean_exit(self, *args):
        """Fecha a janela e limpa processos."""
        self.m.mlx_destroy_window(self.mlx_ptr, self.win_ptr)
        self.m.mlx_loop_exit(self.mlx_ptr)
        sys.exit(0)

    def handle_key(self, key, *args):
        """Controlos: ESC (Sair), SPACE (Solução), C (Cor Paredes), B (Cor Fundo)."""
        if key == 65307: # ESC
            self.clean_exit()
        elif key == 32: # SPACE
            self.show_path = not self.show_path
        elif key == 99: # 'C' - Change Wall Color
            self.wall_color = random.randint(0, 0xFFFFFF) | 0xFF000000
        elif key == 98: # 'B' - Change Background Color
            self.bg_color = random.randint(0, 0xFFFFFF) | 0xFF000000
        
        self.render_all()

    def put_pixel(self, x, y, color):
        """Escreve um pixel no buffer de memória."""
        if 0 <= x < self.win_w and 0 <= y < self.win_h:
            offset = (y * self.sl) + (x * (self.bpp // 8))
            self.data[offset:offset+4] = color.to_bytes(4, 'little')

    def draw_rect(self, x, y, w, h, color):
        """Desenha um retângulo preenchido."""
        for i in range(h):
            for j in range(w): 
                self.put_pixel(x + j, y + i, color)

    def draw_path(self):
        """Desenha o caminho da solução ligando os centros das células."""
        cx, cy = 0, 0
        thick = TILE // 3
        path_color = 0xFF3498DB # Azul
        
        for step in SOLUTION:
            old_px, old_py = cx * TILE + (TILE // 2), cy * TILE + (TILE // 2)
            if step == 'E': cx += 1
            elif step == 'W': cx -= 1
            elif step == 'S': cy += 1
            elif step == 'N': cy -= 1
            new_px, new_py = cx * TILE + (TILE // 2), cy * TILE + (TILE // 2)
            
            x_s = min(old_px, new_px) - (thick // 2)
            y_s = min(old_py, new_py) - (thick // 2)
            w = abs(old_px - new_px) + thick
            h = abs(old_py - new_py) + thick
            self.draw_rect(x_s, y_s, w, h, path_color)

    def render_all(self):
        """Renderiza todo o estado no buffer de imagem."""
        # Preenche o fundo com a cor dinâmica
        self.draw_rect(0, 0, self.maze_w, self.win_h, self.bg_color)
        
        for y, row in enumerate(HEX_GRID):
            for x, char in enumerate(row):
                px, py = x * TILE, y * TILE
                
                # Se for parte do padrão "42", desenha bloco sólido preto
                if (x, y) in PATTERN_42:
                    self.draw_rect(px, py, TILE, TILE, 0xFF000000)
                    continue 

                # Entrada / Saída
                if (x, y) == (0, 0): self.draw_rect(px, py, TILE, TILE, 0xFF2ECC71)
                elif (x, y) == (14, 14): self.draw_rect(px, py, TILE, TILE, 0xFFE74C3C)
                
                # Paredes (Decodificação Hexadecimal)
                val = int(char, 16)
                t = 3 # grossura
                if val & 1: self.draw_rect(px, py, TILE, t, self.wall_color) # N
                if val & 2: self.draw_rect(px+TILE-t, py, t, TILE, self.wall_color) # E
                if val & 4: self.draw_rect(px, py+TILE-t, TILE, t, self.wall_color) # S
                if val & 8: self.draw_rect(px, py, t, TILE, self.wall_color) # W

        # Desenha caminho se ativado
        if self.show_path: self.draw_path()
        
        # Desenha Sidebar
        self.draw_rect(self.maze_w, 0, SIDEBAR_W, self.win_h, 0xFF34495E)
        self.refresh()

    def refresh(self, *args):
        """Empurra a imagem para a janela e sobrepõe o texto."""
        self.m.mlx_put_image_to_window(self.mlx_ptr, self.win_ptr, self.img_ptr, 0, 0)
        xt = self.maze_w + 20
        self.m.mlx_string_put(self.mlx_ptr, self.win_ptr, xt, 50, 0xFFFFFFFF, "CONTROLES:")
        self.m.mlx_string_put(self.mlx_ptr, self.win_ptr, xt, 80, 0xFFFFFFFF, "ESC: Sair")
        self.m.mlx_string_put(self.mlx_ptr, self.win_ptr, xt, 110, 0xFFFFFFFF, "SPACE: Ver Solucao")
        self.m.mlx_string_put(self.mlx_ptr, self.win_ptr, xt, 140, 0xFFFFFFFF, "C: Cor Paredes")
        self.m.mlx_string_put(self.mlx_ptr, self.win_ptr, xt, 170, 0xFFFFFFFF, "B: Cor Fundo")

    def run(self):
        self.render_all()
        self.m.mlx_loop(self.mlx_ptr)

if __name__ == "__main__":
    MazeApp().run()