
def generate_maze(self):
    # 1. Mapeo de direcciones y paredes (usando sistema de bits)
    # Asumiendo los bits estándar: Norte=1, Este=2, Sur=4, Oeste=8
    # Formato: (DesplX, DesplY, Pared a romper en celda actual,
    #           pared a romper en la vecina)
    DIRECTIONS = [
            (0, -1, 1, 4),  # Norte
            (1, 0, 2, 8),   # Este
            (0, 1, 4, 1),   # Sur
            (-1, 0, 8, 2)   # Oeste
        ]

    # 2. Celda de inicio (para empezar en 0,0) a construir el laberinto
    # Usar random?? para que sea aleatorio
    start_x, start_y = 0, 0
    self.visited[start_y][start_x] = True