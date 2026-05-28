from __future__ import annotations

import math
import random

from map import Map, GridCell
from utils import grid_to_pixels, find_cells
from enemy import Enemy, EnemyContext
from textures import ANIMATION_BAT

from constants import BAT_SPEED, BAT_WIDTH, BAT_HEIGHT, SCALE, FRAMES_BAT_TURN


def _clamp(value: float, min_value: float, max_value: float) -> int:
    """comme son nom l'indique, elle ramène une valeur dans un
    intervalle donné. """
    return int(max(min_value, min(value, max_value)))


def _random_velocity(rng: random.Random, speed: float) -> tuple[float, float]:
    """cette fonction s'occupe de générer une vitesse de direction aléatoire
    pour gérer l'aspect semi-aleatoire du mvt des bats."""
    angle = rng.random() * 2 * math.pi
    return math.cos(angle) * speed, math.sin(angle) * speed


class Bat(Enemy):
    """Chauve-souris : rebondit dans un rectangle de mouvement.
    à noter qu'on a opté pour un design séparant logique et affichage,
    c'est sync_sprite qui donnera à center_x et y leurs valeurs. """
    logic_x:float
    logic_y:float
    dx:float
    dy:float
    min_x:int
    max_x:int
    min_y:int
    max_y:int
    frames_to_turn: int
    rng: random.Random
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
        rng: random.Random,
    ) -> None:
        super().__init__(animation=ANIMATION_BAT, scale=SCALE)

        self.logic_x = start_x
        self.logic_y = start_y
        self.dx = dx
        self.dy = dy
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y
        self.frames_to_turn = FRAMES_BAT_TURN
        self.rng = rng
    def _turn_velocity_slightly(self) -> tuple[float, float]:
        angle = math.atan2(self.dy, self.dx)
        angle += self.rng.uniform(-math.pi / 6, math.pi / 6)
        return math.cos(angle) * BAT_SPEED, math.sin(angle) * BAT_SPEED

    def update_logic(self, context:EnemyContext) -> None:
        """c'est la fonction qui met à jour la pos logique de la bat."""
        next_x = self.logic_x + self.dx
        next_y = self.logic_y + self.dy

        if next_x <= self.min_x or next_x >= self.max_x:
            """càd qu'on a atteint les limites du rectangle d'action, on inverse la vitesse."""
            self.dx = -self.dx
            next_x = self.logic_x + self.dx
            self.frames_to_turn = FRAMES_BAT_TURN

        if next_y <= self.min_y or next_y >= self.max_y :
            self.dy = -self.dy
            next_y = self.logic_y + self.dy
            self.frames_to_turn = FRAMES_BAT_TURN

        self.logic_x = next_x
        self.logic_y = next_y

        self.frames_to_turn -= 1

        if self.frames_to_turn <= 0:
            self.dx, self.dy = self._turn_velocity_slightly()
            self.frames_to_turn = FRAMES_BAT_TURN

    def sync_sprite(self) -> None:
        self.center_x = self.logic_x
        self.center_y = self.logic_y


def _compute_bat_bounds(game_map: Map, x: int, y: int) -> tuple[int, int, int, int]:
    """ici, on calcule les limites de déplacement de la chauve-souris"""
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
        rng=rng
    )


def create_bats(game_map: Map, rng: random.Random) -> list[Bat]:
    return [
        create_bat(game_map, x, y, rng)
        for x, y in find_cells(game_map, GridCell.BAT)
    ]
