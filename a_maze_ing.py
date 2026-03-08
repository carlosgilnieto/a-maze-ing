import sys
from mazegen import MazeGenerator
from mazegen.parsing import check_config, parsing_config, get_config_file
from typing import List, Dict, Any, Tuple


def main():
    
    mandatory_params = {'WIDTH': "int",
                        'HEIGHT': "int",
                        'ENTRY': "tuple",
                        'EXIT': "tuple",
                        'OUTPUT_FILE': "file",
                        'PERFECT': "bool"}

    bonus_params = {"SEED": "int"}

    params = {'mandatory': mandatory_params,
              'bonus': bonus_params}

    config_file = get_config_file()
    if config_file:
        try:
            with open(config_file) as f:
                config = f.read()
            pars_cfg: Dict[str, Any] = parsing_config(config,
                                                      params)
            #print("Config:")
            #for key, val in pars_cfg.items():
            #    print(f"    {key} -> {val}")
            if check_config(pars_cfg, params):
                maze_gen = MazeGenerator(pars_cfg)
                #maze_gen.check_maze(maze_gen.visited, True)
                maze_gen.generate_maze()
                maze_gen.debug_print_state()
        except FileNotFoundError:
            print(f"'{config_file}' does not exist in the directory")
            sys.exit()
        except ValueError as e:
            print(e)
            sys.exit()

if __name__ == "__main__":
    main()
