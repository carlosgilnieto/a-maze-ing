import sys
from mazegen import MazeGenerator


def main():
    
    n = len(sys.argv)
    if n != 2:
        print("\033[31mrun: python3 a_maze_ing.py \"file_name\"\033[0m")
        sys.exit()

    filename = sys.argv[1]
    maze = MazeGenerator(filename)
    maze.generate_maze()


if __name__ == "__main__":
    main()
