PYTHON3 = python3
PIP = pip
MAIN = a_maze_ing.py
CONFIG_FILE = config.txt

FLAKE8 = $(PYTHON3) -m flake8 . 
FLAKE8_EXCLUDED = .venv,.mypy_cache
MYPY = mypy
MYPY_EXCLUDED = "(.venv|.mypy_cache)"
MYPY_FLAGS = --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

SRC     = a_maze_ing.py

CACHE 	= .mypy_cache \
		  dist/ \
		  build/ \
		  *.egg-info

all: install run

run:
	@$(PYTHON3) $(MAIN) $(CONFIG_FILE)

install: 
	@echo "\033[33mInstalling the necessary packages...\033[0m"
	@$(PIP) install -r requirements.txt
	
debug:
	@$(PYTHON3) -m pdb $(MAIN) $(CONFIG_FILE)

clean:
	@echo "\033[33mDeleting cache files\033[0m"
	@rm -rf $(CACHE)
	@find . -type d -name "__pycache__" | xargs rm -rf

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

package:
	@echo "\033[33mGenerating Mazegen package\033[0m"
	@$(PYTHON3) -m build -w >/dev/null 
	@cp dist/*.whl .

.PHONY: run install debug clean lint lint-strict package