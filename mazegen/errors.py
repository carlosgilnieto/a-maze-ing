
#Cambiar Docstrings
def print_error(msg: str, error_type="Error") -> None:
    """
    Imprimir errores que se vean
    """
    print(f"\033[31m{error_type}: {msg}.\033[0m")

#Cambiar Dosctrings
def error(error_type: str) -> dict[str, callable]:
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