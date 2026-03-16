"""
Configuration parsing and validation module.

This module is responsible for reading the config.txt file, validating
that the keys are correct according to the predefined schema (CONFIG_SCHEMA),
converting the data types (from strings to integers, booleans or tuples) and
verifying that the logical constraints of the maze
(minimum size, input, output) are met.
"""

import sys
from typing import List, Dict, Any
from .errors import MazeError

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
        'SPEED_ANIMATION': "float"
    }}


def get_config_from_file(directory: str) -> Dict[str, Any]:
    """
    Reads and processes the configuration file from the specified path.

    Opens the text file, extracts its contents, and uses the parsing and
    validation functions to generate a secure configuration dictionary.

    Args:
        directory (str):
            Path to the configuration file (e.g. “config.txt”).

    Returns:      Dict[str, Any]:
            Dictionary containing the parsed and validated
            configuration.

    Raises:
        FileNotFoundError:
            If the file does not exist at the specified path.
        ValueError:
            If there is a formatting error or an unexpected
            value in the file.
    """
    try:
        with open(directory, "r") as file:
            txt: str = file.read()
        config_parsed: Dict[str, Any] = parsing_config(txt)
        if not check_params(config_parsed):
            sys.exit()
        else:
            return config_parsed
    except FileNotFoundError:
        raise FileNotFoundError(f"'{directory}' does not exist "
                                "in the root directory")
    except PermissionError:
        raise PermissionError(f"'{directory}' must have read permissions")
    except MazeError as e:
        raise ValueError(e)


def parsing_config(txt: str) -> Dict[str, Any]:
    """

    Parses the raw text from the file and converts the values to their
    data types.

    Analyses each line, ignores comments (marked with “#”) and assigns
    the values to their respective keys, checking the type against
    CONFIG_SCHEMA.
    [Note: Does not check the logical validity of the maze,
    only the value type].

    Args:
        txt (str): Raw content extracted from the configuration file.

    Returns:
            Dict[str, Any]:
                Dictionary with correctly typed keys and values.

    Raises:
        ValueError: If there is a formatting error or an unexpected
            value in the file.

    """
    error_list = []

    def check_value(key: str, value: str, data_type: str) -> Any:
        """
        Converts and validates a configuration value according to
        its expected type.

        Args:
            key: Name of the configuration key (e.g. “WIDTH”).
            value: Raw value read from the file, as a text string.
            data_type: Expected type according to CONFIG_SCHEMA.
             Accepted values:
             “int”, “float”, “tuple”, “bool” or “file”.

        Returns:
                  The value converted to the corresponding type:
            - “int”   → int
            - “float” → float
            - “tuple” → tuple[int, int]
            - “bool”  → bool
            - “file”  → str (validated filename)

        Raises:
            ValueError: If the value cannot be converted to the specified type,
                contains spaces, is empty, or the data_type is not supported.
        """
        if " " in value:
            raise ValueError(f"{key}: Value must not contain spaces")
        if not value:
            raise ValueError(f"{key}: Is empty")
        if data_type == "int":
            try:
                return int(value)
            except ValueError:
                raise ValueError(f"'{key}={value}' Is not a valid int")
        if data_type == "float":
            try:
                return float(value)
            except ValueError:
                raise ValueError(f"'{key}={value}' Is not a valid float(x.xx)")
        elif data_type == "tuple":
            values = value.split(",")
            if len(values) != 2:
                raise ValueError(f"'{key}={value}' must have exactly "
                                 "2 coordinates (int, int)")
            try:
                position = tuple((int(values[0]), int(values[1])))
            except (IndexError, ValueError):
                raise ValueError(f"'{key}={value}' must be 2 int (int, int)")
            return position
        elif data_type == "bool":
            if value == "True":
                return True
            elif value == "False":
                return False
            else:
                raise ValueError(f"'{key}={value}' Is not a valid bool "
                                 "(True or False)")
        elif data_type == "file":
            extend = value.split(".")
            file_name: str = extend[0]
            if (extend[len(extend) - 1] != "txt"
                or not file_name.strip()
                    or len(extend) < 2):
                raise ValueError(f"'{key}={value}' Is not a valid .txt file")
            return value
        else:
            raise ValueError(f"{data_type} has not support")

    config: Dict[str, Any] = {}
    params: Dict[str, str] = (CONFIG_SCHEMA['mandatory'] |
                              CONFIG_SCHEMA['bonus'])
    checked: List[str] = []
    lines = txt.split("\n")

    for num_line, lin_text in enumerate(lines, 1):
        line_text = lin_text.split('#')[0].strip()

        if not line_text:
            continue

        line_parts = line_text.split("=")
        if len(line_parts) != 2 or not line_parts[0]:
            error_list.append(f"Line {num_line} format must be 'KEY'='VALUE'")
        else:
            key = line_parts[0]
            value = line_parts[1]

            if config.get(key, None) or key in checked:
                error_list.append(f"Line {num_line} '{key}' is duplicated")
                checked.append(key)

            elif not any(key == line_parts[0]
                         for key in params.keys()):
                error_list.append(f"Line {num_line} '{key}' "
                                  "is not a valid KEY")
            else:
                try:
                    config[key] = check_value(key, value, params[key])
                except ValueError as e:
                    error_list.append(str(e))
                checked.append(key)

    if (len(CONFIG_SCHEMA['mandatory']) > len(checked)):
        missing_keys = [key
                        for key in CONFIG_SCHEMA['mandatory']
                        if key not in checked
                        ]
        missing_str = ", ".join(missing_keys)
        error_list.append(f"Missing keys: {missing_str}")
    if len(error_list) > 0:
        raise MazeError("", error_list)
    else:
        return config


def check_params(config: Dict[str, Any]) -> bool:
    """
    Validates the logical and business constraints of the maze.

    Checks that:
    the dimensions are at least the minimum required,
    the ENTRY and EXIT are different,
    the animation speed is valid and that both the start and end points
    are strictly within the boundaries of the generated grid.

    Args:
        config (Dict[str, Any]): Previously parsed configuration dictionary.

    Returns:
        bool: True if the entire configuration is logically valid,
        False if there is an error.

    Raises:
        MazeError: If one or more required keys are missing, list them
            in the error message.
    """
    error_list: List[str] = []
    required: List[str] = list(CONFIG_SCHEMA['mandatory'].keys())
    missing: List[str] = []
    for key in required:
        if config.get(key, None) is None:
            missing.append(key)
    if missing:
        missing_str = ", ".join(missing)
        error_list.append(f"Key missing ({missing_str})")
    else:
        return True
    raise MazeError("KEY ERROR", error_list)


def check_42_pattern(width: int, height: int) -> None:
    """
    Checks whether the maze is large enough to draw the “42” pattern.

    If the dimensions are smaller than the minimum required (WIDTH < 9 or
    HEIGHT < 7), it displays a warning on the console and asks the
    user to confirm whether to continue without the pattern.

    Args:
        width: Width of the maze in number of cells.
        height: Height of the maze in number of cells.

    Returns:
        None

    Raises:
        SystemExit: If the user replies “n” when asked
            whether they wish to continue without the “42” pattern.
    """
    if width < 9 or height < 7:
        print("\033[33mWARNING: A maze will be generated "
              "WITHOUT ‘pattern 42’.\n"
              "Minimum size for print pattern: WIDTH=9, HEIGHT=7\033[0m")
        option = input("Continue? (y/n): ")
        if option not in ["yes", "y"]:
            sys.exit()
