import sys
from typing import List, Dict, Any, Tuple, Callable
from .errors import MazeError

#variable global con el diccionario de KEY=VALUE aceptados
#Value en este caso es un str del tipo de valor que acepta
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
    }}


def get_config_from_file(directory: str) -> Dict[str, Any]:
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
    Mira que todos los valores del archivos, cumplan con lo que tienen que ser
    [NO COMPRUEBA SI ESTAN TODOS LOS VALORES NECESARIOS, SOLO EL TIPO DE VALOR]
    """
    error_list = []
    def check_value(key: str, value: str, data_type: str) -> Any:
        '''
        Funcion auxiliar para obtener los datos de cada valor
        '''
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
    #Junta los dos diccionarios para comprobar las KEYS validas
    params: Dict[str, str] = (CONFIG_SCHEMA['mandatory'] |
                              CONFIG_SCHEMA['bonus'])
    checked: List[str] = []
    txt = txt.split("\n")

    for num_line, line in enumerate(txt, 1):
        #Quita comentarios del archivo aunque esten dentras de una linea posible valida
        line = line.split('#')[0].strip()
        if not line:
            continue
        #Separa por "=" para comprobar que cumple la linea "KEY=VALUE"
        line = line.split("=")
        if len(line) != 2 or not line:
            error_list.append(f"Line {num_line} format must be 'KEY'='VALUE'")
        else:
            key = line[0]
            value = line[1]
            #Comprueba si ya esta guardado el key, es decir ya tengo un valor con ese Key
            if config.get(key, None) or key in checked:
                error_list.append(f"Line {num_line} '{key}' is duplicated")
                checked.append(key)
            #Compara si el nombre del key que se ha encontrado en la linea cuadra con los que se puede tener
            elif not any(key == line[0]
                         for key in params.keys()):
                error_list.append(f"Line {num_line} '{key}' "
                                   "is not a valid KEY")
            #Si no tengo ese key significa que me lo quedo
            else:
                try:
                    config[key] = check_value(key, value, params[key])
                except ValueError as e:
                    error_list.append(e)
                checked.append(key)
    #Si hay una minima linea mal imprime todos los errores que ha habido
    if (len(CONFIG_SCHEMA['mandatory']) > len(checked)):
        missing = [key
                   for key in CONFIG_SCHEMA['mandatory']
                   if key not in checked
                   ]
        missing = ", ".join(missing)
        error_list.append(f"Missing keys: {missing}")
    if len(error_list) > 0:
        raise MazeError("", error_list)
    else:
        return config


def check_params(config: Dict[str, Any]) -> bool:
    """
    Comprueba si todos los valores mandatory estan dentro del archivo
    """
    error_list = []
    required: List[str] = CONFIG_SCHEMA.get('mandatory').keys()
    missing: List = []
    for key in required:
        if config.get(key, None) is None:
            missing.append(key)
    if missing:
        missing = ", ".join(missing)
        error_list.append(f"Key missing ({missing})")
    else:
        return True
    raise MazeError("KEY ERROR", error_list)


def check_42_pattern(width: int, height: int) -> None:
    if width < 9 or height < 7:
        print("\033[33mWARNING: A maze will be generated "
              "WITHOUT ‘pattern 42’.\n"
              "Minimum size for print pattern: WIDTH=9, HEIGHT=7\033[0m")
        option = input("Continue? (y/n): ")
        if option != "y":
            sys.exit()
