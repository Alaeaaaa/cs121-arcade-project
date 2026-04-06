import arcade
from enum import Enum

from constants import *
from textures import *
from direction import Direction


class BoomerangState(Enum):
    INACTIVE = 1
    LAUNCHING = 2
    RETURNING = 3


class Boomerang(arcade.TextureAnimationSprite):

    def __init__(self, center_x: float, center_y: float) -> None:
        super().__init__(
            animation=ANIMATION_BOOMERANG,
            scale=SCALE,
            center_x=center_x,
            center_y=center_y,
        )

        self.state = BoomerangState.INACTIVE
        self.direction = Direction.SOUTH
        self.distance_travelled = 0