# [NOTAS]
#	Importa el orden de los comandos, al hacer 'make' se ejecuta el primer 'comando'


#La carpeta que se genera con el entorno virtual
VENV 	= .venv
#Los comandos hay que ejecutarlos desde el entorno virtual por eso el $(VENV), para que coja la cartea del entorno virtual
PIP 	= $(VENV)/bin/pip
PYTHON 	= $(VEpythonNV)/bin/python3

FLAKE8 = flake8 --exclude=$(VENV)
MYPY = mypy
MYPY_FLAGS = --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

SRC     = a_maze_ing.py

CACHE 	= __pycache__ \
		  mazegen/__pycache__ \
		  .mypy_cache 

$(VENV): #	Crea el entorno virtual
	@echo "Creando entorno virtual..."
	@python3 -m venv .venv

# [Comandos]
install: $(VENV)
#	@echo "\nGenerando paquete mazegen..."
#	Esto va a futuro
	@echo "\nInstalando paquetes..."
	@$(PIP) install -r requirements.txt

run:
	@$(PYTHON) a_maze_ing.py config.txt

debug:

clean:
	@rm -r $(CACHE)

lint:
	@echo "Testing Flake8..."
	-@$(FLAKE8) .
	@echo "Testing mypy..."
	-@$(MYPY) $(SRC) $(MYPY_FLAGS)


lint-strict:
	