import arcade
from enum import Enum

from constants import *
from textures import *
from direction import Direction


class BoomerangState(Enum):
    """
    Le boomerang peut être dans 3 états différents.

    INACTIVE :
        Le boomerang n'est pas utilisé. Il n'est pas visible dans le jeu.

    LAUNCHING :
        Le joueur vient de lancer le boomerang. Il part en ligne droite
        dans la direction où regarde le joueur.

    RETURNING :
        Le boomerang revient vers le joueur après avoir atteint sa distance
        maximale ou après avoir touché un obstacle ou un monstre.
    """
    INACTIVE = 1
    LAUNCHING = 2
    RETURNING = 3


class Boomerang(arcade.TextureAnimationSprite):
    """
    Cette classe représente le boomerang du joueur.

    J'ai choisi d'hériter de TextureAnimationSprite parce que :
    - le boomerang doit être affiché dans le jeu
    - il a une position (center_x, center_y)
    - il possède une animation (rotation du boomerang)

    En héritant de cette classe, je peux facilement :
    - le dessiner
    - lui donner une animation
    - gérer ses collisions
    """

    def __init__(self, center_x: float, center_y: float) -> None:
        """
        Constructeur du boomerang.

        Quand on crée le boomerang :
        - on lui donne son animation
        - sa taille (scale)
        - sa position initiale
        """

        # J'appelle le constructeur de TextureAnimationSprite
        # pour initialiser l'animation et la position.
        super().__init__(
            animation=ANIMATION_BOOMERANG,
            scale=SCALE,
            center_x=center_x,
            center_y=center_y,
        )

        # =========================
        # État du boomerang
        # =========================

        # Au début du jeu, le boomerang est inactif.
        # Il ne sera donc pas affiché tant que le joueur
        # n'appuie pas sur la touche D.
        self.state = BoomerangState.INACTIVE

        # Direction actuelle du boomerang.
        # Cette direction sera copiée depuis la direction du joueur
        # au moment où il lance le boomerang.
        self.direction = Direction.SOUTH

        # Distance parcourue par le boomerang pendant la phase LAUNCHING.
        # Cette variable nous sert à savoir quand il a parcouru
        # la distance maximale (8 cases).
        self.distance_travelled = 0