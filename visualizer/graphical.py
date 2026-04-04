import os
from mlx import Mlx

# 1. Configuração de Dados (Lado do Membro A)
HEX_GRID = [
    "D3D153951795153", "BC383AC3E947ABA", "87AAAC3A9693AAA",
    "856EABAC696C6AA", "C539684556D152A", "B96AFAFBFFFABC6",
    "AA96FEF857FA83B", "AC6BFFFAFFFC6AA", "813853FAFD513C2",
    "EAC6D6FAFFFEA96", "9695555415552AB", "83AD513969556C2",
    "AC693EAABA95556", "A956A92AC6AD553", "C6D546EC5545556"
]
SOLUTION = (
    "ESESSWWSEESWSSENENNENNNWNEESSESSEEENENESENNNEESSSSS"
    "WNWWSSSENESSESWSSESWWWWSSEEEE"
)
TILE = 40

# Coordenadas do Padrão "42" ajustadas para o centro (Y + 1)
PATTERN_42 = [
    # Dígito 4
    (4, 5), (4, 6), (4, 7), (5, 7), (6, 5), (6, 6), (6, 7), (6, 8), (6, 9),
    # Dígito 2
    (8, 5), (9, 5), (10, 5), (10, 6), (10, 7), (9, 7),
    (8, 7), (8, 8), (8, 9), (9, 9), (10, 9)
]


class MazeApp:
    def __init__(self):
        # Inicializa a conexão com a MiniLibX
        self.m = Mlx()
        self.mlx_ptr = self.m.mlx_init()

        self.cols, self.rows = len(HEX_GRID[0]), len(HEX_GRID)
        self.maze_w = self.cols * TILE
        self.win_w, self.win_h = self.maze_w, self.rows * TILE

        # Variáveis de Estado
        self.show_path = False

    # --- VARIÁVEIS DO PATO AUTOMÁTICO ---
        self.pato_x = 0
        self.pato_y = 0
        self.pato_dir = 'S'
        self.pato_frame = 0
        self.duck_step = 0     # Qual letra da solução ele está lendo
        self.duck_timer = 0    # Controla a velocidade do pato

        # Helper para carregar PNG

        # Novo Helper para carregar XPM (À prova de falhas!)
        def load_xpm(filename):
            base_dir = os.path.dirname(__file__)
            full_path = os.path.join(base_dir, filename)

            # Mudamos para a função de carregar XPM
            result = self.m.mlx_xpm_file_to_image(self.mlx_ptr, full_path)

            if not result:
                print(f"⚠️ ERRO: Não achou a imagem {full_path}!")
                return None

            img_ptr, _width, _height = result
            return img_ptr

        # E no dicionário, mude para os novos arquivos .xpm:
        self.sprites = {
            'N': [load_xpm("duck_n_1.xpm"), load_xpm("duck_n_2.xpm")],
            'S': [load_xpm("duck_s_1.xpm"), load_xpm("duck_s_2.xpm")],
            'E': [load_xpm("duck_e_1.xpm"), load_xpm("duck_e_2.xpm")],
            'W': [load_xpm("duck_w_1.xpm"), load_xpm("duck_w_2.xpm")]
        }

        # Registra a função que vai fazer o pato andar sozinho (Loop
        # Hook)[cite: 4]
        self.m.mlx_loop_hook(self.mlx_ptr, self.animate_duck, None)

        self.palette = [
            0xFF000000,  # 0. Preto (Padrão)
            0xFFFFFFFF,  # 1. Branco (A Pegadinha!)
            0xFF39FF14,  # 2. Verde Neon
            0xFF00FFFF,  # 3. Ciano Neon
            0xFFFF00FF,  # 4. Rosa Neon
            0xFFFAED27,  # 5. Amarelo Neon
            0xFFFF5F1F,  # 6. Laranja Neon
            0xFF9D00FF,  # 7. Roxo Neon
            0xFFFF0000,  # 8. Vermelho Sangue
            0xFF34495E  # 9. Azul Escuro
        ]

        # Índices de controle
        self.idx_wall = 0
        self.idx_bg = 1
        self.idx_42 = 9

        # AS SUAS VARIÁVEIS ORIGINAIS (agora puxam a cor da paleta!)
        self.wall_color = self.palette[0]
        self.bg_color = self.palette[self.idx_bg]
        self.pattern_color = self.palette[self.idx_42]
        # Criação da Janela e Buffer de Imagem
        self.win_ptr = self.m.mlx_new_window(
            self.mlx_ptr, self.win_w, self.win_h, "A-Maze-Ing 42 - Porto")
        self.img_ptr = self.m.mlx_new_image(
            self.mlx_ptr, self.win_w, self.win_h)

        # Acesso direto à memória para performance (Yoga)
        self.data, self.bpp, self.sl, self.fmt = self.m.mlx_get_data_addr(
            self.img_ptr)

        # Configuração de Hooks (Eventos)
        self.m.mlx_hook(self.win_ptr, 33, 0, self.clean_exit, None)
        self.m.mlx_key_hook(self.win_ptr, self.handle_key, None)
        self.m.mlx_expose_hook(self.win_ptr, self.render_all, None)

        print("\n" + "=" * 35)
        print("🎮 BEM-VINDO AO A-MAZE-ING 42 🎮")
        print("=" * 35)
        print("[ESC]   Sair do Jogo")
        print("[SPACE] Mostrar/Esconder Solucao")
        print("[ C ]   Mudar Cor das Paredes")
        print("[ B ]   Mudar Cor do Fundo")
        print("[ P ]   Mudar Cor do Padrao 42")
        print("=" * 35 + "\n")

    def clean_exit(self, *args):
        """Fecha a janela e limpa processos."""
        self.m.mlx_destroy_window(self.mlx_ptr, self.win_ptr)
        self.m.mlx_loop_exit(self.mlx_ptr)
        return 0

    def handle_key(self, key, *_args):
        if key == 65307:  # ESC
            self.clean_exit()
        elif key == 32:  # SPACE
            self.show_path = not self.show_path
            # Devolve o pato pro início quando
            # a solução for ligada/desligada
            self.pato_x = 0
            self.pato_y = 0
            self.duck_step = 0
            self.pato_dir = 'S'
            self.pato_frame = 0
        elif key == 99:  # 'C'
            self.idx_wall = (self.idx_wall + 1) % len(self.palette)
        elif key == 98:  # 'B'
            self.idx_bg = (self.idx_bg + 1) % len(self.palette)
        elif key == 112:  # 'P'
            self.idx_42 = (self.idx_42 + 1) % len(self.palette)

        self.render_all()

    def put_pixel(self, x, y, color):
        """Escreve um pixel no buffer de memória."""
        if 0 <= x < self.win_w and 0 <= y < self.win_h:
            offset = (y * self.sl) + (x * (self.bpp // 8))
            self.data[offset:offset + 4] = color.to_bytes(4, 'little')

    def draw_rect(self, x, y, w, h, color):
        """Desenha um retângulo preenchido."""
        for i in range(h):
            for j in range(w):
                self.put_pixel(x + j, y + i, color)

    def draw_path(self):
        """Desenha o caminho da solução com matemática limpa e par."""
        cx, cy = 0, 0
        thick = 14  # Espessura par cravada
        path_color = 0xFF3498DB  # Azul

        for step in SOLUTION:
            old_px, old_py = cx * TILE + (TILE // 2), cy * TILE + (TILE // 2)
            if step == 'E':
                cx += 1
            elif step == 'W':
                cx -= 1
            elif step == 'S':
                cy += 1
            elif step == 'N':
                cy -= 1
            new_px, new_py = cx * TILE + (TILE // 2), cy * TILE + (TILE // 2)

            x_s = min(old_px, new_px) - (thick // 2)
            y_s = min(old_py, new_py) - (thick // 2)
            w = abs(old_px - new_px) + thick
            h = abs(old_py - new_py) + thick
            self.draw_rect(x_s, y_s, w, h, path_color)

    def render_all(self, *_args):
        """Renderiza o estado no buffer usando espaco negativo."""
        wall_color = self.palette[self.idx_wall]
        bg_color = self.palette[self.idx_bg]
        pattern_color = self.palette[self.idx_42]

        # 1. O TRUQUE: Preenche o fundo TODO com a cor da PAREDE
        self.draw_rect(0, 0, self.win_w, self.win_h, wall_color)

        t = 1  # Espessura da parede
        miolo_size = TILE - 2 * t  # Tamanho do quadrado de chão

        for y, row in enumerate(HEX_GRID):
            for x, char in enumerate(row):
                px, py = x * TILE, y * TILE

                # Se for parte do padrão "42", desenha bloco sólido por cima de
                # tudo
                if (x, y) in PATTERN_42:
                    self.draw_rect(px, py, TILE, TILE, pattern_color)
                    continue

                # Define a cor do chão (Branco normal, Verde pra entrada,
                # Vermelho pra saída)
                floor_color = bg_color
                if (x, y) == (0, 0):
                    floor_color = 0xFF2ECC71
                elif (x, y) == (14, 14):
                    floor_color = 0xFFE74C3C

                # 2. Desenha o "Miolo" (o centro do azulejo onde o pato pisa)
                self.draw_rect(
                    px + t,
                    py + t,
                    miolo_size,
                    miolo_size,
                    floor_color)

                # 3. Abre as "Portas" para os lados onde NÃO há parede
                val = int(char, 16)
                # Se nao tem parede Norte, estica o chao pra cima.
                if not (val & 1):
                    self.draw_rect(px + t, py, miolo_size, t, floor_color)
                # Se nao tem parede Leste, estica o chao pra direita.
                if not (val & 2):
                    self.draw_rect(
                        px + TILE - t, py + t, t, miolo_size, floor_color)
                # Se nao tem parede Sul, estica o chao pra baixo.
                if not (val & 4):
                    self.draw_rect(
                        px + t, py + TILE - t, miolo_size, t, floor_color)
                # Se nao tem parede Oeste, estica o chao pra esquerda.
                if not (val & 8):
                    self.draw_rect(px, py + t, t, miolo_size, floor_color)

        # Desenha caminho azul se ativado
        if self.show_path:
            self.draw_path()

        # Empurra para a tela
        self.m.mlx_put_image_to_window(
            self.mlx_ptr, self.win_ptr, self.img_ptr, 0, 0)

        # Desenha o pato
        if self.show_path:
            img_pato_atual = self.sprites[self.pato_dir][self.pato_frame]
            if img_pato_atual:
                px_pato = (self.pato_x * TILE) + 5
                py_pato = (self.pato_y * TILE) + 5
                self.m.mlx_put_image_to_window(
                    self.mlx_ptr,
                    self.win_ptr,
                    img_pato_atual,
                    px_pato,
                    py_pato,
                )

    def animate_duck(self, *_args):
        # O pato só anda se a solução estiver ativada
        if not self.show_path:
            return

        # Controle de Velocidade (Aumente o 1000 se o pato estiver muito
        # rápido, ou diminua se estiver devagar)
        self.duck_timer += 1
        if self.duck_timer < 5:
            return
        self.duck_timer = 0  # Reseta o timer para o próximo passo

        # Se ainda não chegou no fim do labirinto
        if self.duck_step < len(SOLUTION):
            # Descobre para onde tem que ir lendo a string SOLUTION
            step_dir = SOLUTION[self.duck_step]
            self.pato_dir = step_dir

            # Atualiza as coordenadas
            if step_dir == 'E':
                self.pato_x += 1
            elif step_dir == 'W':
                self.pato_x -= 1
            elif step_dir == 'S':
                self.pato_y += 1
            elif step_dir == 'N':
                self.pato_y -= 1

            # Bate a perninha
            self.pato_frame = 1 - self.pato_frame

            # Vai para a proxima letra da solucao
            # na proxima vez que a funcao rodar.
            # rodar
            self.duck_step += 1

            # Atualiza a tela para mostrar o pato no novo lugar
            self.render_all()

    def run(self):
        self.render_all()
        self.m.mlx_loop(self.mlx_ptr)


if __name__ == "__main__":
    MazeApp().run()
