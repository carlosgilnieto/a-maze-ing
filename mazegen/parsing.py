import sys
from typing import List, Dict, Any, Tuple
from .errors import error, print_error

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
        'SEED': "int"
    }}


def get_config_from_file(directory: str) -> Dict[str, Any]:
    try:
        with open(directory) as file:
            txt: str = file.read()
        config_parsed: Dict[str, Any] = parsing_config(txt)
        if not check_required(config_parsed):
            sys.exit()
        else:
            return config_parsed
    except FileNotFoundError:
        raise FileNotFoundError(f"'{directory}' does not exist in the directory")
    except ValueError as e:
        raise ValueError(e)


def parsing_config(txt: str) -> Dict[str, Any]:
    """
    Mira que todos los valores del archivos, cumplan con lo que tienen que ser
    [NO COMPRUEBA SI ESTAN TODOS LOS VALORES NECESARIOS, SOLO EL TIPO DE VALOR]
    """

    def check_value(key: str, value: str, data_type: str) -> Any:
        '''
        Funcion auxiliar para obtener los datos de cada valor
        '''
        if not value:
            # errors['add'](f"{key} is empty")
            raise ValueError(f"{key}: Is empty")
        if data_type == "int":
            try:
                return int(value)
            except ValueError:
                # errors['add'](f"{key} is not a valid int")
                raise ValueError(f"'{key}={value}' Is not a valid int")
        elif data_type == "tuple":
            values = value.split(",")
            if len(values) > 2:
                # errors['add'](f"{key} must Only 2 int (int, int)")
                raise ValueError(f"'{key}={value}' must be 2 int (int, int)")
            return tuple((int(values[0]), int(values[1])))
        elif data_type == "bool":
            if value == "True":
                return True
            elif value == "False":
                return False
            else:
                # errors['add'](f"{key}: Is not a bool")
                raise ValueError(f"'{key}={value}' Is not a valid bool")
        elif data_type == "file":
            extend = value.split(".")
            file_name: str = extend[0]
            if (extend[len(extend) - 1] != "txt"
                or not file_name.strip()
                    or len(extend) < 2):
                raise ValueError(f"'{key}={value}' Is not a valid .txt file")
                # errors['add'](f"{key}: Is not a valid .txt file")
            return value
        else:
            # errors['add'](f"{data_type} has not support")
            raise ValueError(f"{data_type} has not support")

        #Gestor de errores
    pars_errors = error("Parsing File")
    val_errors = error("Value Error")

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
            pars_errors['add'](f"Line {num_line} format must be 'KEY'='VALUE'")
        else:
            key = line[0]
            value = line[1]
            #Comprueba si ya esta guardado el key, es decir ya tengo un valor con ese Key
            if config.get(key, None) or key in checked:
                pars_errors['add'](f"Line {num_line} '{key}' is duplicated")
                checked.append(key)
            #Compara si el nombre del key que se ha encontrado en la linea cuadra con los que se puede tener
            elif not any(key == line[0]
                         for key in params.keys()):
                pars_errors['add'](f"Line {num_line} '{key}' "
                                   "is not a valid KEY")
            #Si no tengo ese key significa que me lo quedo
            else:
                try:
                    config[key] = check_value(key, value, params[key])
                except Exception as e:
                    val_errors['add'](e)
                checked.append(key)
    #Si hay una minima linea mal imprime todos los errores que ha habido
    if (len(CONFIG_SCHEMA['mandatory']) > len(checked)):
        missing = [key
                   for key in CONFIG_SCHEMA['mandatory']
                   if key not in checked
                   ]
        missing = ", ".join(missing)
        pars_errors['add'](f"Missing keys: {missing}")
    if pars_errors['len']() > 0 or val_errors['len']() > 0:
        pars_errors['print']()
        val_errors['print']()
        sys.exit()
    else:
        return config


def check_required(config: Dict[str, Any]) -> bool:
    """
    Comprueba si todos los valores mandatory estan dentro del archivo
    """
    required: List[str] = CONFIG_SCHEMA.get('mandatory').keys()
    missing: List = []
    for key in required:
        if config.get(key, None) is None:
            missing.append(key)
    if missing:
        missing = ", ".join(missing)
        raise ValueError(f"Key missing ({missing})")
    else:
        #Comprueba que se pueda imprimir el patron 42
        # if config.get('WIDTH') < 9 or config.get('HEIGHT') < 8:
        #     print("\033[33mWARNING: A maze will be generated WITHOUT ‘pattern 42’.\n"
        #           "Minimum size: WIDTH=8, HEIGHT=7\033[0m")
        #     option = input("Continue? (y/n): ")
        #     if option != "y":
        #         sys.exit()
        if config.get('WIDTH') < 1:
            raise ValueError("Recomended minimun size: WIDTH=2")
        if config.get('HEIGHT') < 1:
            raise ValueError("Recomended minimun size: HEIGHT=2")
        #Comprueba si ENTRY y EXIT son distintos
        if config.get('ENTRY', None) == config.get('EXIT', None):
            raise ValueError("The value of ENTRY and EXIT must be different")
        #Comprueba si ENTRY Y EXIT están dentro del laberinto
        for key in ['ENTRY', 'EXIT']:
            pos: Tuple = config.get(key, None) # Recoge el valor de la config
            #Comprueba que es los parametros de entry and exit esten dentro del tamaño del laberinto
            if ((pos[0] >= config.get('WIDTH', None) or pos[0] < 0) or
                    (pos[1] >= config.get('HEIGHT', None) or pos[1] < 0)):
                raise ValueError(f"{key}({pos[0]}, {pos[1]}) "
                                 "must be between (0, 0) and "
                                 f"(<{config['WIDTH']}, <{config['HEIGHT']})")
        return True


def check_42_pattern(width: int, height: int) -> None:
    if width < 9 or height < 8:
        print("\033[33mWARNING: A maze will be generated "
              "WITHOUT ‘pattern 42’.\n"
              "Minimum size: WIDTH=8, HEIGHT=7\033[0m")
        option = input("Continue? (y/n): ")
        if option != "y":
            sys.exit()
