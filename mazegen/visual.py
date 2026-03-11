import time
import sys
import termios
import tty
from enum import Enum
from .generator import MazeGenerator

# \033[H -> Mueve el cursor de la terminal a 0,0(arriba de todo)
# \033[J -> Limpia todo lo que este por debajo del cursor
# \033[3J -> Borra el historial de desplazamiento
# \033[?25l -> Oculta el cursor en la terminal


class Color(Enum):
    BLACK = "\033[30m"
    GREEN = "\033[32m"
    CYAN = "\033[36m"
    BLUE = "\033[34m"
    PURPLE = "\033[35m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    RESET = "\033[0m"

    @staticmethod
    def get_pallete() -> list:
        return [c
                for c in Color
                if not c == Color.RESET]


class Draw(Enum):
    # +---+---+
    # | ■     |
    # +   +---+
    WALL_H= "---" # Wall for North & South
    EMPTY_H= "   " # No-Wall for North & South
    WALL_V= "|" # Wall for East & West
    EMPTY_V= " " # No-Wall for East & West
    CROSS = "+"
    BLOCK=" ■ "


def render_maze(maze: MazeGenerator, show_path=False, color=Color.BLACK) -> str:
    """
    Devuelve el string para imprimir el resultado.
    Creo que si se quiere animar el recorrido, hay que cambiar el return a un print
    """
    # +---+---+ (Line Norte de 0,0)
    # | ■     | (Line Center de 0,0)
    # +---+---+ (Line Norte de 1,0)

    color = color.value #Por el momento quita el aviso del patron 42
    display = []
    for y in range(maze.height):
        display.append(_render_row(maze, y, show_path, color))

    #Cierre de la pared de abajo
    line_final = (color +
                  (Draw.CROSS.value + Draw.WALL_H.value) * maze.width)
    line_final += Draw.CROSS.value + Color.RESET.value
    display.append(line_final)
    return "".join(display)


def _get_cell_content(maze: MazeGenerator, x: int, y: int,
                      show_path: bool, color: Color) -> str:
    """
    Al pasar la posicion en el grid de una celda devuelve el contenido de ella
    para imprimir
    """
    if (x, y) == maze.entry:
        return f"{Color.GREEN.value}{Draw.BLOCK.value}{Color.RESET.value}"
    if (x, y) == maze.exit:
        return f"{Color.RED.value}{Draw.BLOCK.value}{Color.RESET.value}"
    if show_path and (x, y) in maze.path:
        return f"{Color.RESET.value}{Draw.BLOCK.value}"
    return Draw.EMPTY_H.value
    if maze.grid[y][x] == 15:
        return f"{color}{Draw.BLOCK.value}{Color.RESET.value}"


def _render_row(maze: MazeGenerator, y: int,
                show_path: bool, color: Color) -> str:
    line_north = color
    line_center = ""

    for x in range(maze.width):
        line_north += Draw.CROSS.value  # Pinta las esquina
        if maze.grid[y][x] & 1: # Comprueba si esta abierto hacia el norte
            line_north += Draw.WALL_H.value
        else:
            line_north += Draw.EMPTY_H.value
        if maze.grid[y][x] & 8: # Comprueba si esta abieto hacia el oeste
            line_center += (color +
                            Draw.WALL_V.value +
                            Color.RESET.value)
        else:
            line_center += Draw.EMPTY_V.value
        line_center += _get_cell_content(maze, x, y, show_path, color)

    # Cierre del borde derecha
    line_north += Draw.CROSS.value # Añade el ultimo cross
    if maze.grid[y][maze.width - 1] & 2:
        line_center += color + Draw.WALL_V.value + Color.RESET.value
    return f"{line_north}\n{line_center}\n"

def animated_generator(maze: MazeGenerator, color=Color.BLACK) -> None:
    try:
        maze.reset_maze()
        maze.debug_print_state()
        if maze.is_perfect:
            generator = maze.perfect_maze(maze.directions)
        else:
            generator = maze.non_perfect_maze(maze.directions)
    except Exception:
        print("error")
        sys.exit()
    for current in generator:
        clean_terminal()
        print(render_maze(maze))
        time.sleep(0.1)

def animated_path(maze: MazeGenerator, path: list, color=Color.RESET, delay=0.1) -> None:
    """Animates the solution path of the maze in the terminal.

    Iteratively updates the maze's path and renders it to create a visual 
    animation. It temporarily disables terminal echo to prevent user input 
    from interfering with the display.

    Args:
        maze (MazeGenerator): The maze object instance to be rendered.
        path (list): A list of tuples [(x, y), ...] representing the coordinates 
            of the solution path.
        color (Color, optional): The color of the maze walls and path. 
            Defaults to Color.WHITE.
        delay (float, optional): Time in seconds to wait between each frame 
            of the animation. Defaults to 0.1.

    Raises:
        Any exception raised during rendering will be caught to ensure the 
        terminal settings are restored in the 'finally' block.
    """
    try:
        toggle_terminal(False)
        for i in range(len(path) + 1):
            step_path = path[:i]
            maze.path = step_path
            print(render_maze(maze, True, color))
            time.sleep(delay)
        flush_input()
    finally:
        toggle_terminal(True)


def toggle_terminal(enable: bool) -> None:
    # ~termios.ECHO -> Lo que se escribe con teclado por pantalla no se ve
    # ~termios.ICANON -> Desactiva que puedas enviar datos al pulsar enter
    # tcsadrain -> Los cambios en la terminal se aplican despues de imprimir todo
    fd = sys.stdin.fileno()
    settings = termios.tcgetattr(fd)
    # Se hace un toggle del bit que esta en fd[3]
    if enable:
        settings[3] = settings[3] | termios.ECHO | termios.ICANON
    else:
        settings[3] = settings[3] & ~termios.ECHO & ~termios.ICANON
    termios.tcsetattr(fd, termios.TCSADRAIN, settings)


def flush_input() -> None:
    # tcflush -> Vacia la espera de texto
    termios.tcflush(sys.stdin, termios.TCIFLUSH)


def disable_cursor():
    sys.stdout.write("\033[?25l")


def enable_cursor():
    sys.stdout.write("\033[?25h")


def clean_terminal() -> str:
    # \033[?25l
    sys.stdout.write("\033[2J\033[3J\033[H")
