import sys
from mazegen import MazeGenerator, render_maze, Color


def main():
    
    n = len(sys.argv)
    if n != 2:
        print("\033[31mrun: python3 a_maze_ing.py \"file_name\"\033[0m")
        sys.exit()

    filename = sys.argv[1]
    maze = MazeGenerator(filename)
    maze.generate_maze()
    while True:
        # print(render_maze(maze))
        maze.debug_print_state()
        print("=== A-Maze-ing ===")
        # print("1. Re-generate a new maze\n"
        #         "2. Show/Hide path from entry to exit\n"
        #         "3. Change maze colors\n"
        #         "4. Quit\n")
        option = input("Choise? (1-4):")
        if not option in ["1", "2", "3", "4"]:
                print("\033[31mSelect a valid option (1-4).\033[0m\n")
        else:
        #Queda meter que dependiendo de la opcion haga lo que corresponde
            if option == "1": # Regenerar el maze
                maze.generate_maze()
            elif option == "2": # Show/Hide path
                sys.exit()
            elif option == "3": # Cambiar color
                sys.exit()
            if option == "4":
                sys.stdout.write("\033[2J\033[3J\033[H\033[?25h")
                sys.exit()


if __name__ == "__main__":
    main()
