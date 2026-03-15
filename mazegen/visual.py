"""
Module for visual representation and animations on the terminal.

This module contains the enumerations for colours and drawing characters.
It provides the functions needed to draw the maze, render
the animations for generation (DFS) and traversal (BFS), and control the
terminal modes to enable a live interactive menu.
"""
import time
import sys
import termios
from typing import Optional
from enum import Enum
from .generator import MazeGenerator


class Color(Enum):
    """
    List of ANSI escape sequences for terminal colours:
    This enumeration defines a set of colours that can be used to enhance
    the visual representation of the maze in the terminal. Each colour is
    represented by its corresponding ANSI escape code, which allows for
    colored text output in the terminal.

    The Color class also includes a method to retrieve a palette of valid
    colours for rendering the maze, excluding those that are not suitable
    for visibility (e.g., black) or that are reserved for specific elements
    (e.g., green for entry, red for exit).

    Attributes:
        BLACK: Black (ANSI code 30).
        RED: Red (ANSI code 31).
        GREEN: Green (ANSI code 32).
        YELLOW: Yellow colour (ANSI code 33).
        BLUE: Blue colour (ANSI code 34).
        PURPLE: Purple colour (ANSI code 35).
        CYAN: Cyan colour (ANSI code 36).
        RESET: Reset colour (ANSI code 0).
    """
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    PURPLE = "\033[35m"
    CYAN = "\033[36m"
    RESET = "\033[0m"

    @staticmethod
    def get_pallete() -> list:
        """
        Generates a list of valid colours to use as the main colour
        of the maze.

        Returns:
            List[Color]: A filtered list excluding system or reserved colours.
        """
        invalid_colors = [Color.RESET, Color.BLACK,
                          Color.GREEN, Color.RED]
        return [c
                for c in Color
                if c not in invalid_colors]


class Draw(Enum):
    """
    List of characters used to draw the grid.

    Base cell pattern:
    +---+---+
    | ■     |
    +   +---+

    Attributes:
        WALL_H: String representing a horizontal wall.
        EMPTY_H: String representing an empty horizontal space (no wall).
        WALL_V: String representing a vertical wall.
        EMPTY_V: String representing an empty vertical space (no wall).
        CROSS: String representing the intersection of walls (corners).
        BLOCK: String representing a filled cell (used for entry, exit, path).

    """

    WALL_H = "---"
    EMPTY_H = "   "
    WALL_V = "|"
    EMPTY_V = " "
    CROSS = "+"
    BLOCK = " ■ "


def render_maze(maze: MazeGenerator, show_path: bool = False,
                color: Color = Color.BLACK,
                terminal: bool = False,
                stack: Optional[list] = None,
                path: Optional[tuple] = None) -> str:
    """
    Generates the complete string of the rendered maze, including characters
    and colours.

    Iterates over the height of the grid, building row by row.

    Args:
        maze (MazeGenerator): The main maze object.
        show_path (bool): Determines whether the solution path is drawn.
        color (Color): ANSI colour applied to the maze walls.
        terminal (bool): If True, prints the result directly.
        stack (Optional[list]): Current stack of nodes (used in DFS animation).
        path (Optional[tuple]): Current state of the path (used in
            BFS animation).

    Returns:
        str: Final text string representing the drawn maze.
    """

    display = []
    clean_terminal()
    for y in range(maze.height):
        display.append(_render_row(maze, y, show_path, color, stack, path))

    line_final = ((paint(Draw.CROSS, color) +
                   paint(Draw.WALL_H, color)) * maze.width)
    line_final += paint(Draw.CROSS, color)
    display.append(line_final)

    output = "".join(display)
    if terminal:
        print(output)
    return output


def _render_row(maze: MazeGenerator,
                y: int,
                show_path: bool,
                color: Color,
                stack: Optional[list] = None,
                path: Optional[tuple] = None) -> str:
    """
    Renders a specific row of the grid by evaluating the bitmaps.

    Generates two lines per iteration: the top line (north walls)
    and the centre line (west walls and cell contents).
        For example, for the cell at position (0, 0):

     +---+---+ (North line of 0,0)
     | ■     | (Center line of 0,0)
     +---+---+ (North line of 1,0)
    """
    line_north = ""
    line_center = ""
    grid = maze.get_grid()

    for x in range(maze.width):
        line_north += paint(Draw.CROSS, color)

        if grid[y][x] & 1:
            line_north += paint(Draw.WALL_H, color)
        else:
            line_north += Draw.EMPTY_H.value

        if grid[y][x] & 8:
            line_center += paint(Draw.WALL_V, color)
        else:
            line_center += paint(Draw.EMPTY_V, color)

        line_center += _get_cell_content(maze, x, y, show_path,
                                         color, stack, path)

    line_north += paint(Draw.CROSS, color)
    if grid[y][maze.width - 1] & 2:
        line_center += paint(Draw.WALL_V, color)

    return f"{line_north}\n{line_center}\n"


def _get_cell_content(maze: MazeGenerator, x: int, y: int,
                      show_path: bool,
                      color: Color,
                      stack: Optional[list] = None,
                      path: Optional[tuple] = None) -> str:
    """
    When the cursor hovers over a cell in the grid, it returns the
    cell's contents for printing, which can be a wall, an empty space,
    or a path.

    Args:
        maze (MazeGenerator):
            The main maze object.
        x (int):
            The x-coordinate of the cell being evaluated.
        y (int):
            The y-coordinate of the cell being evaluated.
        show_path (bool):
            Determines whether the solution path is drawn.
        color (Color):
            ANSI colour applied to the maze walls.
        stack (Optional[list]):
            Current stack of nodes (used in DFS animation).
        path (Optional[tuple]):
            Current state of the path (used in BFS animation).

    Returns:
        str: The string representing the content of the cell, which can be
        a wall, an empty space, or a path, with the appropriate colour applied.

    """
    grid = maze.get_grid()
    if stack:
        if (x, y) == stack[-1]:
            return paint(Draw.BLOCK, Color.YELLOW)
        elif (x, y) in stack:
            return paint(Draw.BLOCK, Color.PURPLE)
    if path:
        came_from, current_cell = path
        if (x, y) == current_cell:
            return paint(Draw.BLOCK, Color.YELLOW)
        elif (x, y) in came_from:
            return paint(Draw.BLOCK, Color.CYAN)

    if (x, y) == maze.entry:
        return paint(Draw.BLOCK, Color.GREEN)
    if (x, y) == maze.exit:
        return paint(Draw.BLOCK, Color.RED)
    if grid[y][x] == 15:
        return paint(Draw.BLOCK, (color))
    if show_path and maze.get_path() and (x, y) in maze.get_path():
        return paint(Draw.BLOCK, Color.RESET)
    return paint(Draw.EMPTY_H, Color.RESET)


def render_generation(maze: MazeGenerator,
                      wall_color: Color = Color.BLACK) -> None:
    """
    Monitor the visual generation process (DFS) frame by frame.
    The function manages terminal modes to create a smooth animation effect,
    disabling user input and hiding the cursor during the animation, and
    ensuring that the final state of the maze is displayed at the end of the
    generation process.

    Args:
        maze (MazeGenerator): The maze instance being generated.
        wall_color (Color): The colour used to draw the maze walls during
        the animation.
    Returns:
        None: This function does not return a value; it directly renders the
        maze on the terminal.
    """
    try:
        maze.reset_maze()
    except Exception:
        sys.exit()

    if maze.is_perfect:
        generator = maze.perfect_algo()
    else:
        generator = maze.non_perfect_algo()

    toggle_terminal(False)
    disable_cursor()
    try:
        current_stack = None
        for _, current_stack in generator:
            if maze.speed_animation > 0:
                output = render_maze(maze, color=wall_color,
                                     stack=current_stack)
                print(output)
                time.sleep(maze.speed_animation)
            else:
                pass

        # Asegura la impresión del estado final al terminar la generación
        print(render_maze(maze, color=wall_color, stack=current_stack))
        flush_input()
        enable_cursor()
    finally:
        toggle_terminal(True)


def render_solve(maze: MazeGenerator,
                 color: Color = Color.BLACK) -> None:
    """
    Monitor the visual search process (solving the maze) frame by frame.

    Args:
        maze (MazeGenerator): The maze instance being solved.
        color (Color): The colour used to highlight the path during
        the animation.
    Returns:
        None: This function does not return a value; it directly renders the
        maze on the terminal.

    """
    generator = maze.solve_algo()
    toggle_terminal(False)
    disable_cursor()
    try:
        for anim_path in generator:
            output = render_maze(maze, color=color, path=anim_path)
            print(output)
            time.sleep(maze.speed_animation)
        flush_input()
    finally:
        toggle_terminal(True)
        enable_cursor()


def render_path(maze: MazeGenerator,
                animated_path: bool = False,
                wall_color: Color = Color.BLACK) -> None:
    """
    Plots the final path from the start to the finish.
        If `animated_path` is False, the entire path is drawn at once. If True,
    the path is drawn progressively, showing each step in sequence with a delay
    defined by `maze.speed_animation`.

    Returns:
            None: This function does not return a value; it directly renders
            the path on the terminal.
    """
    toggle_terminal(False)
    disable_cursor()
    final_path = maze.get_path()
    try:
        if animated_path:
            for i in range(len(final_path) + 1):
                maze.set_path(final_path[:i])
                print(render_maze(maze, show_path=True, color=wall_color))
                time.sleep(maze.speed_animation)
    finally:
        toggle_terminal(True)
        enable_cursor()
        print(render_maze(maze, show_path=True, color=wall_color))


def toggle_terminal(enable: bool) -> None:
    """
    Enables or disables the terminal's built-in functions.

    - ECHO: Disables the display of text entered via the keyboard.
    - ICANON: Disables line buffering (direct input without pressing “Enter”).

    This function is used to create a more interactive experience during the
    maze generation and solving animations, allowing for real-time updates
    without waiting for user input.

    Args:
        enable (bool): If True, restores normal terminal behavior; if False,
            disables ECHO and ICANON for interactive animations.
    """

    fd = sys.stdin.fileno()
    settings = termios.tcgetattr(fd)

    if enable:
        settings[3] = settings[3] | termios.ECHO | termios.ICANON
    else:
        settings[3] = settings[3] & ~termios.ECHO & ~termios.ICANON
    termios.tcsetattr(fd, termios.TCSADRAIN, settings)


def flush_input() -> None:
    """
    Clears the input buffer to prevent any pending keystrokes from affecting
    the program after animations or terminal mode changes.This is particularly
    useful to ensure that any keys pressed during the animation do not
    interfere with the interactive menu that follows.

    This function uses termios.tcflush to clear the input buffer of the
    terminal, ensuring that the program starts with a clean slate for user
    input after animations or mode toggling.
    """
    termios.tcflush(sys.stdin, termios.TCIFLUSH)


def paint(form: Draw,
          color: Color = Color.RESET) -> str:
    """
    Returns a string in the format used to “draw” the shape and colour.
    """
    return f"{color.value}{form.value}{Color.RESET.value}"


def disable_cursor() -> None:
    """
    Hide the cursor in the terminal.
    """
    sys.stdout.write("\033[?25l")


def enable_cursor() -> None:
    """
    The blinking cursor reappears in the terminal.
    """
    sys.stdout.write("\033[?25h")


def clean_terminal() -> None:
    """
    Clear the terminal and move the cursor to the starting position (0,0).
    """
    # \033[?25l
    sys.stdout.write("\033[2J\033[3J\033[H")
