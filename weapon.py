from abc import ABC, abstractmethod

import arcade

from direction import Direction


class Weapon(arcade.TextureAnimationSprite, ABC):
    def __init__(self, animation, scale: float):
        super().__init__(animation=animation, scale=scale)
        self.direction = Direction.SOUTH

    @abstractmethod
    def is_active(self) -> bool:
        pass

    @abstractmethod
    def deactivate(self) -> None:
        pass