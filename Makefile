# Variáveis de Caminho
PYTHON = venv/bin/python
PIP = venv/bin/pip
MLX_WHEEL = mlx-2.2-py3-none-any.whl

# Cores para o terminal
GREEN = \033[0;32m
RESET = \033[0m

all: install

install:
	@echo "🔧 Criando ambiente virtual..."
	python3 -m venv venv
	@echo "📦 Instalando ferramentas e MiniLibX local..."
	$(PIP) install --upgrade pip
	$(PIP) install flake8 mypy
	# Esta linha instala o arquivo .whl que você tem na pasta
	$(PIP) install ./$(MLX_WHEEL)
	@echo "$(GREEN)✅ Pronto! Use 'make run' para gerar ou 'make viz' para ver.$(RESET)"

run:
	@echo "🚀 Gerando labirinto..."
	$(PYTHON) a_maze_ing.py config.txt

viz:
	@echo "🎨 Abrindo visualizador gráfico..."
	$(PYTHON) visualizer/graphical.py

lint:
	@echo "🔍 Verificando normas da 42 (Flake8 & Mypy)..."
	venv/bin/flake8 .
	venv/bin/mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

clean:
	@echo "🧹 Limpando ambiente..."
	rm -rf venv __pycache__ visualizer/__pycache__ .mypy_cache
	rm -f maze.txt

.PHONY: all install run viz lint clean