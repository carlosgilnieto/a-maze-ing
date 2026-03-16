"""
Main controller for the A-Maze-ing project.

This script acts as the application's entry point.
It is responsible for validating command-line arguments, initialising
the maze-generation engine (mazegen) from a configuration file,
and managing the interactive event loop in the terminal.
"""

import sys

try:
    import mazegen
except ImportError:
    print("\033[31mFailed to import mazegen package run: make install\033[0m")
    sys.exit()


def main() -> None:
    """
    Main entry point of the A-Maze-ing programme.

    Reads the name of the configuration file from the command-line
    arguments, generates the maze and enters the interactive loop
    that allows the user to regenerate it, show/hide the solution path
    and change the wall colours.

    Raises:
        SystemExit: If exactly one argument is not provided or if
            the configuration file contains errors.
    """
    n = len(sys.argv)
    if n != 2:
        print("\033[31mrun: python3 a_maze_ing.py \"file_name\"\033[0m")
        sys.exit()
    filename = sys.argv[1]

    try:
        maze = mazegen.MazeGenerator.maze_from_file(filename)
    except mazegen.MazeError as e:
        print(f"\033[31m{e}\033[0m")
        sys.exit()

    # Options
    msg = ""
    pallet = mazegen.Color.get_pallete()
    color_idx = 0
    show_path = False
    anim_path = maze.animation
    generate = True
    while True:
        if maze.animation:
            if generate:
                mazegen.render_generation(maze)
                mazegen.render_solve(maze)
        else:
            if generate:
                maze.generate()
                maze.calculate_path()

        if show_path:
            mazegen.render_path(maze, maze.animation and anim_path,
                                pallet[color_idx])
        mazegen.render_maze(maze, terminal=True, show_path=show_path,
                            color=pallet[color_idx])

        mazegen.generate_output(maze)
        print("=== A-Maze-ing ===")
        print("[1]. Re-generate a new maze\n"
              f"[2]. {'Hide' if show_path else 'Show'} path from "
              "entry to exit\n"
              "[3]. Change maze colors\n"
              "[4]. Quit\n")

        option = input("\033[?25h" + msg + "Choise? (1-4):")
        options = ["1", "2", "3", "4"]

        try:
            index = int(option) - 1
            if index < 0:
                raise ValueError

            option = options[index]
            msg = ""
            generate = False
            anim_path = False

            if option == "1":
                generate = True
                anim_path = True
                pass
            elif option == "2":
                show_path = not show_path
                anim_path = True
            elif option == "3":
                color_idx = (color_idx + 1) % len(pallet)
            elif option == "4":
                sys.stdout.write("\033[2J\033[3J\033[H\033[?25h")
                sys.exit()
        except (IndexError, ValueError):
            msg = "\033[31mSelect a valid option (1-4).\033[0m\n"
            generate = False
            anim_path = False


if __name__ == "__main__":
    main()
