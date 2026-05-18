from abc import ABC, abstractmethod

import arcade

from direction import Direction


class Weapon(arcade.TextureAnimationSprite, ABC):
    def __init__(self, animation, scale: float):
        # Une arme est un sprite animé Arcade.
        # L'animation et la taille sont données par les classes filles.
        super().__init__(
            animation=animation,
            scale=scale,
        )

        # Direction actuelle de l'arme.
        # Elle sera souvent mise à jour avec la direction du joueur.
        self.direction = Direction.SOUTH

    @abstractmethod
    def is_active(self) -> bool:
        # Retourne True si l'arme est actuellement utilisée.
        pass

    @abstractmethod
    def deactivate(self) -> None:
        # Désactive l'arme.
        pass