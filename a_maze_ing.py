import sys
from mazegen import MazeGenerator, generate_output, render_solve, render_generation,render_path, render_maze, Color

def main():

    n = len(sys.argv)
    if n != 2:
        print("\033[31mrun: python3 a_maze_ing.py \"file_name\"\033[0m")
        sys.exit()
    filename = sys.argv[1]

    # # Manual Method
    # try:
    #     maze = MazeGenerator(10, 10, (1, 0), (8, 9) speed_animation=0.05)
    # except Exception:
    #     sys.exit()

    # File Method
    try:
        maze = MazeGenerator.maze_from_file(filename)
    except Exception:
        sys.exit()

    # render_generation(maze)
    # render_solve(maze)

    #Options
    msg = ""
    pallet = Color.get_pallete()
    color_idx = 0
    show_path = False
    anim_path = maze.animation
    generate = True # Flag para bloquear la generacion cuando cambia de color

    while True:
        if maze.animation:
            if generate:
                render_generation(maze)
                render_solve(maze)
        else:
            if generate:
                maze.generate()
                maze.calculate_path()
        if show_path:
            render_path(maze, maze.animation and anim_path, pallet[color_idx])
        render_maze(maze, terminal=True, show_path=show_path, color=pallet[color_idx])
        print("=== A-Maze-ing ===")
        print("[1]. Re-generate a new maze\n"
              f"[2]. {'Hide' if show_path else 'Show'} path from entry to exit\n"
              "[3]. Change maze colors\n"
              "[4]. Quit\n")
        option = input("\033[?25h" + msg + "Choise? (1-4):")
        options = ["1", "2", "3", "4"]
        try:
            option = options[int(option) - 1] # Solo por validar que es una opcion correcta
            msg = ""
            generate = False
            anim_path = False
            if option == "1": # Regenerar el maze
                generate = True
                anim_path = True
                pass
            elif option == "2":
                show_path = not show_path
                anim_path = True
            elif option == "3": # Cambiar color
                color_idx = (color_idx + 1) % len(pallet)
            elif option == "4":
                sys.stdout.write("\033[2J\033[3J\033[H\033[?25h")
                sys.exit()
        except (IndexError, ValueError):
            msg = "\033[31mSelect a valid option (1-5).\033[0m\n"
            generate = False
            anim_path = False


if __name__ == "__main__":
    main()
