import sys
try:
    import mazegen
except ImportError:
    print("\033[31mFailed to import mazegen package run: make install\033[0m")

def main() -> None:

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

    #Options
    msg = ""
    pallet = mazegen.Color.get_pallete()
    color_idx = 0
    show_path = False
    anim_path = maze.animation
    generate = True # Flag para bloquear la generacion cuando cambia de color

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
            mazegen.render_path(maze, maze.animation and anim_path, pallet[color_idx])
        mazegen.render_maze(maze, terminal=True, show_path=show_path, color=pallet[color_idx])
        mazegen.generate_output(maze)
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
            msg = "\033[31mSelect a valid option (1-4).\033[0m\n"
            generate = False
            anim_path = False


if __name__ == "__main__":
    main()
