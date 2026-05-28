from map import GridCell, Map
from constants import TILE_SIZE


def grid_to_pixels(i: int) -> int:
    return i * TILE_SIZE + TILE_SIZE // 2

def is_inside_map(game_map: Map, x: int, y: int) -> bool:
    return 0 <= x < game_map.width and 0 <= y < game_map.height

def find_cells(game_map: Map, target: GridCell) -> list[tuple[int, int]]:
    # cette fonction trouve toutes les cases d'un certain type dans la map
    return [
        (x, y)
        for y in range(game_map.height)
        for x in range(game_map.width)
        if game_map.get(x, y) == target
    ]
