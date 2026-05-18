from enum import Enum, auto

from direction import Direction
from textures import ANIMATION_SWORD
from weapon import Weapon  # Weapon est dans weapon.py, pas weapon_system.py


class SwordState(Enum):
    INACTIVE = auto()
    ACTIVE = auto()


class Sword(Weapon):

    def __init__(self):
        super().__init__(
            animation=ANIMATION_SWORD[Direction.SOUTH],
            scale=2,
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
        self.state = SwordState.INACTIVE
        self.time = 0.0

    def update_direction_animation(self) -> None:
        self.animation = ANIMATION_SWORD[self.direction]