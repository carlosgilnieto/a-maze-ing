import time
# time.sleep(0.5)
import sys
from enum import Enum
from .generator import MazeGenerator

# \033[H -> Mueve el cursor de la terminal a 0,0(arriba de todo)
# \033[J -> Limpia todo lo que este por debajo del cursor
# \033[3J -> Borra el historial de desplazamiento
# \033[?25l -> Oculta el cursor en la terminal


class Color(Enum):
    WHITE = "\033[0m"
    BLUE = "\033[34m"
    CYAN = "\033[36m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"

    @staticmethod
    def get_pallete() -> list:
        return [c for c in Color]


class Draw(Enum):
    # +---+---+
    # | ■     |
    # +   +---+
    WALL_H= "---" # Wall for North & South
    EMPTY_H= "   " # No-Wall for North & South
    WALL_V= "|" # Wall for East & West
    EMPTY_V= " " # No-Wall for East & West
    CROSS = "+"
    POINT=" ● "
    BLOCK=" ■ "


def render_maze(maze: MazeGenerator, show_path: bool, color=Color.WHITE) -> str:
    """
    Devuelve el string para imprimir el resultado.
    Creo que si se quiere animar el recorrido, hay que cambiar el return a un print
    """
    # +---+---+ (Line Norte de 0,0)
    # | ■     | (Line Center de 0,0)
    # +---+---+ (Line Norte de 1,0)
    grid = maze.grid
    path = maze.path
    color = color.value
    clean_terminal() #Por el momento quita el aviso del patron 42
    display = ""
    for y in range(maze.height):
        line_north = color
        line_center = ""
        for x in range(maze.width):
            line_north += Draw.CROSS.value # Pinta las esquinas
            if grid[y][x] & 1: # Comprueba si esta abierto hacia el norte
                line_north += Draw.WALL_H.value
            else:
                line_north += Draw.EMPTY_H.value
            if grid[y][x] & 8: # Comprueba si esta abieto hacia el oeste
                line_center += (color + 
                                Draw.WALL_V.value + 
                                Color.WHITE.value)
            else:
                line_center += Draw.EMPTY_V.value
            if (x, y) == maze.entry:
                line_center += (Color.GREEN.value + 
                                Draw.BLOCK.value + 
                                Color.WHITE.value)
            elif (x, y) == maze.exit:
                line_center += (Color.RED.value + 
                                Draw.BLOCK.value + 
                                Color.WHITE.value)
            elif (x, y) in path and show_path: # Solo deberia de pintar el cuadrado si se quiere
                line_center += (Color.WHITE.value +
                                Draw.POINT.value)
            elif grid[y][x] == 15:
                line_center += (color + 
                                Draw.BLOCK.value +
                                Color.WHITE.value)
            else:
                line_center += Draw.EMPTY_H.value

        # Cierre del borde derecha
        line_north += Draw.CROSS.value # Añade el ultimo cross
        if grid[y][maze.width - 1] & 2:
            line_center += color + Draw.WALL_V.value + Color.WHITE.value
        # Junta todas las lines para pintar la celda
        display += line_north + "\n" + line_center + "\n"
    
    #Cierre de la pared de abajo
    line_final = color
    for x in range(maze.width):
        line_final += Draw.CROSS.value
        line_final += Draw.WALL_H.value
    line_final += Draw.CROSS.value
    display += line_final + Color.WHITE.value
    return display


def animated_path(maze: MazeGenerator, path: list, color=Color.WHITE, delay=0.1):
    for i in range(len(path) + 1):
        step_path = path[:i]
        maze.path = step_path
        print(render_maze(maze, True, color))
        time.sleep(delay)

def disable_cursor():
    print("\033[?25l")


def enable_cursor():
    print("\033[?25h")


def clean_terminal() -> str:
    sys.stdout.write("\033[2J\033[3J\033[H\033[?25l")

