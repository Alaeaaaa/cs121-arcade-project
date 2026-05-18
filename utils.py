from constants import TILE_SIZE


def grid_to_pixels(i: int) -> int:
    # Convertit une coordonnée de grille vers le centre de la case en pixels.
    return i * TILE_SIZE + TILE_SIZE // 2