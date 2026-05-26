from constants import SCALE
from enum import Enum, auto

from direction import Direction
from textures import ANIMATION_SWORD
from weapon import Weapon

class SwordState(Enum):
    """on aurait pu utiliser un booléen à la place, mais
    comme ça au moins c'est bien illustré"""
    INACTIVE = auto()
    ACTIVE = auto()


class Sword(Weapon):
    state:SwordState
    direction:Direction
    time:float
    def __init__(self)->None:
        super().__init__(
            animation=ANIMATION_SWORD[Direction.SOUTH],
            scale=SCALE,
        )
        self.state = SwordState.INACTIVE
        self.time = 0.0

    def is_active(self) -> bool:
        return self.state == SwordState.ACTIVE

    def activate(self, direction: Direction) -> None:
        self.state = SwordState.ACTIVE
        self.direction = direction
        self.time = 0.0
        self.update_direction_animation()

    def deactivate(self) -> None:
        #désactive l'épée, et remet donc le compteur à 0
        self.state = SwordState.INACTIVE
        self.time = 0.0

    def update_direction_animation(self) -> None:
        self.animation = ANIMATION_SWORD[self.direction]
