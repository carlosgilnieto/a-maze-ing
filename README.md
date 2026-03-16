<!-- markdownlint-disable-next-line MD041 -->
*This project has been created as part of the 42 curriculum by cagil, irivas-v.*

# A-Maze-ing: Procedural Maze Generation and Solving

## Description

**A-Maze-ing** is a maze generation and solving system developed as part of the
42 curriculum. The project focuses on maze generation, constraint enforcement
 (including the mandatory "42 stamp"), shortest-path solving, and
interactive ASCII visualization.

### Goals

- Generate perfect and imperfect mazes using procedural algorithm.
- Solve mazes using shortest-path pathfinding algorithm.
- Enforce structural constraints (borders, connectivity, mandatory 42 pattern).
- Provide an interactive, ANSI-colored ASCII visualization.

---

## Instructions

### Installation

```bash
# Clone the repository
git clone <git repository>
cd a-maze-ing

# **Optional**: Create a virtual environment and install the 'mazagen' package
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
make install
```

### Execution

```bash
# Run the maze generator and solver with interactive visualization
make run

# Run manually with a specific configuration file
python3 a_maze_ing.py config.txt

# Run static type checking and linting (mypy + flake8)
make lint

# Run static type checking and strict linting (mypy + flake8)
make lint --strict
```

### End

```bash
# Clean files at program exit.
make clean

# Exit virtual environment
deactivate
```

### Configuration File Format

The maze is configured via a `KEY=VALUE` text file. Comments starting with `#` are ignored.

```
# Mandatory fields (required for all mazes)
WIDTH=20                    # Maze width in cells (must be > 1)
HEIGHT=15                   # Maze height in cells (must be > 1)
ENTRY=0,0                   # Entry point coordinates (x,y) (must be > 0 and < WIDTH)
EXIT=19,14                  # Exit point coordinates (x,y) (must be > 0 and < HEIGHT)
OUTPUT_FILE=maze.txt        # Output file path for hexadecimal maze
PERFECT=True                # True for perfect maze (One path resolution) False for imperfect ()

# Bonus fields (optional, have sensible defaults)
SEED=42                     # Random seed (default: 42; use empty/None to disable)
SPEED_ANIMATION=0.01        # Delay in seconds between frames (e.g., 0.01). 
                              Disable animation = 0. Max = 1.

# Comments are supported (lines starting with #)
# Empty lines are ignored
```

**Example Configuration:**

```
WIDTH=20
HEIGHT=15
ENTRY=0,1
EXIT=19,14
OUTPUT_FILE=output_maze.txt
PERFECT=True
SEED=42 # Optional
SPEED_ANIMATION=0.01 # Optional
```

### Interactive Commands

Once the maze is displayed, the following commands are available:

| Command | Action |
|---------|--------|
| `1` | Regenerate maze (creates a new maze with current config/seed)
| `2` | Toggle solution path display |
| `3` | Change colors (Cycles circularly through the available ANSI color palettes)
| `4` | Exit program|

## Algorithms & Constraint Enforcement

### Chosen Algorithm: DFS (Depth-First Search) with Backtracking

DFS was chosen as the generation algorithm because:

1. **Simplicity & Memory Efficiency**:Runs smoothly using an iterative stack approach.
2. **Perfect Maze Generation**: Guarantees a perfect maze (no loops, all cells connected).
3. **Visual Appeal**: Naturally generates mazes with long, winding corridors which makes them challenging and visually striking.
4. **Animation-Friendly**: Easily yields step-by-step states for terminal visualization.

## Imperfect Mazes

If `PERFECT=False` is set in the configuration, the engine first generates a perfect DFS maze and then randomly destroys ~75% of the remaining walls, creating multiple valid paths and closed loops.

## Solving Algorithm: BFS (Breadth-First Search)

The system uses BFS for pathfinding. Unlike DFS, BFS guarantees finding the shortest possible path between the entry and the exit, exploring the maze level by level radially.

---

## Constraint Enforcement (The "42" Stamp)

After validating sizes, mazes are enhanced with the mandatory pattern:

- For grids of at least `9x7`, an immutable **'42' pattern** is embedded in the center.
- The coordinates of the pattern are protected (`self.__protected`) to ensure that neither the DFS nor the imperfect wall-breaker algorithms destroy the structural integrity of the numbers

---

## Reusable Code Architecture

The reusable component required by Chapter VI is the module
`mazegen`, which is packaged as `mazegen-1.0.0-py3-none-any.whl` and located at the
root of the repository. This module can be installed independently via pip:

```bash
pip install mazegen-1.0.0-py3-none-any.whl
```


### Package Documentation (required by subject)

**Instantiate and use the generator (basic example):**

```python
# or from maze import MazeGenerator
import mazegen

# Initialize the generator directly
maze = MazeGenerator(width=20, height=15, entry=(0,0), exit=(19,14), perfect=True)

# Uses the Factory Method to parse the file and instantiate the object
maze = MazeGenerator.maze_from_file("config.txt")

# Generate and solve without animation
maze_grid = maze.generate()
path = maze.calculate_path()

# Generate and solve with animation
    # Renderizes generation process
    render_generation(maze)

    # Renderizes path resolution
    render_solve(maze)
```

**Instantiate from a config file**

- width, height: maze dimensions (int)
- seed: int or None (None => random)
- perfect: bool (True => perfect maze; False => may create loops)
- Speed Animation: float (used when float > 0. If speed animation = 0, no animation)

**Access the generated structure and a solution:**

- maze.width, maze.height
- maze.cells[y][x]: int bitmask in 0..15
  (Bits: N=1, E=2, S=4, W=8; bit set => wall is CLOSED)
- self.__protected for 42 pattern (if present)
- path is a list of moves like ["N", "E", ...]
- maze.get_grid(): Returns the 2D matrix of integers (0-15 bitmasks).
- maze.get_path(): Returns the list of (x, y) tuples forming the shortest path.
- maze.width, maze.height: Access dimensions.

### Building the mazegen-* package

All packaging metadata lives in pyproject.toml at the repository root.
The subject accepts a .whl, so an sdist-only build is sufficient:

```bash
python3 -m pip install --upgrade build
python3 -m build -w
```

The artifact will appear in dist/ as:
- mazegen- < version > .whl

### Core Modules

#### 1. MazeGenerator Class

The primary entry point is the MazeGenerator class. It manages the grid state, generation logic, and solution pathfinding.

**Instantiation**
You can instantiate the generator in two ways: via configuration file or manual parameters.

***- Using a Configuration File (Recommended)***
This approach parses a text file (e.g., config.txt) to set up dimensions, entry/exit points, and seeds.
```bash
from mazegen import MazeGenerator

# Initialize using a path to a config file
# The maze is automatically generated/parsed based on the config
maze = MazeGenerator("config.txt")
```

***- Using Manual parameters***
For dynamic generation without external files.
```bash
from mazegen import MazeGenerator

maze = MazeGenerator(
    width=20,
    height=20,
    entry=(0, 0),        # (x, y)
    exit=(19, 19),       # (x, y)
    seed=None,           # Optional: int or str for reproducibility
    speed_animation=0.01 # Optional: Set 0 to disable animation
)
```

**Generating and Solving**
```bash
# 1. Generate the maze structure
maze.generate()

# 2. Solve the maze (calculates the path from Entry to Exit)
solution = maze.calculate_path() # Returns a list of coordinates (x, y) that form the shortest path
```
+ generate(): Populates the internal grid with walls/passages and 42_pattern.
+ calculate_path(): Returns the path (A list of coordinates).

**Accesing Data**
Once generated, you can access the raw data st
```bash
# Access the grid (List[List[int]])
# Values 0-15 represent bitmask walls (N=1, E=2, S=4, W=8)
grid_data = maze.get_grid()

# Access the solution path
# Returns a list of (row, col) tuples or path object
path_data = maze.get_path()
```

**Future Extensibility:**
```python
Easy to add new algorithms:
1. Implement generation logic in _generate_<algorithm>()
2. Add algorithm name to self.algorithm validation
3. Call gen.set_algorithm("<new_algo>") to switch at runtime
```

#### 2. Configuration Parser
**Configuration Schema Structure**

The `CONFIG_SCHEMA` global variable in `parsing.py` defines all valid configuration parameters:
```bash
CONFIG_SCHEMA = {
    'mandatory': {
        'WIDTH': "int",
        'HEIGHT': "int",
        'ENTRY': "tuple",
        'EXIT': "tuple",
        'OUTPUT_FILE': "file",
        'PERFECT': "bool"
    },
    'bonus': {
        'SEED': "int",
        'ANIMATION': "bool",
        'SPEED_ANIMATION': "float"
    }
}
```
+ `get_config_from_file()`: This function orchestrates file reading, parsing, and validation.
+ `parsing_config()`: This function accumulates all errors before raising, allowing users to fix multiple issues simultaneously

#### 3. Output Generation file
The Output Generation system is responsible for converting maze data from the internal grid representation into a persistent file format. This module provides encoding utilities and file writing functionality to serialize maze structures and their solutions to disk.

```python
from mazegen import generate_output

maze.generate()
maze.calculate_path()

generate_output(maze) # Generate the file.txt with the grid in hex and the path to solve
```

The generated output file follows a strict four-section format. Each section is separated by newlines, and the structure is designed for easy parsing.
```bash
# Maze Grid
D393953953
BC6C696C3A
851796D56A
AFAFABFFFA
AFEFA857FA
AFFFC2FFFA
853FBAFD52
AD6F86FFFA
A953C553D2
C47C555456

1,2 # Entry
8,9 # Exit
WSSSSSSSENEESEEEEE # Direction to solve the maze
```

#### 4. Terminal Visualization

Functions that generate the maze and solve it, but which demonstrate the process

```python
- render_maze(maze, show_path, wall_color, terminal)
- render_generation(maze, wall_color)
- render_solve(maze, color)
- render_path(maze, animated_path, color)
```

+ `render_maze(...)`: Generate a string describing the layout of the maze grid, you can print directly on the terminal with `terminal=True`

+ `render_generation(...)`: Run the generation algorithm (Perfect or Non-Perfect) and, at each step of the algorithm, clear the screen and redraw the maze, showing the expanding ‘front’ in yellow.

+ `render_solve(...)`: It shows how the solution algorithm explores the paths, highlighting the visited cells until it finds the exit

+ `render_path(...)`: Draws the path from start to finish instantly, or if “animated_path=True”, draws the path step by step, as if the user were navigating the maze.

*Example:*
```python
from mazegen import render_generation, render_solve, render_path, render_maze
while True:
        if maze.animation:
            if generate:
                render_generation(maze)
                render_solve(maze)
        else:
            if generate:
                maze.generate() # Generate maze without animation
                maze.calculate_path() #Generate solve without animation

        if show_path:
            render_path(maze, maze.animation and anim_path,
                                pallet[color_idx])
        render_maze(maze, terminal=True, show_path=show_path,
                            color=pallet[color_idx])
```

#### 5. Error Handling
The `MazeError` class is a custom exception that extends Python's built-in Exception class. It provides structured error reporting with support for both single error messages and aggregated multiple errors.

**Initialization and Attributes**
The `MazeError` constructor accepts two optional parameters:
| Parameter | Type           | Default | Description |
|-----------|----------------|---------|-------------|
| `prefix`  |`str` or `None` | None    | Primary error message or category
| `errors`  |`List[str]` or `None` | None    | List of specific error details

**The `__str__` method implements custom formatting logic:**

+ *Single Error Mode*: When the errors list is empty, only the prefix is returned

+ *Multiple Error Mode*: When the errors list contains items, each error is formatted as "{prefix}: {msg}." and joined with newlines
This creates a multi-line error message where each line follows the same pattern.

*Example:*
```python
try:
        maze = mazegen.MazeGenerator.maze_from_file(filename)
    except mazegen.MazeError as e:
        print(e) # Print formated text in diferrent lines the errors
        sys.exit()
```

---

## Team & Project Management

### Team Structure

| Member | Login | Role | Responsibilities |
|--------|-------|------|------------------|
| Carlos | cagil | **Configuration, Serialization, Solving & Visualization** | Config parsing, validation, file I/O, output encoding, pathfinding, integration & testing | ASCII renderer, integration & testing |
| Nacho | irivas-v | **Maze Engine & Documentation** | Algorithm implementation, constraint enforcement, integration & testing.

### Project Evolution

#### Initial Planning
- **Phase 1**: Core DFS algorithm with perfect maze generation
- **Phase 2**: Constraint enforcement (borders, entry/exit validation)
- **Phase 3**: Configuration system and I/O
- **Phase 4**: ASCII visualization and interaction
- **Phase 5**: Bonus features (animation, multiple colors)

#### What Actually Happened
1. **Phase 1-2**: Completed on schedule with clean algorithm implementation
2. **Phase 3**: Config parser required iteration on boolean parsing and tuple handling; added testing for edge cases
3. **Phase 4**: ASCII renderer evolved significantly—added multi-color support, junction rendering, and animation infrastructure
4. **Phase 5**: Algorithm switching and animation completed; step-by-step solvers added for visualization
5. **Integration Phase**: mazegen implementation pulled in; required type annotation, docstring fixes and API verification


### What Could Be Improved

+ **Configuration Validation**: Could add schema validation framework (e.g., Pydantic) for more robust parsing
+ **Performance**: Large mazes (>100×100) could benefit from parallel constraint checking
+ **Display Formats**: Only ASCII currently supported; JSON/image export would be a nice option
+ **GUI Alternative**: Terminal UI is functional but a graphical interface would be an improvement

### Tools & Technologies Used

| Tool | Purpose | Usage |
|------|---------|-------|
| **mypy** | Static type checking | Strict mode type safety verification |
| **flake8** | Code style linting | PEP 8 compliance (79-char lines) |
| **git** | Version control | Branch management, PR reviews |
| **Make** | Build automation | `make install`, `make run`, `make test`, `make lint` |
| **ANSI Colors** | Terminal rendering | 5-color palette for wall visualization |
| **termios** | Standard Python libraries for live keyboard event capturing

---

## References & Resources

### Maze Generation Algorithms
- [Maze Generation Algorithms (Wikipedia)](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Depth-First Search Maze](https://en.wikipedia.org/wiki/Depth-first_search)
- [Red Blob Games - Maze Generation](https://www.redblobgames.com/grids/intro/)

### Pathfinding Algorithms
- [Breadth-First Search (BFS)](https://en.wikipedia.org/wiki/Breadth-first_search)

### Technical Documentation
- [Python Type Hints (PEP 484)](https://www.python.org/dev/peps/pep-0484/)
- [Python Dataclasses](https://docs.python.org/3/library/dataclasses.html)
- [pytest Documentation](https://docs.pytest.org/)
- [ANSI Escape Codes](https://en.wikipedia.org/wiki/ANSI_escape_code)

### Code Style & Quality
- [PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/)
- [mypy Static Type Checker](https://www.mypy-lang.org/)
- [flake8 Linter](https://flake8.pycqa.org/)

### AI Usage

**AI** was used for the following tasks and components:

   - Documentation and README structuring
   - Code style and readability improvements (e.g. PEP 8 compliance)
   - Reviewing type annotations and static analysis feedback
   - Suggesting testing strategies and edge-case coverage.
   - Gaining a deeper understanding of concepts and examples.

All core project logic — maze generation algorithm, constraint enforcement, pathfinding, rendering logic, and overall architecture — was designed, implemented, and validated by the team.

