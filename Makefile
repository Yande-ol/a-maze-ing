PYTHON = venv/bin/python
PIP = venv/bin/pip
FLAKE8 = venv/bin/flake8
MYPY = venv/bin/mypy

# Escopo do projeto (evita varrer venv)
SRC = a_maze_ing.py mazegen visualizer

all: install

install:
	python3 -m venv venv
	$(PIP) install --upgrade pip
	$(PIP) install flake8 mypy
	$(PIP) install ./mlx-2.2-py3-none-any.whl

run:
	$(PYTHON) a_maze_ing.py config.txt

debug:
	$(PYTHON) -m pdb a_maze_ing.py config.txt

viz:
	PYTHONPATH=. $(PYTHON) visualizer/graphical.py maze.txt

vix: viz

clean:
	rm -rf venv __pycache__ .mypy_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -f maze.txt

lint:
	$(FLAKE8) . --exclude venv
	$(MYPY) . --exclude 'venv/' --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	$(FLAKE8) . --exclude venv
	$(MYPY) . --exclude 'venv/' --strict

.PHONY: all install run debug viz vix clean lint lint-strict