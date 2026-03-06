import random #BORRAR
from mazegen.errors import print_error
from typing import List, Any, Dict

#BORRAR (funcion auxiliar para pruebas)
def generate_maze(w, h) -> list[list[int]]:
    maze = []
    walls = [1,2,4,8,3,5,9,6,10,12,7,11,13,14]
    for y in range(h):
        line = []
        for x in range(w):
            line.append(random.choice(walls))
        maze.append(line)
    return maze

def int_to_hex(maze: List[List[int]]) -> List[List[str]]:
    """ Pasa de un 'grid' en Decimal a Hexadecimal"""
    grid:List[List] = []
    for line in maze:
        txt = ""
        for cell in line:
            txt += str(hex(cell)[2:]).upper()
        grid.append(txt)
    return grid

def hex_to_str(maze: List[List[int]]) -> str:
    """ Pasa de un 'grid' en Hexadecimal a un str"""
    output = ""
    for line in maze:
        txt = ""
        for cell in line:
            txt += cell
        output += txt + "\n"
    return output

def generate_output() -> None:
    maze = int_to_hex(generate_maze(5,5))
    maze_txt = hex_to_str(maze)
    #Cambiar por value de dic
    config = {'ENTRY': (1, 1),
              'EXIT': (3, 6),
              'OUTPUT_FILE': "output_maze.txt"}
    with open(config['OUTPUT_FILE'], 'w') as output:
        #Añade el laberinto al output.txt
        output.write(maze_txt)
        output.write("\n")
        #Añade el entry y exit al output.txt
        output.write(f"{config['ENTRY'][0]},{config['ENTRY'][1]}\n")
        output.write(f"{config['EXIT'][0]},{config['EXIT'][1]}\n")

