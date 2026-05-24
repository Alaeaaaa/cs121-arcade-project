from map import GridCell, Map
from constants import TILE_SIZE


def grid_to_pixels(i: int) -> int:
    # Convertit une coordonnée de grille vers le centre de la case en pixels.
    return i * TILE_SIZE + TILE_SIZE // 2


def find_cells(game_map: Map, target: GridCell) -> list[tuple[int, int]]:
    # Trouve toutes les cases d'un certain type dans la map.
    return [
        (x, y)
        for y in range(game_map.height)
        for x in range(game_map.width)
        if game_map.get(x, y) == target
    ]