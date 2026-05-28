from abc import abstractmethod

import arcade

from direction import Direction


class Weapon(arcade.TextureAnimationSprite):

    def __init__(self, animation: arcade.TextureAnimation , scale: float)->None:

        super().__init__(animation=animation, scale=scale)
        self.direction = Direction.SOUTH

    @abstractmethod
    def is_active(self) -> bool:
        """indique si l'arme est active(utilisée)"""
        ...

    @abstractmethod
    def deactivate(self) -> None:
        """désactive l'arme en question"""
        ...
