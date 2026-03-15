from typing import List


class MazeError(Exception):
    """
    Custom exception for maze generation and validation errors.

    Allows multiple error messages to be grouped into a single exception,
    displaying them all together with an identifying prefix.

    Attributes:
        prefix: Error title or category (e.g. "KEY ERROR").
        errors: List of individual error messages.

    Example:
        >>> raise MazeError("CONFIG ERROR", ["WIDTH is missing",
        "HEIGHT is missing"])
        CONFIG ERROR: WIDTH is missing.
        CONFIG ERROR: HEIGHT is missing.
    """
    def __init__(self, prefix: str = "",
                 errors: list[str] | None = None) -> None:
        """
        Initialises MazeError with a prefix and a list of errors.

        Args:
            prefix:
                Error title or category. Default is an empty string.
            errors:
                List of individual error messages. Default is an
                empty list.
        """
        self.prefix: str = prefix
        self.errors: List[str] = errors if errors is not None else []
        super().__init__(self.prefix)

    def __str__(self) -> str:
        """
        Returns a text representation of all errors.

        Returns :
            If there are no errors, returns only the prefix. If there
            are errors, returns each message on a separate line in the format
            'prefix: message.'
        """
        if not self.errors:
            return self.prefix
        formated_msg = [f"{self.prefix}: {msg}."
                        for msg in self.errors]
        return "\n".join(formated_msg)


def print_error(msg: str, error_type: str = "Error") -> None:
    """
    Imprimir errores que se vean
    """
    print(f"\033[31m{error_type}: {msg}.\033[0m")
