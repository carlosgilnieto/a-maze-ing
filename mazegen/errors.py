class MazeError(Exception):
    def __init__(self, prefix="ERROR", errors=None):
        self.prefix = prefix
        self.errors = errors if errors is not None else []
        super().__init__(self.prefix)
    
    def __str__(self) :
        if not self.errors:
            return self.prefix
        formated_msg = [f"{self.prefix}: {msg}."
                        for msg in self.errors]
        return "\n".join(formated_msg)


#Cambiar Docstrings
def print_error(msg: str, error_type="Error") -> None:
    """
    Imprimir errores que se vean
    """
    print(f"\033[31m{error_type}: {msg}.\033[0m")
