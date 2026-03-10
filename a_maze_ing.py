import sys
from mazegen import MazeGenerator, animated_path, render_maze, Color


def main():
    
    n = len(sys.argv)
    if n != 2:
        print("\033[31mrun: python3 a_maze_ing.py \"file_name\"\033[0m")
        sys.exit()

    filename = sys.argv[1]
    maze = MazeGenerator(filename)
    grid = maze.generate_maze()
    path = maze.solve_maze()

    #Options
    msg = ""
    pallet = Color.get_pallete()
    color_idx = 0
    show_path = True
    anim_path = False
    aux_anim = True

    while True:
        if show_path and anim_path and aux_anim:
            animated_path(maze, path, pallet[color_idx])
        else:
            print(render_maze(maze, show_path, pallet[color_idx]))
        print("=== A-Maze-ing ===")
        print("[1]. Re-generate a new maze\n"
              f"[2]. {'Hide' if show_path else 'Show'} path from entry to exit\n"
              f"[3]. {'OFF' if anim_path else 'ON'} path animation\n"
              "[4]. Change maze colors\n"
              "[5]. Quit\n")
        option = input("\033[?25h" + msg + "Choise? (1-5):")
        options = ["0", "1", "2", "3", "4", "5"]
        if not option == options[int(option)]:
                msg = "\033[31mSelect a valid option (1-5).\033[0m\n" 
        else:
        #Queda meter que dependiendo de la opcion haga lo que corresponde
            msg = ""
            if option == "0":
                msg = "\033[31mSelect a valid option (1-5).\033[0m\n" 
            if option == "1": # Regenerar el maze
                maze.generate_maze()
                path = maze.solve_maze()
                aux_anim = True
            elif option == "2": # Show/Hide path
                show_path = not show_path
                if not show_path:
                    anim_path = False
            elif option == "3":
                if show_path:
                    anim_path = not anim_path
                else:
                    msg = "\033[31mFirst activate 'show path' with option 2.\033[0m\n"
            elif option == "4": # Cambiar color
                aux_anim = False
                color_idx = (color_idx + 1) % len(pallet)
            if option == "5":
                sys.stdout.write("\033[2J\033[3J\033[H\033[?25h")
                sys.exit()


if __name__ == "__main__":
    main()
