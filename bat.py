from __future__ import annotations

from dataclasses import dataclass
import math
import random

from constants import TILE_SIZE
from map import GridCell, Map


# ==================================================
# Constantes des chauves-souris
# ==================================================

BAT_SPEED = 2.0
BAT_WIDTH = 6
BAT_HEIGHT = 4


@dataclass
class BatBounds:
    # Limites du rectangle de mouvement, en pixels.
    min_x: int
    max_x: int
    min_y: int
    max_y: int


@dataclass
class Bat:
    # Position actuelle en pixels.
    x: float
    y: float

    # Vitesse actuelle en pixels/frame.
    dx: float
    dy: float

    # Zone dans laquelle la chauve-souris peut bouger.
    bounds: BatBounds

#refactoriser
def grid_to_pixels(i: int) -> int:
    # Convertit une coordonnée de grille vers le centre de la case en pixels.
    return i * TILE_SIZE + TILE_SIZE // 2


def clamp(value: int, min_value: int, max_value: int) -> int:
    # Force value à rester dans [min_value, max_value].
    return max(min_value, min(value, max_value))

#refactoriser
def find_cells(game_map: Map, target: GridCell) -> list[tuple[int, int]]:
    # Trouve toutes les cases d'un certain type dans la map.
    return [
        (x, y)
        for y in range(game_map.height)
        for x in range(game_map.width)
        if game_map.get(x, y) == target
    ]


def find_bats(game_map: Map) -> list[tuple[int, int]]:
    return find_cells(game_map, GridCell.BAT)


def compute_bounds(
    game_map: Map,
    x: int,
    y: int,
    width: int,
    height: int,
) -> BatBounds:
    # Calcule les limites de mouvement autour de la position de départ.
    #
    # x, y sont en coordonnées de grille.
    # Les limites retournées sont en pixels.
    min_grid_x = clamp(x - width // 2, 0, game_map.width - 1)
    max_grid_x = clamp(x + width // 2, 0, game_map.width - 1)

    min_grid_y = clamp(y - height // 2, 0, game_map.height - 1)
    max_grid_y = clamp(y + height // 2, 0, game_map.height - 1)

    return BatBounds(
        min_x=grid_to_pixels(min_grid_x),
        max_x=grid_to_pixels(max_grid_x),
        min_y=grid_to_pixels(min_grid_y),
        max_y=grid_to_pixels(max_grid_y),
    )


def compute_bat_bounds(game_map: Map, x: int, y: int) -> BatBounds:
    return compute_bounds(
        game_map,
        x,
        y,
        BAT_WIDTH,
        BAT_HEIGHT,
    )


def random_velocity(
    rng: random.Random,
    speed: float,
) -> tuple[float, float]:
    # Crée une vitesse aléatoire de norme speed.
    angle = rng.random() * 2 * math.pi

    return (
        math.cos(angle) * speed,
        math.sin(angle) * speed,
    )


def create_bat(
    game_map: Map,
    x: int,
    y: int,
    rng: random.Random,
) -> Bat:
    dx, dy = random_velocity(rng, BAT_SPEED)

    return Bat(
        x=grid_to_pixels(x),
        y=grid_to_pixels(y),
        dx=dx,
        dy=dy,
        bounds=compute_bat_bounds(game_map, x, y),
    )


def create_bats(
    game_map: Map,
    rng: random.Random,
) -> list[Bat]:
    return [
        create_bat(game_map, x, y, rng)
        for x, y in find_bats(game_map)
    ]