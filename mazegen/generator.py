from typing import List, Any, Tuple, Dict
from .errors import print_error
from .parsing import parsing_config, check_config
import random
import sys

class MazeGenerator():
    def __init__(self, config_file: str):
        #Obtiene los valores del config file
        if config_file:
            try:
                with open(config_file) as f:
                    config = f.read()
                pars_cfg: Dict[str, Any] = parsing_config(config,
                                                          self.get_params())
                if not check_config(pars_cfg, self.get_params()):
                    sys.exit()
                else:
                    config = pars_cfg
            except FileNotFoundError:
                print_error(f"'{config_file}' does not exist in the directory")
                sys.exit()
            except ValueError as e:
                print_error(e)
                sys.exit()

        self.width = config['WIDTH']
        self.height = config['HEIGHT']
        self.entry = config['ENTRY']
        self.exit = config['EXIT']
        self.output_file = config['OUTPUT_FILE']
        self.is_perfect = config['PERFECT']
        self.seed = config.get('SEED')
        self.grid = []
        self.protected = set() #Lista de coordenadas que no pueden ser modificadas
        self.visited = []
        
        # Mapeo de direcciones y paredes (usando sistema de bits)
        # Asumiendo los bits estándar: Norte=1, Este=2, Sur=4, Oeste=8
        # Formato: (DesplX, DesplY, Pared a romper en celda actual (Wall),
        #           pared a romper en la vecina(opp_wall))
        self.directions = [
                (0, -1, 1, 4),  # Norte
                (1, 0, 2, 8),   # Este
                (0, 1, 4, 1),   # Sur
                (-1, 0, 8, 2)   # Oeste
            ]
        self.impar_pattern = [[(0, 0),         (0, 2), (0, 4), (0, 5), (0, 6)],
                            [(1, 0),         (1, 2),                 (1, 6)],
                            [(2, 0), (2, 1), (2, 2), (2, 4), (2, 5), (2, 6)],
                            [                (3, 2), (3, 4)                ],
                            [                (4, 2), (4, 4), (4, 5), (4, 6)]]
        self.par_pattern = [[(0, 0),         (0, 2), (0, 5), (0, 6), (0, 7)],
                              [(1, 0),         (1, 2),                 (1, 7)],
                              [(2, 0), (2, 1), (2, 2), (2, 5), (2, 6), (2, 7)],
                              [                (3, 2), (3, 5)                ],
                              [                (4, 2), (4, 5), (4, 6), (4, 7)]]

    @staticmethod
    def get_params() -> dict[dict[str]]:
        mandatory_params = {'WIDTH': "int",
                            'HEIGHT': "int",
                            'ENTRY': "tuple",
                            'EXIT': "tuple",
                            'OUTPUT_FILE': "file",
                            'PERFECT': "bool"}

        bonus_params = {"SEED": "int"}

        return {'mandatory': mandatory_params,
                'bonus': bonus_params}

    def get_center(self) -> Tuple:
        """
        Te devuelve la coordenada del centro del grid
        Para usar división entera y que no haya float, con doble barra:
        """
        return (self.width // 2, self.height // 2)

    #BORRAR
    def check_maze(self, maze: List[List[Any]], debug=False):
        center = self.get_center()
        print(f"Center: {center}")
        if debug:
            for y, line in enumerate(maze, 1):
                txt = ""
                for x, sqr in enumerate(line, 1):
                    if sqr is False:
                        txt += "\033[40m0\033[0m"
                    else:
                        txt += "\033[43m1\033[0m"
                print(txt)
        else:
            for line in maze:
                txt = ""
                for sqr in line:
                    txt += str(sqr)
                print(txt)

    def pattern_42(self):
        """
        Dibuja grid inicial en la terminal y superpone el patrón '42' en el centro.
        Utiliza códigos ANSI para darle color.
        """
        if self.width < 8 or self.height < 6:
           return # Salimos de la función patrón 42 y generamos laberinto normal.

        if self.width % 2 == 0:
            pattern = self.par_pattern
        else:
            pattern = self.impar_pattern
        # 2. Calcular el punto de inicio para que el "42" quede centrado
        center_x = self.width // 2
        center_y = self.height // 2
        # Desplazamos el punto de inicio hacia arriba y a la izquierda.
        # (El patrón tiene unas 5 (0-4) filas de alto y 7-8 (0-6) columnas de ancho)
        offset_x = center_x - 4
        offset_y = center_y - 2
        # 3. Extraer todas las coordenadas del patrón y adaptarlas al tamaño real del grid
        # Usamos un 'set' (conjunto) porque buscar en un set es más rápido que en una lista
        pattern_coords = set()
        for row in pattern:
            for py, px in row:
                real_x = px + offset_x
                real_y = py + offset_y
                if self.entry == (real_x, real_y):
                    raise ValueError(f"ENTRY={self.entry} "
                                     "must be outside of the 42 patter, "
                                     "try other position")
                elif self.exit == (real_x, real_y):
                    raise ValueError(f"EXIT={self.exit} "
                                     "must be outside of the 42 patter, "
                                     "try other position")
                pattern_coords.add((real_x, real_y))
                self.protected.add((real_x, real_y))

        # 4. Añadido patrón como visitado.
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) in pattern_coords:
                    self.visited[y][x] = True

    def open_doors(self, pos: tuple):
        """
        Comprueba si una coordenada está en el borde del laberinto.
        Si es así, rompe el muro exterior correspondiente para abrirlo al mundo.
        """
        x, y = pos

        # Norte = 1 (0001)
        # Este  = 2 (0010)
        # Sur   = 4 (0100)
        # Oeste = 8 (1000)

        if (y == 0):
            # Está en el borde superior: romper pared Norte: ~0001 => 1110.
            self.grid[y][x] &= ~1
        elif (y == self.height - 1):
            # Está en el borde inferior: romper pared Sur: ~0100 => 1011.
            self.grid[y][x] &= ~4
        elif (x == 0):
            # Está en el borde izquierdo: romper pared Oeste: ~1000 => 0111.
            self.grid[y][x] &= ~8
        elif (x == self.width - 1):
            # Está en el borde derecho: romper pared Este: ~0010 => 1101.
            self.grid[y][x] &= ~2

    def generate_maze(self) -> List[List[int]]:
        # Esto hace que sea aleatorio cada vez que se genera uno nuevo
        if self.seed:
            random.seed(self.seed)
        else:
            random.seed()
        self.grid = [[15 for _ in range(self.width)]
                     for _ in range(self.height)]
        self.visited = [[False for _ in range(self.width)]
                        for _ in range(self.height)]
        try:
            self.pattern_42()
        except ValueError as e:
            print_error(e, "Patter Error")
            sys.exit()

        grid = self.perfect_maze(self.directions)
        if not self.is_perfect:
            return self.non_perfect_maze(self.directions)
        return grid

    def perfect_maze(self, directions: List[tuple]) -> List[List[int]]:
        # 2. Celda de inicio (para empezar en 0,0) a construir el laberinto
        # Usar random?? para que sea aleatorio
        start_x, start_y = 0, 0
        self.visited[start_y][start_x] = True  # Celda de inicio visitada.
        # "pila" (stack) nos servirá para retroceder (backtrack)
        stack = [(start_x, start_y)]

        # 3. Bucle principal del algoritmo
        while stack:
            # Miramos la celda actual (la que está en la cima de la pila)
            cx, cy = stack[-1]
            # Buscar todos los vecinos válidos que NO han sido visitados
            unvisited_neighbors = []

            # bucle que dará exactamente 4 vueltas, una por cada punto
            # cardinal de la lista DIRECTIONS
            for dx, dy, wall, opp_wall in directions:
                nx, ny = cx + dx, cy + dy  # next x, next y. Es la celda 'vecina'
                # Calcula las coordenadas reales de ese vecino en la cuadrícula

                # Comprobar que el vecino esté dentro de los límites
                if (0 <= nx < self.width) and (0 <= ny < self.height):
                    # Comprobar si NO ha sido visitado
                    if not self.visited[ny][nx]:
                        unvisited_neighbors.append((nx, ny, wall, opp_wall))

            # Avanzar o retroceder
            if unvisited_neighbors:
                # Elegimos uno al azar para crear la ruta del laberinto
                nx, ny, wall, opp_wall = random.choice(unvisited_neighbors)

                # ROMPER LAS PAREDES:
                # Usamos el operador AND (&) con el complemento a nivel de bits (~)
                # Ejemplo: 15 & ~1 (1111 AND 1110) = 14 (1110) -> Hemos quitado el bit de la pared Norte
                self.grid[cy][cx] &= ~wall      # celda actual → derriba la pared compartida
                self.grid[ny][nx] &= ~opp_wall  # celda vecina → derriba la pared compartida

                self.visited[ny][nx] = True
                stack.append((nx, ny))
            else:
                # Callejón sin salida: Si no hay vecinos no visitados, eliminamos esta celda de la pila
                # y el algoritmo retrocede al anterior:
                stack.pop()
        return self.grid
    
    def non_perfect_maze(self, directions: List[tuple]) -> List[List[int]]:
        amount_walls: int = (self.width * self.height) // 50
        attempts = 0
        while amount_walls > 0 and attempts < 2000:
            attempts += 1
            cx = random.randint(1, self.width - 2)
            cy = random.randint(1, self.height - 2)

            direction = random.choice(directions)
            dx, dy, wall, opp_wall = direction
            if (cx, cy) in self.protected:
                continue

            if self.grid[cy][cx] & wall:
                nx, ny = cx + dx, cy + dy
        # 1. Verificar límites del laberinto
                if (0 <= nx < self.width) and (0 <= ny < self.height):
                    # 2. Verificar que ninguna esté protegida (Patrón 42)
                    if (nx, ny) not in self.protected:
                        self.grid[cy][cx] &= ~wall      # Quita pared en actual
                        self.grid[ny][nx] &= ~opp_wall  # Quita pared en vecina
                        amount_walls -= 1

    def solve_maze(self) -> List[tuple[int,int]]:
        #Lista de posiciones que quedan por comprobar
        queue_pos = [self.entry]

        # came_from sirve como 'visited' y como 'mapa de retorno'
        # { siguiente celda: celda a mirar }
        came_from = {self.entry: None}
        n = 0 #BORRAR

        while queue_pos: #Mientras que queden posiciones por mirar...
            n += 1
            cx, cy = queue_pos.pop(0) #Obtendo los datos de la "primera" que encontre
            #Al hacer pop desaparece de la lista

            # Compruebo si es el final del maze
            if (cx, cy) == self.exit:
                break
            # Checkea todas las direcciones de la celda para guardar sus posiciones
            for dx, dy, wall, op_wall in self.directions:
                nx, ny, = cx + dx, cy + dy
                if (0 <= nx < self.width) and (0 <= ny < self.height):
                    # Si la celda que se mira es posible ir
                    # y tampoco es una celda que ya se haya "visitado" (Evita bucles de pasillos)
                    if (not (self.grid[cy][cx] & wall)
                        and (nx, ny) not in came_from):
                        # Se añade que desde (cx, cy) se puede ir a (nx, ny)
                        came_from[(nx, ny)] = (cx, cy)
                        # Se guarda la posicion de (nx, ny) para luego checkear
                        #a donde se puede ir con ella
                        queue_pos.append((nx, ny))
            # print(f"==={n}===")
            # for pos in came_from:
            #     print(f"{pos}:{came_from[pos]}")
            # print(queue)

        #Se ha llegado al final del laberinto y se sabe cual es la ruta
        
        path = []
        current = self.exit

        while current is not None:
            path.append(current)
            current = came_from[current]
        print(path)
        return path[::-1]
    
    def debug_print_state(self):
        """
        Imprime el estado actual de 'grid'
        """
        for y in range(self.height):
            row_grid = ""
            for x in range(self.width):
                # {:>2} asegura que los números ocupen siempre 2 espacios
                row_grid += f" {self.grid[y][x]:>2} "
            print(row_grid)
