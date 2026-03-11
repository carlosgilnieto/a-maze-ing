from typing import List, Tuple
from .generator import MazeGenerator

def int_to_hex(maze: List[List[int]]) -> List[List[str]]:
    """ Pasa de un 'grid' en Decimal a Hexadecimal"""
    grid: List[List] = []
    for line in maze:
        row = ""
        for cell in line:
            row += str(hex(cell)[2:]).upper()
        grid.append(row)
    return grid


def hex_to_str(maze: List[List[int]]) -> str:
    """ Pasa de un 'grid' en Hexadecimal a un str"""
    output: str = ""
    for line in maze:
        row = ""
        for cell in line:
            row += cell
        output += row + "\n"
    return output


def dir_to_path(path: List[tuple]) -> str:
    route: List = []
    moves = {(0, -1): "N",
             (1, 0): "E",
             (0, 1): "S",
             (-1, 0): "W"}
    if not path or len(path) < 2:
        return ""
    
    #Zip hace combinaciones entre el n y n + 1
    #Se comparan la posicion con la siguiente pos y se saca la direccion
    for (cx, cy), (nx, ny) in zip(path, path[1:]):
        direction = (nx - cx, ny - cy)
        route.append(moves.get(direction, "X"))
    return "".join(route)


#Esto esta pensado para que directamente vaya en la clase MazeGenerator
def generate_output(maze: MazeGenerator) -> None:
    maze_hex = int_to_hex(maze.get_grid())
    maze_txt = hex_to_str(maze_hex)
    maze_path = dir_to_path(maze.get_path())
    #Cambiar por value de dic
    output_data = {'ENTRY': maze.entry,
                   'EXIT': maze.exit,
                   'OUTPUT_FILE': maze.output_file,
                   'PATH': maze_path}
    with open(output_data['OUTPUT_FILE'], 'w') as output:
        #Añade el laberinto al output.txt
        output.write(maze_txt)
        output.write("\n")
        #Añade el entry y exit al output.txt
        output.write(f"{output_data['ENTRY'][0]},{output_data['ENTRY'][1]}\n")
        output.write(f"{output_data['EXIT'][0]},{output_data['EXIT'][1]}\n")
        output.write(f"{output_data['PATH']}\n")
