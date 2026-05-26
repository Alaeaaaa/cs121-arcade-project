from enum import Enum, auto

from direction import Direction
from textures import ANIMATION_BOOMERANG
from weapon import Weapon


from constants import (
    BOOMERANG_SCALE
)

class BoomerangState(Enum):
    INACTIVE = auto()
    LAUNCHING = auto()
    RETURNING = auto()


class Boomerang(Weapon):
    state:BoomerangState
    distance_travelled:float

    def __init__(self)->None:
        super().__init__(
            animation=ANIMATION_BOOMERANG,
            scale=BOOMERANG_SCALE,
        )
        self.state = BoomerangState.INACTIVE
        self.distance_travelled = 0.0

    def is_active(self) -> bool:
        return self.state != BoomerangState.INACTIVE

    def launch(self, direction: Direction, x: float, y: float) -> None:
        #on lance le boomerang depuis une certaine position en tenant compte de la direction
        self.state = BoomerangState.LAUNCHING
        self.direction = direction
        self.center_x = x
        self.center_y = y
        self.distance_travelled = 0.0

    def return_to_player(self) -> None:
        self.state = BoomerangState.RETURNING

    def deactivate(self) -> None:
        #désactive le boomerang, sa distance parcourue est donc à nouveau 0
        self.state = BoomerangState.INACTIVE
        self.distance_travelled = 0.0
