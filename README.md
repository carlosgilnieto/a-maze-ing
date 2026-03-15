
*This project has been created as part of the 42 curriculum by cagil, irivas-v.*

# A-Maze-ing: Procedural Maze Generation and Solving

## Description

**A-Maze-ing** is a maze generation and solving system developed as part of the
42 curriculum. The project focuses on maze generation, constraint enforcement
 (including the mandatory "42 stamp"), shortest-path solving, and
interactive ASCII visualization.

### Goals

- Generate perfect and imperfect mazes using procedural algorithms.
- Solve mazes using shortest-path pathfinding algorithms.
- Enforce structural constraints (borders, connectivity, mandatory 42 pattern).
- Provide an interactive, ANSI-colored ASCII visualization.

---

## Instructions

### Installation

```bash
# Clone the repository
git clone <git@vogsphere-v2.42madrid.com:vogsphere/intra-uuid-a6b25f53-8883-48dc-ab00-ff88b3d642e0-7295009-cagil>
cd a-maze-ing

# Create a virtual environment and install the 'mazagen' package
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

### Configuration File Format

The maze is configured via a `KEY=VALUE` text file. Comments starting with `#` are ignored.

```
# Mandatory fields (required for all mazes)
WIDTH=20                    # Maze width in cells (must be > 0)
HEIGHT=15                   # Maze height in cells (must be > 0)
ENTRY=0,0                   # Entry point coordinates (x,y)
EXIT=19,14                  # Exit point coordinates (x,y)
OUTPUT_FILE=maze.txt        # Output file path for hexadecimal maze
PERFECT=True                # True for perfect maze (no loops) False for imperfect

# Bonus fields (optional, have sensible defaults)
SEED=42                     # Random seed (default: 42; use empty/None to disable)
ANIMATION=True              # Enables live terminal animations
SPEED_ANIMATION=0.01        # Delay in seconds between frames (e.g., 0.01)

# Comments are supported (lines starting with #)
# Empty lines are ignored
```

**Example Configuration:**

```
WIDTH=020
HEIGHT=15
ENTRY=0,1
EXIT=19,14
OUTPUT_FILE=output_maze.txt
PERFECT=True
SEED=42 # Optional
ANIMATION=True # Optional but need SPEED_ANIMATION
SPEED_ANIMATION=0.01 # Optional but need ANIMATION
```

### Interactive Commands

Once the maze is displayed, the following commands are available:

| Command | Action |
|---------|--------|
| `1` | Regenerate maze (creates a new maze with current config/seed)
| `2` | Toggle solution path display |
| `3` | Change colors (Cycles circularly through the available ANSI color palettes)
| `4` | Toggle solver animation (BFS pathfinding with step-by-step visualization) |

## Algorithms & Constraint Enforcement

### Chosen Algorithm: DFS (Depth-First Search) with Backtracking

DFS was chosen as the primary generation algorithm because:

1. **Simplicity & Memory Efficiency**:Runs smoothly using an iterative stack approach.
2. **Perfect Maze Generation**: Guarantees a perfect maze (no loops, all cells connected).
3. **Visual Appeal**: Naturally generates mazes with long, winding corridors which makes them challenging and visually striking.
4. **Animation-Friendly**: Easily yields step-by-step states for terminal visualization.

## Imperfect Mazes

If `PERFECT=False` is set in the configuration, the engine first generates a perfect DFS maze and then randomly destroys ~25% of the remaining walls, creating multiple valid paths and closed loops.

## Solving Algorithm: BFS (Breadth-First Search)

The system uses BFS for pathfinding. Unlike DFS, BFS guarantees finding the shortest possible path between the entry and the exit, exploring the maze level by level radially.

---

## Constraint Enforcement (The "42" Stamp)

After validating sizes, mazes are enhanced with the mandatory pattern:

- For grids of at least `9x7`, an immutable **'42' pattern** is embedded in the center.
- The coordinates of the pattern are protected (`self.__protected`) to ensure that neither the DFS nor the imperfect wall-breaker algorithms destroy the structural integrity of the numbers

---

## Reusable Code Architecture

The reusable component required by Chapter VI is the standalone Python module
`mazegen.py`, which is packaged as `mazegen-1.0.0.tar.gz` and located at the
root of the repository. This module can be installed independently via pip:

```bash
pip install ./mazegen-1.0.0.tar.gz
```

### Short Documentation (required by subject)

**Instantiate and use the generator (basic example):**

```python
from mazegen import MazeGenerator

# Initialize the generator directly
gen = MazeGenerator(width=20, height=15, entry=(0,0), exit=(19,14), perfect=True)

# Generate and solve
maze_grid = gen.generate()
path = gen.calculate_path()

# Uses the Factory Method to parse the file and instantiate the object
maze = MazeGenerator.maze_from_file("config.txt")
```

**Instantiate from a config file**

- width, height: maze dimensions (int)
- seed: int or None (None => random)
- perfect: bool (True => perfect maze; False => may create loops)
- Animation: bool
- Speed Animation: float (used when Animation=True)

**Access the generated structure and a solution:**

- maze.width, maze.height
- maze.cells[y][x]: int bitmask in 0..15
  (Bits: N=1, E=2, S=4, W=8; bit set => wall is CLOSED)
- maze.omitted_42 and maze.stamp42 (if present)
- path is a list of moves like ["N", "E", ...]
- maze.get_grid(): Returns the 2D matrix of integers (0-15 bitmasks).
- maze.get_path(): Returns the list of (x, y) tuples forming the shortest path.
- maze.width, maze.height: Access dimensions.

### Building the mazegen-* package

All packaging metadata lives in pyproject.toml at the repository root.
The subject accepts a .tar.gz, so an sdist-only build is sufficient:

```bash
python3 -m pip install --upgrade build
python3 -m build --sdist
```

The artifact will appear in dist/ as:
- mazegen-<version>.tar.gz

### Core Modules

#### 1. **mazegen.py** - Maze Generation Engine
**Highly Reusable**: Multi-algorithm support with pluggable architecture

```python
gen = MazeGenerator(width=20, height=20, seed=42, perfect=True, algorithm="dfs")
maze = gen.generate(entry=(0,0), exit=(19,19))
path = gen.solve(maze, entry=(0,0), exit=(19,19))
```

**Reusable Components:**
<!-- - Algorithm switching: `gen.set_algorithm("prim")` → regenerate with different algorithm
- Step-by-step generation: `gen.iter_generation_steps(entry, exit)` → yields intermediate mazes for animation
- Step-by-step solving: `gen.solve_bfs_steps()` → yields solver frontier for visualization
- Constraint validation: Built-in 42 stamp, border, and connectivity checks -->

**Future Extensibility:**
```python
# Easy to add new algorithms:
# 1. Implement generation logic in _generate_<algorithm>()
# 2. Add algorithm name to self.algorithm validation
# 3. Call gen.set_algorithm("<new_algo>") to switch at runtime
```

<!-- #### 2. **config.py** - Configuration Parser
**Reusable**: Generic KEY=VALUE parser with type validation

```python
cfg = load_config("config.txt")
# cfg.width, cfg.height, cfg.entry, cfg.exit, cfg.algorithm, etc.
```

**Reusable Components:**
- Parser helper functions: `_parse_int()`, `_parse_bool()`, `_parse_coord()`, `_parse_density()`
- Validation logic easily adapted for other 42 projects using configuration files
- Type conversion with clear error messages

#### 3. **serializer.py** - Maze Encoding/Output
**Reusable**: Hexadecimal maze format with validation

```python
write_output_file("maze.txt", maze, entry, exit, path)
# Produces 42-compatible hexadecimal maze format
```

**Reusable Components:**
- Maze-to-hex encoding (4-bit wall bitmask per cell)
- Path encoding as direction strings (N/S/E/W)
- Output validator for format verification

#### 4. **renderer_ascii.py** - Terminal Visualization
**Reusable**: Modular animation system with color support

```python
renderer = AsciiRenderer()
renderer.run(maze, path, gen, cfg)
```

**Reusable Components:**
- `_draw_maze()`: Renders maze with walls, entry, exit, path, visited/frontier visualization
- Animation speed control: `self.animation_speed` (adjustable)
- Color cycling system: 5 configurable ANSI colors
- Solver animation with visited/frontier tracking
- Generation animation with step-by-step rendering -->

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

⚠️ **Configuration Validation**: Could add schema validation framework (e.g., Pydantic) for more robust parsing
⚠️ **Performance**: Large mazes (>100×100) could benefit from parallel constraint checking
⚠️ **Display Formats**: Only ASCII currently supported; JSON/image export would be a nice option
⚠️ **GUI Alternative**: Terminal UI is functional but a graphical interface would be an improvement

### Tools & Technologies Used

| Tool | Purpose | Usage |
|------|---------|-------|
| **mypy** | Static type checking | Strict mode type safety verification |
| **flake8** | Code style linting | PEP 8 compliance (79-char lines) |
| **git** | Version control | Branch management, PR reviews |
| **Make** | Build automation | `make install`, `make run`, `make test`, `make lint` |
| **Dataclasses** | Immutable config objects | Frozen `Config` for type-safe configuration |
| **ANSI Colors** | Terminal rendering | 5-color palette for wall visualization |
| **termios / tty** | Standard Python libraries for live keyboard event capturing

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

All core project logic — maze generation algorithms, constraint enforcement, pathfinding, rendering logic, and overall architecture — was designed, implemented, and validated by the team.
