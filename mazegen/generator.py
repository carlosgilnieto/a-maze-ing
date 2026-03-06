from typing import List, Any, Tuple, Dict


class MazeGenerator():
    # CAMBIAR PARAMETROS DE ENTRADA A DICCIONARIO
    def __init__(self, config: Dict[str, Any]):
        self.width = config['WIDTH']
        self.height = config['HEIGHT']
        self.entry = config['ENTRY']
        self.exit = config['EXIT']
        self.is_perfect = ['PERFECT']
        self.seed = ['SEED']
        self.grid = [[15 for _ in range(config['WIDTH'])]
                     for _ in range(config['HEIGHT'])]
        self.visited = [[False for _ in range(config['WIDTH'])]
                        for _ in range(config['HEIGHT'])]  # grid de bools para DFS

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
        Para usar división entera y que no haya float, con doble barra:
        """
        return (self.width // 2, self.height // 2)
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


    def check_maze_42(self, maze: List[List[Any]]):
        """
        Dibuja rid inicial en la terminal y superpone el patrón '42' en el centro.
        Utiliza códigos ANSI para darle color.
        """
        if self.width % 2 == 0:
            pattern = self.par_pattern
        else:
            pattern = self.impar_pattern
        # 2. Calcular el punto de inicio para que el "42" quede centrado
        center_x = self.width // 2
        center_y = self.height // 2
        # Desplazamos el punto de inicio hacia arriba y a la izquierda.
        # (El patrón tiene unas 5 (0-4) filas de alto y 7-8 (0-6) columnas de ancho)
        offset_x = center_x - 3
        offset_y = center_y - 2
        # 3. Extraer todas las coordenadas del patrón y adaptarlas al tamaño real del grid
        # Usamos un 'set' (conjunto) porque buscar en un set es más rápido que en una lista
        pattern_coords = set()
        for row in pattern:
            for py, px in row:
                real_x = px + offset_x
                real_y = py + offset_y
                pattern_coords.add((real_x, real_y))
        # 4. Dibujar la cuadrícula en la terminal
        print(f"\n--- Grid Inicial ({self.width}x{self.height}) con Patrón 42 ---")
        for y in range(self.height):
            line_str = ""
            for x in range(self.width):
                if (x, y) in pattern_coords:
                    line_str += "\033[43m  \033[0m"
                else:
                    line_str += "\033[40m  \033[0m"
            print(line_str)



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