from enum import Enum, auto

from direction import Direction
from textures import ANIMATION_BOOMERANG
from weapon_system import Weapon  # Weapon est dans weapon.py, pas weapon_system.py


BOOMERANG_SCALE = 2


class BoomerangState(Enum):
    INACTIVE = auto()
    LAUNCHING = auto()
    RETURNING = auto()


class Boomerang(Weapon):

    def __init__(self):
        super().__init__(
            animation=ANIMATION_BOOMERANG,
            scale=BOOMERANG_SCALE,
        )
        self.state = BoomerangState.INACTIVE
        self.distance_travelled = 0.0

    def is_active(self) -> bool:
        return self.state != BoomerangState.INACTIVE

    def launch(self, direction: Direction, x: float, y: float) -> None:
        self.state = BoomerangState.LAUNCHING
        self.direction = direction
        self.center_x = x
        self.center_y = y
        self.distance_travelled = 0.0

    def return_to_player(self) -> None:
        self.state = BoomerangState.RETURNING

    def deactivate(self) -> None:
        self.state = BoomerangState.INACTIVE
        self.distance_travelled = 0.0