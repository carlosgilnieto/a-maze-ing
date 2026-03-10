from typing import List
from .generator import MazeGenerator

def int_to_hex(maze: List[List[int]]) -> List[List[str]]:
    """ Pasa de un 'grid' en Decimal a Hexadecimal"""
    grid:List[List] = []
    for line in maze:
        row = ""
        for cell in line:
            row += str(hex(cell)[2:]).upper()
        grid.append(row)
    return grid


def hex_to_str(maze: List[List[int]]) -> str:
    """ Pasa de un 'grid' en Hexadecimal a un str"""
    output = ""
    for line in maze:
        row = ""
        for cell in line:
            row += cell
        output += row + "\n"
    return output


#Esto esta pensado para que directamente vaya en la clase MazeGenerator
def generate_output(maze: MazeGenerator) -> None:
    maze_hex = int_to_hex(maze.grid)
    maze_txt = hex_to_str(maze_hex)
    #Cambiar por value de dic
    output_data = {'ENTRY': maze.entry,
                   'EXIT': maze.exit,
                   'OUTPUT_FILE': maze.output_file}
    with open(output_data['OUTPUT_FILE'], 'w') as output:
        #Añade el laberinto al output.txt
        output.write(maze_txt)
        output.write("\n")
        #Añade el entry y exit al output.txt
        output.write(f"{output_data['ENTRY'][0]},{output_data['ENTRY'][1]}\n")
        output.write(f"{output_data['EXIT'][0]},{output_data['EXIT'][1]}\n")

