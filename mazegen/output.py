from typing import List, Tuple, Dict, Any
from .generator import MazeGenerator


def int_to_hex(maze: List[List[int]]) -> List[str]:
    """
    Converts the decimal maze array into a list of hexadecimal strings.

    Iterates over each cell in the array and converts its integer
    value (bitmask) to its hexadecimal representation in uppercase,
    removing the “0x” prefix.

    Args:
        maze (List[List[int]]): Maze grid with decimal values.

    Returns:
        List[str]: List of strings, where each string represents a complete row
                   of the maze in hexadecimal format.
    """
    grid: List[str] = []
    for line in maze:
        row = ""
        for cell in line:
            row += str(hex(cell)[2:]).upper()
        grid.append(row)
    return grid


def hex_to_str(maze: List[str]) -> str:
    """
    Converts a list of hexadecimal strings into a single multi-line string.

    Args:
        maze_hex (List[str]): A list of rows in hexadecimal format.

    Returns:
        str: A complete representation of the maze, ready to be written
             to a file, with line breaks at the end of each row.
    """
    output: str = ""
    for line in maze:
        row = ""
        for cell in line:
            row += cell
        output += row + "\n"
    return output


def dir_to_path(path: List[Tuple[int, int]]) -> str:
    """
    Converts a list of coordinates into a sequence of cardinal directions.

    Compares each coordinate on the route with the next one to determine
    the direction of movement (North, South, East, West).

    Args:
        path (List[Tuple[int, int]]): List of route coordinates (x, y).

    Returns:
        str: String containing the directions (e.g. “NNESWW”).
            Returns an empty string if the route
            does not have at least 2 steps.
    """
    route: List[str] = []
    moves = {(0, -1): "N",
             (1, 0): "E",
             (0, 1): "S",
             (-1, 0): "W"}

    if not path or len(path) < 2:
        return ""

    for (cx, cy), (nx, ny) in zip(path, path[1:]):
        direction = (nx - cx, ny - cy)
        route.append(moves.get(direction, "X"))
    return "".join(route)


def generate_output(maze: MazeGenerator) -> None:
    """
    Generates and saves the output file containing the current state
    of the maze.

    Retrieves the maze matrix, the solved path, and the entry/exit points
    from the MazeGenerator object.
    Formats this data according to the subject standard
    (Hexadecimal -> Entry -> Exit -> Path) and writes it to disk.

    Args:
        maze (MazeGenerator): Current instance of the maze generator.
    """
    maze_hex = int_to_hex(maze.get_grid())
    maze_txt = hex_to_str(maze_hex)
    maze_path = dir_to_path(maze.get_path())

    # Solucionado el tipado de mypy: Dict[str, Any] permite mezclar
    # strings y tuplas.
    output_data: Dict[str, Any] = {
        'ENTRY': maze.entry,
        'EXIT': maze.exit,
        'OUTPUT_FILE': maze.output_file,
        'PATH': maze_path
    }

    with open(output_data['OUTPUT_FILE'], 'w', encoding="utf-8") as output:
        # Añade el laberinto al output.txt
        output.write(maze_txt)
        output.write("\n")
        # Añade el entry y exit al output.txt
        output.write(f"{output_data['ENTRY'][0]},{output_data['ENTRY'][1]}\n")
        output.write(f"{output_data['EXIT'][0]},{output_data['EXIT'][1]}\n")
        output.write(f"{output_data['PATH']}\n")
