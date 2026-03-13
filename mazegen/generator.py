from typing import List, Any, Dict, Tuple, Generator
from .errors import MazeError
from .parsing import get_config_from_file, check_42_pattern
import random


class MazeGenerator():
    def __init__(self, width: int, height: int,
                 entry: tuple, exit: tuple,
                 seed=0,
                 perfect=True, output_file="maze.txt",
                 animation=False, speed_animation=0):

        self._check_values(width, height, entry, exit,
                           seed, perfect, output_file,
                           animation, speed_animation)

        check_42_pattern(width, height)

        self.width: int = width
        self.height: int = height
        self.entry: tuple = entry
        self.exit: tuple = exit
        self.output_file: str = output_file
        self.is_perfect: bool = perfect
        self.seed: int = seed
        self.animation: bool = animation
        self.speed_animation: float = speed_animation

        #DFS
        self.__grid: list = []
        self.__visited: list = []
        # Mapeo de direcciones y paredes (usando sistema de bits)
        # Asumiendo los bits estándar: Norte=1, Este=2, Sur=4, Oeste=8
        # Formato: (DesplX, DesplY, Pared a romper en celda actual (Wall),
        #           pared a romper en la vecina(opp_wall))
        self.__directions = [
                (0, -1, 1, 4),  # Norte
                (1, 0, 2, 8),   # Este
                (0, 1, 4, 1),   # Sur
                (-1, 0, 8, 2)   # Oeste
            ]

        #Pattern
        self.__protected = set() #Lista de coordenadas que no pueden ser modificadas
        self.__impar_pattern = [[(0, 0),         (0, 2), (0, 4), (0, 5), (0, 6)],
                            [(1, 0),         (1, 2),                 (1, 6)],
                            [(2, 0), (2, 1), (2, 2), (2, 4), (2, 5), (2, 6)],
                            [                (3, 2), (3, 4)                ],
                            [                (4, 2), (4, 4), (4, 5), (4, 6)]]
        self.__par_pattern = [[(0, 0),         (0, 2), (0, 5), (0, 6), (0, 7)],
                              [(1, 0),         (1, 2),                 (1, 7)],
                              [(2, 0), (2, 1), (2, 2), (2, 5), (2, 6), (2, 7)],
                              [                (3, 2), (3, 5)                ],
                              [                (4, 2), (4, 5), (4, 6), (4, 7)]]

        #BFS
        self.__path: list = []
        self.reset_maze()

    @classmethod
    def maze_from_file(cls, filename: str) -> "MazeGenerator":
        """
        Genera un objeto maze apartid de un archivo
        """
        #Duelve raise de FileNotFound, PermissionError y ValueError
        try:
            config: Dict[str, Any] = get_config_from_file(filename)
        except (FileNotFoundError, PermissionError) as e:
            raise MazeError("FILE ERROR", [e])
        except ValueError as e:
            raise MazeError("CONFIG ERROR", [e])
        config = {k.lower(): v
                  for k, v in config.items()}
        maze: MazeGenerator = cls(**config)
        return maze

    def get_grid(self):
        return self.__grid

    def get_path(self):
        return self.__path

    def set_path(self, path: List[Tuple]):
        self.__path = path

    def _check_values(self, width: int, height: int,
                      entry: tuple, exit: tuple,
                      seed=0,
                      perfect=True, output_file="maze.txt",
                      animation=False, speed_animation=0):
        error_list: List = [] #Listado de errores
        if width < 1:
            error_list.append("Recomended minimun size: WIDTH=2")
        if height < 1:
            error_list.append("Recomended minimun size: HEIGHT=2")
        if entry == exit:
            error_list.append("The value of ENTRY and EXIT must be different")
        if ((0 > entry[0] or entry[0] >= width) or
                (0 > entry[1] or entry[1] >= height)):
            error_list.append("The value of ENTRY must be between "
                              "(0,0) and (< WIDTH, < HEIGHT)")
        if ((0 > exit[0] or exit[0] >= width) or
                (0 > exit[1] or exit[1] >= height)):
            error_list.append("The value of EXIT must be between "
                              "(0,0) and (< WIDTH, < HEIGHT)")
        if animation:
            if speed_animation < 0.01:
                error_list.append("Need SPEED_ANIMATION key or "
                                  "SPEED_ANIMATION minimun value=0.01)")
        else:
            if speed_animation > 0:
                error_list.append("You need set ANIMATION=True or quit SPEED_ANIMATION key")
        if len(error_list) > 0:
            raise MazeError("MAZEGEN ERROR", error_list)

    def _set_pattern_42(self) -> None:
        """
        Dibuja grid inicial en la terminal y superpone el patrón '42' en el centro.
        Utiliza códigos ANSI para darle color.
        """
        error_list = []
        if self.width < 9 or self.height < 7:
           return # Salimos de la función patrón 42 y generamos laberinto normal.

        if self.width % 2 == 0:
            pattern = self.__par_pattern
        else:
            pattern = self.__impar_pattern
        # 2. Calcular el punto de inicio para que el "42" quede centrado
        center_x = self.width // 2
        center_y = self.height // 2
        # Desplazamos el punto de inicio hacia arriba y a la izquierda.
        # (El patrón tiene unas 5 (0-4) filas de alto y 7-8 (0-6) columnas de ancho)
        offset_x = center_x - (3 if self.width % 2 else 4)
        offset_y = center_y - 2
        # 3. Extraer todas las coordenadas del patrón y adaptarlas al tamaño real del grid
        # Usamos un 'set' (conjunto) porque buscar en un set es más rápido que en una lista
        pattern_coords = set()
        for row in pattern:
            for py, px in row:
                real_x = px + offset_x
                real_y = py + offset_y
                if self.entry == (real_x, real_y):
                    error_list.append(f"ENTRY={self.entry} "
                                         "must be outside of the 42 patter, "
                                         "try other position")
                if self.exit == (real_x, real_y):
                    error_list.append(f"EXIT={self.exit} "
                                         "must be outside of the 42 patter, "
                                         "try other position")
                pattern_coords.add((real_x, real_y))
                self.__protected.add((real_x, real_y))

        #Printea errores
        if len(error_list) > 0:
            raise MazeError("MAZEGEN", error_list)

        # 4. Añadido patrón como visitado.
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) in pattern_coords:
                    self.__visited[y][x] = True

    def reset_maze(self) -> List[List[int]]:
        """
        Crea el laberinto con todas las paredes cerradas y añade el 42 patron
        """
        # Esto hace que sea aleatorio cada vez que se genera uno nuevo
        if self.seed:
            random.seed(self.seed)
        else:
            random.seed()
        self.__grid = [[15 for _ in range(self.width)]
                       for _ in range(self.height)]
        self.__visited = [[False for _ in range(self.width)]
                          for _ in range(self.height)]
        try:
            self._set_pattern_42()
        except MazeError as e:
            print(e.errors)
            raise MazeError("MAZEGEN", e.errors)
        return self.__grid

    def generate(self) -> None:
        self.reset_maze()
        if self.is_perfect:
            generator = self.perfect_algo()
        generator = self.non_perfect_algo()

        #Al ser generadores hay que hacer que se haga toda la funcion
        for __, _ in generator:
            pass

        return self.__grid

    def calculate_path(self) -> None:
        generator = self.solve_algo()

        #Al ser generadores hay que hacer que se haga toda la funcion
        for _, _ in generator:
            pass
        return self.__path

    def perfect_algo(self) -> Generator:
        """
        DFS algoritmo usado como generador para poder animarlo
        """
        # 2. Celda de inicio (para empezar en 0,0) a construir el laberinto
        # Usar random?? para que sea aleatorio
        # start_x, start_y = 0, 0
        start_x, start_y = self.__get_valid_random_point()

        self.__visited[start_y][start_x] = True  # Celda de inicio visitada.
        # "pila" (stack) nos servirá para retroceder (backtrack)
        stack = [(start_x, start_y)]

        yield self.__grid, stack
        # 3. Bucle principal del algoritmo
        while stack:
            # Miramos la celda actual (la que está en la cima de la pila)
            cx, cy = stack[-1]
            # Buscar todos los vecinos válidos que NO han sido visitados
            unvisited_neighbors = []

            # bucle que dará exactamente 4 vueltas, una por cada punto
            # cardinal de la lista DIRECTIONS
            for dx, dy, wall, opp_wall in self.__directions:
                nx, ny = cx + dx, cy + dy  # next x, next y. Es la celda 'vecina'
                # Calcula las coordenadas reales de ese vecino en la cuadrícula

                # Comprobar que el vecino esté dentro de los límites
                if (0 <= nx < self.width) and (0 <= ny < self.height):
                    # Comprobar si NO ha sido visitado
                    if not self.__visited[ny][nx]:
                        unvisited_neighbors.append((nx, ny, wall, opp_wall))

            # Avanzar o retroceder
            if unvisited_neighbors:
                # Elegimos uno al azar para crear la ruta del laberinto
                nx, ny, wall, opp_wall = random.choice(unvisited_neighbors)

                # ROMPER LAS PAREDES:
                # Usamos el operador AND (&) con el complemento a nivel de bits (~)
                # Ejemplo: 15 & ~1 (1111 AND 1110) = 14 (1110) -> Hemos quitado el bit de la pared Norte
                self.__grid[cy][cx] &= ~wall      # celda actual → derriba la pared compartida
                self.__grid[ny][nx] &= ~opp_wall  # celda vecina → derriba la pared compartida

                self.__visited[ny][nx] = True
                stack.append((nx, ny))
                yield self.__grid, stack
            else:
                # Callejón sin salida: Si no hay vecinos no visitados, eliminamos esta celda de la pila
                # y el algoritmo retrocede al anterior:
                stack.pop()
                yield self.__grid, stack
        yield self.__grid, stack

    def non_perfect_algo(self) -> Generator:
        """
        Primero usa el DFS para generar el laberinto y luego aleatoriamente escoge un 25% de las paredes
        para quitarlas y crear posibles caminos
        """
        #Ejecuta perfect_maze y vuelve el yield, cuando deja de haber yield continua la funcion
        yield from self.perfect_algo()

        amount_walls: int = (self.width * self.height) // 75
        attempts = 0
        while amount_walls > 0 and attempts < 2000:
            attempts += 1
            cx = random.randint(1, self.width - 2)
            cy = random.randint(1, self.height - 2)

            direction = random.choice(self.__directions)
            dx, dy, wall, opp_wall = direction
            nx, ny = cx + dx, cy + dy

            # Check la celda estan dentro del laberinto?
            if not (0 <= nx < self.width and 0 <= ny < self.height):
                continue
            # Check la celda y la vecian son protegidas? (42 patron)
            if (cx, cy) in self.__protected or (nx, ny) in self.__protected:
                continue
            #Check la celda ya esta abierta?
            if not (self.__grid[cy][cx] & wall):
                continue
            #Check si la celda o la vecina ya tienen abiertas 2 paredes
            if self.__count_walls(cx, cy) <= 1 or self.__count_walls(nx, ny) <= 1:
                continue

            self.__grid[cy][cx] &= ~wall      # Quita pared en actual
            self.__grid[ny][nx] &= ~opp_wall  # Quita pared en vecina
            amount_walls -= 1

            # Se hace un ministack para poder animar
            yield self.__grid, [(cx, cy), (nx, ny)]

        yield self.__grid, []

    def solve_algo(self) -> Generator:
        """
        Algortimo BFS
        """
        #Lista de posiciones que quedan por comprobar
        queue_pos = [self.entry]

        # came_from sirve como 'visited' y como 'mapa de retorno'
        # { siguiente celda: celda a mirar }
        came_from = {self.entry: None}

        while queue_pos: #Mientras que queden posiciones por mirar...
            cx, cy = queue_pos.pop(0) #Obtendo los datos de la "primera" que encontre
            #Al hacer pop desaparece de la lista

            # Compruebo si es el final del maze
            if (cx, cy) == self.exit:
                break
            # Checkea todas las direcciones de la celda para guardar sus posiciones
            for dx, dy, wall, _ in self.__directions:
                nx, ny, = cx + dx, cy + dy
                if (0 <= nx < self.width) and (0 <= ny < self.height):
                    # Si la celda que se mira es posible ir
                    # y tampoco es una celda que ya se haya "visitado" (Evita bucles de pasillos)
                    if (not (self.__grid[cy][cx] & wall)
                        and (nx, ny) not in came_from):
                        # Se añade que desde (cx, cy) se puede ir a (nx, ny)
                        came_from[(nx, ny)] = (cx, cy)
                        # Se guarda la posicion de (nx, ny) para luego checkear
                        #a donde se puede ir con ella
                        queue_pos.append((nx, ny))
                        yield came_from, (nx, ny)

        #Se ha llegado al final del laberinto y se sabe cual es la ruta
        path = []
        current = self.exit

        while current is not None:
            path.append(current)
            current = came_from[current]
        self.__path = path[::-1]

    def __count_walls(self, x: int, y: int) -> int:
        """Cuenta cuantos 1 hay en la celda"""
        cell = self.__grid[y][x]
        return bin(cell).count('1')

    def __get_valid_random_point(self) -> Tuple[int]:
        while True:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)

            if (x, y) not in self.__protected:
                return (x, y)

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
            self.__grid[y][x] &= ~1
        elif (y == self.height - 1):
            # Está en el borde inferior: romper pared Sur: ~0100 => 1011.
            self.__grid[y][x] &= ~4
        elif (x == 0):
            # Está en el borde izquierdo: romper pared Oeste: ~1000 => 0111.
            self.__grid[y][x] &= ~8
        elif (x == self.width - 1):
            # Está en el borde derecho: romper pared Este: ~0010 => 1101.
            self.__grid[y][x] &= ~2

    def debug_print_state(self):
        """
        Imprime el estado actual de 'grid'
        """
        for y in range(self.height):
            row_grid = ""
            for x in range(self.width):
                # {:>2} asegura que los números ocupen siempre 2 espacios
                row_grid += f" {self.__grid[y][x]:>2} "
            print(row_grid)
