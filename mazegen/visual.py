import time
from enum import Enum
from typing import List, Any
# time.sleep(0.5)
import sys

# \033[H -> Mueve el cursor de la terminal a 0,0(arriba de todo)
# \033[J -> Limpia todo lo que este por debajo del cursor
# \033[3J -> Borra el historial de desplazamiento
# \033[?25l -> Oculta el cursor en la terminal

# +---+---+
# | ■     |
# +---+---+

class DRAW(Enum):
    # +---+---+
    # | ■     |
    # +---+---+
    WALL_H= "---" # Wall for North & South
    EMPTY_H= "   " # No-Wall for North & South
    WALL_V= "|" # Wall for East & West
    EMPTY_V= " " # No-Wall for East & West
    CROSS = "+"
    POINT="■"


def render_maze(grid: List[List[Any]]):


def disable_cursor():
    print("\033[?25l")


def enable_cursor():
    print("\033[?25h")


def clean_terminal():
    print("\033[2J\033[3J\033[H\033")

