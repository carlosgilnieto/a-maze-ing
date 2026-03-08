import time
# time.sleep(0.5)
from enum import Enum
from .generator import MazeGenerator

# \033[H -> Mueve el cursor de la terminal a 0,0(arriba de todo)
# \033[J -> Limpia todo lo que este por debajo del cursor
# \033[3J -> Borra el historial de desplazamiento
# \033[?25l -> Oculta el cursor en la terminal

class Color(Enum):
    BLUE = "\033[34m"
    CYAN = "\033[36m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    RESET = "\033[0m"

class Draw(Enum):
    # +---+---+
    # | ■     |
    # +   +---+
    WALL_H= "---" # Wall for North & South
    EMPTY_H= "   " # No-Wall for North & South
    WALL_V= "|" # Wall for East & West
    EMPTY_V= " " # No-Wall for East & West
    CROSS = "+"
    POINT="■"


def render_maze(maze: MazeGenerator, color: Color) -> str:
# def render_maze(grid: list[list]) -> str:
    # +---+---+ (Line Norte de 0,0)
    # | ■     | (Line Center de 0,0)
    # +---+---+ (Line Norte de 1,0)
    grid = maze.grid
    color = color.value
    clean_terminal()
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
                line_center += color + Draw.WALL_V.value + Color.RESET.value
            else:
                line_center += Draw.EMPTY_V.value
            if x == maze.entry[0] and y == maze.entry[1]:
                line_center += Color.GREEN.value + f" {Draw.POINT.value} " + Color.RESET.value
            elif x == maze.exit[0] and y == maze.exit[1]:
                line_center += Color.RED.value + f" {Draw.POINT.value} " + Color.RESET.value
            else:
                line_center += Draw.EMPTY_H.value
        # Cierre del borde derecha
        line_north += Draw.CROSS.value # Añade el ultimo cross
        if grid[y][maze.width - 1] & 2:
            line_center += color + Draw.WALL_V.value + Color.RESET.value
        else:
            line_center += Draw.EMPTY_V.value
        # Junta todas las lines para pintar la celda
        display += line_north + "\n" + line_center + "\n" 
    line_final = color
    for x in range(maze.width):
        line_final += Draw.CROSS.value
        if grid[y - 1][x] & 4: # Check si tiene pared al sur
            line_final += Draw.WALL_H.value
        else:
            line_final += Draw.EMPTY_H.value
    line_final += Draw.CROSS.value
    display += line_final + Color.RESET.value
    return display

def disable_cursor():
    print("\033[?25l")


def enable_cursor():
    print("\033[?25h")


def clean_terminal() -> str:
    print("\033[2J\033[3J\033[H\033\033[?25l")

