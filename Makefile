PYTHON3 = python3
PIP = pip
MAIN = a_maze_ing.py
CONFIG_FILE = config.txt

FLAKE8 = flake8 . 
FLAKE8_EXCLUDED = .venv,.mypy_cache
MYPY = mypy
MYPY_EXCLUDED = "(.venv|.mypy_cache)"
MYPY_FLAGS = --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

SRC     = a_maze_ing.py

CACHE 	= mazegen/__pycache__ \
		  .mypy_cache 

run:
	@$(PYTHON3) $(MAIN) $(CONFIG_FILE)

install: 
	@echo "\nInstalando paquetes..."
	@$(PIP) install -r requirements.txt

build:
	@echo "\033[33mGenerating Mazegen package\033[0m"
	@$(PYTHON3) -m build -w >/dev/null 
	@cp dist/*.whl .
	@rm -r dist/ build/ *.egg-info
	
debug:
	@$(PYTHON3) -m pdb $(MAIN) $(CONFIG_FILE)

clean:
	@rm -rf $(CACHE)

lint:
	@echo "Testing Flake8..."
	-@$(FLAKE8) . --exclude=$(FLAKE8_EXCLUDED)
	@echo "Testing mypy..."
	-@$(MYPY) . $(MYPY_FLAGS) --exclude $(MYPY_EXCLUDED)

lint-strict:
	@echo "Testing Flake8..."
	-@$(FLAKE8) . --exclude=$(FLAKE8_EXCLUDED)
	@echo "Testing mypy..."
	-@$(MYPY) . --strict --exclude $(MYPY_EXCLUDED)

.PHONY: run install lint debug clean lint lint-strict