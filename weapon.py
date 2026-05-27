from abc import abstractmethod

import arcade

from direction import Direction


class Weapon(arcade.TextureAnimationSprite):
<<<<<<< HEAD
    def __init__(self, animation:arcade.TextureAnimation, scale: float)->None:
=======
    def __init__(self, animation, scale: float):
>>>>>>> 7607e3b (c)
        super().__init__(animation=animation, scale=scale)
        self.direction = Direction.SOUTH

    @abstractmethod
    def is_active(self) -> bool:
<<<<<<< HEAD
        """indique si l'arme est active(utilisée)"""
=======
>>>>>>> 7607e3b (c)
        ...

    @abstractmethod
    def deactivate(self) -> None:
<<<<<<< HEAD
        """désactive l'arme en question"""
        ...
=======
        ...
>>>>>>> 7607e3b (c)
