import sys
from typing import List, Dict, Any, Tuple

#Cambiar Docstrings
def print_error(msg: str, error_type="Error") -> None:
    """
    Imprimir errores que se vean
    """
    print(f"\033[41m{error_type}: {msg}.\033[0m")

#Cambiar Dosctrings
def errors(error_type: str) -> Dict[str, callable]:
    """
    Guarda un registro de errores, Creo que es sobre todo con lo relacionado en
    el parseo, ya que se pueden tener varios errores en el propio archivo
    """
    mem = []

    def add_error(msg: str) -> None:
        mem.append(msg)

    def len_error() -> int:
        return len(mem)

    def print_all() -> None:
        for e in mem:
            print_error(e, error_type)
        mem.clear()

    return {'add': add_error,
            'len': len_error,
            'print': print_all}


def open_file(file: str) -> str:
    """
    Abre el archivo y devuelve lo abierto
    """
    try:
        with open(file) as f:
            config = f.read
        return config
    except FileNotFoundError:
        print_error(f"'{file}' does not exist in the directory")
        sys.exit()


def parsing_config(txt: str, all_params: Dict[str, Dict]) -> Dict[str, Any]:
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
                raise ValueError(f"{key}: Is not a valid int")
        elif data_type == "tuple":
            values = value.split(",")
            if len(values) > 2:
                # errors['add'](f"{key} must Only 2 int (int, int)")
                raise ValueError(f"{key}: Only 2 int (int, int)")
            return tuple((int(values[0]), int(values[1])))
        elif data_type == "bool":
            if value == "True":
                return True
            elif value == "False":
                return False
            else:
                # errors['add'](f"{key}: Is not a bool")
                raise ValueError(f"{key}: Is not a bool")
        elif data_type == "file":
            extend = value.split(".")
            file_name: str = extend[0]
            if (extend[len(extend) - 1] != "txt"
                or not file_name.strip()
                    or len(extend) < 2):
                raise ValueError(f"{key}: Is not a valid .txt file")
                # errors['add'](f"{key}: Is not a valid .txt file")
            return value
        else:
            # errors['add'](f"{data_type} has not support")
            raise ValueError(f"{data_type} has not support")
        
        #Gestor de errores
    pars_errors = errors("Parsing File")
    val_errors = errors("Value Error")

    config: Dict[str: Any] = {}
    #Junta los dos diccionarios para comprobar las KEYS validas
    params: Dict[str: str] = (all_params.get('mandatory')
                              | all_params.get('bonus'))
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
    if pars_errors['len']() > 0 or val_errors['len']() > 0:
        pars_errors['print']()
        val_errors['print']()
        sys.exit()
    else:
        #FALTA COMPROBAR LOS PARAMETROS MANDATORY
        return config
    
def check_config(config: Dict[str, Any], params: Dict) -> bool:
    """
    Comprueba si todos los valores necesarios estan dentro del archivo
    """
    required: List[str] = params.get('mandatory').keys()
    missing: List = []
    for key in required:
        if not config.get(key, None):
            missing.append(key)
    if missing:
        missing = ", ".join(missing)
        raise ValueError(f"Key missing ({missing})")
    else:
        #Comprueba si ENTRY y EXIT son distintos
        if config.get('ENTRY', None) == config.get('EXIT', None):
            raise ValueError("The value of ENTRY and EXIT must be different")
        for key in ['ENTRY', 'EXIT']:
            pos: Tuple = config.get(key, None) # Recoge el valor de la config
            #Comprueba que es los parametros de entry and exit esten dentro del tamaño del laberinto
            if ((pos[0] >= config.get('WIDTH', None) or pos[0] < 0) or
                    (pos[1] >= config.get('HEIGHT', None) or pos[1] < 0)):
                raise ValueError(f"{key}({pos[0]}, {pos[1]}) "
                                 "must be between (>0, >0) and "
                                 f"(<{config['WIDTH']}, <{config['HEIGHT']})")
        return True
