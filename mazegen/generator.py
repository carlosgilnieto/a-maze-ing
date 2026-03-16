"""
Módulo del motor de generación y resolución de laberintos.

Contiene la clase principal `MazeGenerator`, que implementa los algoritmos
de búsqueda en profundidad (DFS) para generar laberintos perfectos,
destrucción aleatoria para laberintos imperfectos, y búsqueda en amplitud
(BFS) para encontrar la ruta óptima de salida.
"""

from typing import List, Any, Dict, Optional, Set, Tuple, Generator
from .errors import MazeError
from .parsing import (get_config_from_file, check_42_pattern)
import random


class MazeGenerator():
    """
    Main engine for generating and solving mazes.

    Implements DFS algorithms for generation (perfect and imperfect)
    and BFS for finding the optimal path. Handles the “42” pattern as
    a protected area within the maze.

    Attributes:
        width: Width of the maze in number of cells.
        height: Height of the maze in number of cells.
        entry: Coordinates of the entrance (x, y).
        exit: Coordinates of the exit (x, y).
        output_file: Name of the output file.
        is_perfect: If True, generates a perfect maze (a single path).
        seed: Seed for reproducibility. 0 means random.
        animation: If True, enables animation mode.
        speed_animation: Animation speed in seconds.
    """

    def __init__(self, width: int,
                 height: int,
                 entry: Tuple[int, int],
                 exit: Tuple[int, int],
                 seed: int = 0,
                 perfect: bool = True,
                 output_file: str = "output_maze.txt",
                 speed_animation: float = 0) -> None:
        """
        Initialises the maze generator and prepares the grid.

        Validates the parameters, checks whether the size allows for the
        “42” pattern, and calls reset_maze to construct the initial grid.

        Args:
            width: Maze width in number of cells.
            height: Maze height in number of cells.
            entry: Entry coordinates as a tuple (x, y).
            exit: Exit coordinates as a tuple (x, y).
            seed: Seed for reproducibility. Default 0 (random).
            perfect: If True, generates a perfect maze. Default True.
            output_file: Name of the output file. Default “maze.txt”.
            animation: Enables animation mode. Default False.
            speed_animation: Animation speed in seconds. Default 0.

        Raises:
            MazeError: If any parameter does not meet the logical constraints.
        """
        self._check_values(width, height, entry, exit,
                           seed, perfect, output_file,
                           speed_animation)

        check_42_pattern(width, height)

        self.width: int = width
        self.height: int = height
        self.entry: Tuple[int, int] = entry
        self.exit: Tuple[int, int] = exit
        self.output_file: str = output_file
        self.is_perfect: bool = perfect
        self.seed: int = seed
        self.animation: bool = False if speed_animation == 0 else True
        self.speed_animation: float = speed_animation

        # DFS (Depth-First Search) for generation.
        self.__grid: List[List[int]] = []
        self.__visited: List[List[bool]] = []

        self.__directions = [
                (0, -1, 1, 4),  # North (1) / opposite South (4)
                (1, 0, 2, 8),   # East  (2)  / opposite West (8)
                (0, 1, 4, 1),   # South (4) / opposite North (1)
                (-1, 0, 8, 2)   # West  (8)  / opposite East (2)
            ]

        # Pattern 42
        self.__protected: Set[Tuple[int, int]] = set()
        self.__impar_pattern: List[List[Tuple[int, int]]] = [
                            [(0, 0), (0, 2), (0, 4), (0, 5), (0, 6)],
                            [(1, 0), (1, 2), (1, 6)],
                            [(2, 0), (2, 1), (2, 2), (2, 4), (2, 5), (2, 6)],
                            [(3, 2), (3, 4)],
                            [(4, 2), (4, 4), (4, 5), (4, 6)]]

        self.__par_pattern: List[List[Tuple[int, int]]] = [
                              [(0, 0), (0, 2), (0, 5), (0, 6), (0, 7)],
                              [(1, 0), (1, 2), (1, 7)],
                              [(2, 0), (2, 1), (2, 2), (2, 5), (2, 6), (2, 7)],
                              [(3, 2), (3, 5)],
                              [(4, 2), (4, 5), (4, 6), (4, 7)]]

        # BFS (Breadth-First Search) for solving.
        self.__path: list[Tuple[int, int]] = []
        self.reset_maze()

    @classmethod
    def maze_from_file(cls, filename: str) -> "MazeGenerator":
        """
        Creates an instance of MazeGenerator from a configuration file.

        Alternative constructor that reads and parses the specified file,
        converts the keys to lower case, and passes them to the main
        constructor.

        Args:
            filename: Path to the configuration file in KEY=VALUE format.

        Returns:
            New instance of MazeGenerator configured according to the file.

        Raises:
             MazeError: If the file does not exist, it does not have read
                permissions or contains formatting errors or invalid values.

        """

        try:
            config: Dict[str, Any] = get_config_from_file(filename)
        except (FileNotFoundError, PermissionError) as e:
            raise MazeError("FILE ERROR", [str(e)])
        except ValueError as e:
            raise MazeError("CONFIG ERROR", e.args[0])

        config = {k.lower(): v
                  for k, v in config.items()}
        maze: MazeGenerator = cls(**config)
        return maze

    def get_grid(self) -> List[List[int]]:
        """
        Returns the current maze grid.

        Returns:
            A 2D array where each integer represents the walls
            of a cell encoded in binary (North=1, East=2, South=4, West=8).
        """
        return self.__grid

    def get_path(self) -> List[Tuple[int, int]]:
        """
        Returns the current path.

        Returns:
            A list of tuples representing the coordinates of the path.
        """
        return self.__path

    def set_path(self, path: List[Tuple[int, int]]) -> None:
        """
        Manually set the path of the maze.

        Args:
            path: A list of coordinates (x, y) that make up the path.
        """
        self.__path = path

    def _check_values(self, width: int,
                      height: int,
                      entry: Tuple[int, int],
                      exit: Tuple[int, int],
                      seed: int = 0,
                      perfect: bool = True,
                      output_file: str = "output_maze.txt",
                      speed_animation: float = 0) -> None:
        """
        Validates the logical constraints of the maze parameters.

        Checks that the dimensions are valid, that the entry and exit
        are distinct and within the limits, and that the animation
        configuration is consistent.

        Args:
            width: Maze width in number of cells.
            height: Maze height in number of cells.
            entry: Entry coordinates as a tuple (x, y).
            exit: Exit coordinates as a tuple (x, y).
            seed: Seed for reproducibility. Default 0.
            perfect: If True, generates a perfect maze. Default True.
            output_file: Name of the output file. Default “maze.txt”.
            speed_animation: Animation speed in seconds. Default: 0.

        Raises:
            MazeError: If one or more parameters do not meet the constraints,
                grouping all errors encountered.
        """
        error_list: List[str] = []
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

        if speed_animation < 0.01 and speed_animation != 0:
            error_list.append("SPEED_ANIMATION minimun value=0.01)")
        elif speed_animation > 1:
            error_list.append("SPEED_ANIMATION max value=1)")

        if len(error_list) > 0:
            raise MazeError("MAZEGEN ERROR", error_list)

    def _set_pattern_42(self) -> None:
        """
        Overlays the “42” pattern centred on the grid and marks its cells as
        protected.

        Calculates the pattern's coordinates depending on whether the width
        is even or odd, centres them on the grid and marks them as visited
        and protected so that the DFS does not alter them.

        Raises:
            MazeError: If the entry or exit coincides with any cell
                in the “42” pattern.
        """
        error_list = []
        if self.width < 9 or self.height < 7:
            return

        if self.width % 2 == 0:
            pattern = self.__par_pattern
        else:
            pattern = self.__impar_pattern

        center_x = self.width // 2
        center_y = self.height // 2

        offset_x = center_x - (3 if self.width % 2 else 4)
        offset_y = center_y - 2

        pattern_coords: Set[Tuple[int, int]] = set()
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

        if len(error_list) > 0:
            raise MazeError("MAZEGEN", error_list)

        for y in range(self.height):
            for x in range(self.width):
                if (x, y) in pattern_coords:
                    self.__visited[y][x] = True

    def reset_maze(self) -> List[List[int]]:
        """
        Resets the maze with all walls closed.

        Initialises the random seed, creates the grid with all cells
        set to 15 (all walls closed), resets the visited cells
        and applies the “42” pattern.

        Returns:
            Grid reset with all walls closed (value 15 per cell).

        Raises:
            MazeError: If the input or output matches the “42” pattern.
        """

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

    def generate(self) -> List[List[int]]:
        """
        Generates the complete maze according to the configured mode.

        Calls reset_maze and executes the corresponding algorithm
        until completion.

        Returns:
            The generated grid as a 2D array of integers.
        """
        self.reset_maze()
        if self.is_perfect:
            generator = self.perfect_algo()
        else:
            generator = self.non_perfect_algo()

        for __, _ in generator:
            pass

        return self.__grid

    def calculate_path(self) -> List[Tuple[int, int]]:
        """
        Calculate the shortest path between the start and end points using BFS.

        Run `solve_algo` until it completes and store the result
        in the private attribute `__path`.

        Returns:
            A list of coordinates (x, y) that form the shortest path
        """
        generator = self.solve_algo()

        for _, _ in generator:
            pass
        return self.__path

    def perfect_algo(self) -> Generator[Tuple[Any, Any], None, None]:
        """
        Generate a perfect maze using DFS with backtracking.

        Traverse the grid by randomly selecting unvisited neighbours and
        breaking down the shared wall. Backtrack when a
        dead end is encountered. This is a generator designed for animation.

        Returns:
            A tuple (grid, stack) containing the current state of the grid and
            the DFS stack at each step.
        """
        start_x, start_y = self.__get_valid_random_point()

        self.__visited[start_y][start_x] = True

        stack = [(start_x, start_y)]

        yield self.__grid, stack

        while stack:
            cx, cy = stack[-1]
            unvisited_neighbors = []

            for dx, dy, wall, opp_wall in self.__directions:
                nx, ny = cx + dx, cy + dy

                if (0 <= nx < self.width) and (0 <= ny < self.height):
                    if not self.__visited[ny][nx]:
                        unvisited_neighbors.append((nx, ny, wall, opp_wall))

            if unvisited_neighbors:
                nx, ny, wall, opp_wall = random.choice(unvisited_neighbors)

                self.__grid[cy][cx] &= ~wall
                self.__grid[ny][nx] &= ~opp_wall

                self.__visited[ny][nx] = True
                stack.append((nx, ny))
                yield self.__grid, stack
            else:
                stack.pop()
                yield self.__grid, stack
        yield self.__grid, stack

    def non_perfect_algo(self) -> Generator[Tuple[Any, Any], None, None]:
        """
        Generates an imperfect maze with multiple possible paths.

        First, run `perfect_algo` to create a perfect maze,
        then randomly destroy a percentage of the interior walls,
        while preserving the protected cells and the corridor width limit.

        Yields:
            Tuple (grid, modified_cells) containing the current state of the
            grid and the two cells affected by each wall demolition.
        """

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

            if not (0 <= nx < self.width and 0 <= ny < self.height):
                continue

            if (cx, cy) in self.__protected or (nx, ny) in self.__protected:
                continue

            if not (self.__grid[cy][cx] & wall):
                continue

            if (self.__count_walls(cx, cy) <= 1 or
                    self.__count_walls(nx, ny) <= 1):
                continue

            self.__grid[cy][cx] &= ~wall
            self.__grid[ny][nx] &= ~opp_wall
            amount_walls -= 1

            # Se hace un ministack para poder animar
            yield self.__grid, [(cx, cy), (nx, ny)]

        yield self.__grid, []

    def solve_algo(self) -> Generator[Tuple[Any, Any], None, None]:
        """
        Find the shortest path between the start and end points using BFS.

        Explore the grid level by level using a queue. Upon reaching the end
        point, reconstruct the path by traversing the `came_from` map
        backwards.

        Outputs:
            A tuple (came_from, current_cell) containing the return map and the
            coordinate explored at each step.
        """

        queue_pos = [self.entry]
        came_from: Dict[
            Tuple[int, int], Optional[Tuple[int, int]]
            ] = {self.entry: None}

        while queue_pos:
            cx, cy = queue_pos.pop(0)
            if (cx, cy) == self.exit:
                break

            for dx, dy, wall, _ in self.__directions:
                nx, ny, = cx + dx, cy + dy
                if (0 <= nx < self.width) and (0 <= ny < self.height):
                    if (not (self.__grid[cy][cx] & wall)
                            and (nx, ny) not in came_from):
                        came_from[(nx, ny)] = (cx, cy)
                        queue_pos.append((nx, ny))
                        yield came_from, (nx, ny)

        path: List[Tuple[int, int]] = []
        current: Optional[Tuple[int, int]] = self.exit

        while current is not None:
            path.append(current)
            current = came_from[current]
        self.__path = path[::-1]

    def __count_walls(self, x: int, y: int) -> int:
        """
        Counts the number of closed walls in a cell.

        Converts the cell's value to binary and counts the bits set to 1.

        Args:
            x: Horizontal coordinate of the cell.
            y: Vertical coordinate of the cell.

        Returns:
            Number of closed walls (between 0 and 4).
        """
        cell = self.__grid[y][x]
        return bin(cell).count('1')

    def __get_valid_random_point(self) -> Tuple[int, int]:
        """
        Returns a random coordinate outside the “42” pattern.

        Generates random coordinates until one is found that is not
        within the set of protected cells.

        Returns:
            A tuple (x, y) with valid coordinates within the grid.
        """
        while True:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)

            if (x, y) not in self.__protected:
                return (x, y)

    def open_doors(self, pos: tuple[int, int]) -> None:
        """
        Open the outer wall of a cell if it is on the edge of the maze.

        Determine which edge the cell is on and remove the corresponding wall
        using bitwise operations.

        Args:
            pos: Coordinates (x, y) of the cell to be opened
        """
        x, y = pos

        # North = 1 (0001)
        # East  = 2 (0010)
        # South = 4 (0100)
        # West  = 8 (1000)

        if (y == 0):
            self.__grid[y][x] &= ~1
        elif (y == self.height - 1):
            self.__grid[y][x] &= ~4
        elif (x == 0):
            self.__grid[y][x] &= ~8
        elif (x == self.width - 1):
            self.__grid[y][x] &= ~2

    def debug_print_state(self) -> None:
        """
        Imprime el estado actual de 'grid'
        """
        for y in range(self.height):
            row_grid = ""
            for x in range(self.width):
                row_grid += f" {self.__grid[y][x]:>2} "
            print(row_grid)
