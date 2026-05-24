from __future__ import annotations

import math
import random

from map import Map, GridCell
from utils import grid_to_pixels, find_cells
from enemy import Enemy


# ==================================================
# Constantes des chauves-souris
# ==================================================
from constants import (
    BAT_SPEED,
    BAT_WIDTH ,
    BAT_HEIGHT 
)



def _clamp(value: int, min_value: int, max_value: int) -> int:
    return max(min_value, min(value, max_value))


def _random_velocity(rng: random.Random, speed: float) -> tuple[float, float]:
    angle = rng.random() * 2 * math.pi
    return math.cos(angle) * speed, math.sin(angle) * speed


class Bat(Enemy):
    
    #Chauve-souris : rebondit dans un rectangle de mouvement.
    

    def __init__(
        self,
        start_x: float,
        start_y: float,
        dx: float,
        dy: float,
        min_x: int,
        max_x: int,
        min_y: int,
        max_y: int,
    ) -> None:
        super().__init__()

        # Position logique en pixels.
        self.logic_x = start_x
        self.logic_y = start_y

        # Vitesse en pixels/frame.
        self.dx = dx
        self.dy = dy

        # Limites de la zone de mouvement en pixels.
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y

    def update_logic(self, **kwargs) -> None:
        # Déplacement + rebond sur les bords.
        self.logic_x += self.dx
        self.logic_y += self.dy

        if self.logic_x <= self.min_x or self.logic_x >= self.max_x:
            self.dx = -self.dx
            self.logic_x = _clamp(self.logic_x, self.min_x, self.max_x)

        if self.logic_y <= self.min_y or self.logic_y >= self.max_y:
            self.dy = -self.dy
            self.logic_y = _clamp(self.logic_y, self.min_y, self.max_y)

    def sync_sprite(self) -> None:
        self.center_x = self.logic_x
        self.center_y = self.logic_y


# --------------------------------------------------
# Factories
# --------------------------------------------------

def _compute_bat_bounds(
    game_map: Map,
    x: int,
    y: int,
) -> tuple[int, int, int, int]:
    # Retourne (min_x, max_x, min_y, max_y) en pixels.
    min_grid_x = _clamp(x - BAT_WIDTH // 2, 0, game_map.width - 1)
    max_grid_x = _clamp(x + BAT_WIDTH // 2, 0, game_map.width - 1)
    min_grid_y = _clamp(y - BAT_HEIGHT // 2, 0, game_map.height - 1)
    max_grid_y = _clamp(y + BAT_HEIGHT // 2, 0, game_map.height - 1)

    return (
        grid_to_pixels(min_grid_x),
        grid_to_pixels(max_grid_x),
        grid_to_pixels(min_grid_y),
        grid_to_pixels(max_grid_y),
    )


def create_bat(game_map: Map, x: int, y: int, rng: random.Random) -> Bat:
    dx, dy = _random_velocity(rng, BAT_SPEED)
    min_x, max_x, min_y, max_y = _compute_bat_bounds(game_map, x, y)

    return Bat(
        start_x=grid_to_pixels(x),
        start_y=grid_to_pixels(y),
        dx=dx,
        dy=dy,
        min_x=min_x,
        max_x=max_x,
        min_y=min_y,
        max_y=max_y,
    )


def create_bats(game_map: Map, rng: random.Random) -> list[Bat]:
    return [
        create_bat(game_map, x, y, rng)
        for x, y in find_cells(game_map, GridCell.BAT)
    ]