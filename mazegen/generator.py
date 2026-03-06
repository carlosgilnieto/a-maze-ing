from typing import List, Any, Tuple


class MazeGenerator():
    #CAMBIAR PARAMETROS DE ENTRADA A DICCIONARIO
    def __init__(self, width: int, height: int, entry: tuple, exit: tuple,
                 is_perfect: bool, seed=10):
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit
        self.is_perfect = is_perfect
        self.seed = seed
        self.grid = [[15 for _ in range(width)]
                     for _ in range(height)]
        self.visited = [[False for _ in range(width)]
                        for _ in range(height)] #grid de bools para DFS
        
        self.par_pattern = [[(0, 0),         (0, 2), (0, 4), (0, 5), (0, 6)],
                            [(1, 0),         (1, 2),                 (1, 6)],
                            [(2, 0), (2, 0), (2, 2), (2, 4), (2, 5), (2, 6)],
                            [                (3, 2), (2, 4)                ],
                            [                (4, 2), (4, 4), (2, 5), (2, 6)]]
        self.impar_pattern = [[(0, 0),         (0, 2), (0, 5), (0, 6), (0, 7)],
                              [(1, 0),         (1, 2),                 (1, 7)],
                              [(2, 0), (2, 0), (2, 2), (2, 5), (2, 6), (2, 7)],
                              [                (3, 2), (2, 5)                ],
                              [                (4, 2), (4, 5), (2, 6), (2, 7)]]

    def get_center(self) -> Tuple:
        """
        Te devuelve la coordenada del centro del grid
        """
        return (self.width / 2, self.height / 2)
    # def set_patron(self, center: tuple):
    #     if self.width % 2 == 0:

    #BORRAR
    def check_maze(self, maze: List[List[Any]], debug=False):
        center = self.get_center()
        print(f"Center: {center}")
        if debug:
            for y, line in enumerate(maze, 1):
                txt = ""
                for x, sqr in enumerate(line, 1):
                    if sqr is False:
                        if (x == center[0] or
                                y == center[1]):
                            txt += "\033[43m0\033[0m"
                        else: 
                            txt += "0"
                    else:
                        txt += "1"
                print(txt)
        else:
            for line in maze:
                txt = ""
                for sqr in line:
                    txt += str(sqr)
                print(txt)

def generate_maze(self):
    # 1. Mapeo de direcciones y paredes (usando sistema de bits)
    # Asumiendo los bits estándar: Norte=1, Este=2, Sur=4, Oeste=8
    # Formato: (DesplX, DesplY, Pared a romper en celda actual,
    #           pared a romper en la vecina)
    DIRECTIONS = [
            (0, -1, 1, 4),  # Norte
            (1, 0, 2, 8),   # Este
            (0, 1, 4, 1),   # Sur
            (-1, 0, 8, 2)   # Oeste
        ]

    # 2. Celda de inicio (para empezar en 0,0) a construir el laberinto
    # Usar random?? para que sea aleatorio
    start_x, start_y = 0, 0
    self.visited[start_y][start_x] = True