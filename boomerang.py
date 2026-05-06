from enum import Enum, auto

import arcade

from direction import Direction
from textures import ANIMATION_BOOMERANG


# Taille visuelle du boomerang dans le jeu.
BOOMERANG_SCALE = 2


class BoomerangState(Enum):
    # Le boomerang n'est pas lancé.
    INACTIVE = auto()

    # Le boomerang part depuis le joueur.
    LAUNCHING = auto()

    # Le boomerang revient vers le joueur.
    RETURNING = auto()


class Boomerang(arcade.TextureAnimationSprite):

    def __init__(self):
        # Le boomerang est un sprite animé Arcade.
        # Son animation est chargée dans textures.py.
        super().__init__(
            animation=ANIMATION_BOOMERANG,
            scale=BOOMERANG_SCALE,
        )

        # Au début, le boomerang n'est pas utilisé.
        self.state = BoomerangState.INACTIVE

        # Direction dans laquelle le boomerang est lancé.
        # Elle sera mise à jour avec la direction du joueur dans gameview.py.
        self.direction = Direction.SOUTH

        # Distance déjà parcourue pendant la phase LAUNCHING.
        # Quand cette distance devient assez grande, le boomerang commence à revenir.
        self.distance_travelled = 0