import arcade
from enum import Enum
from textures import *
from player import Direction
from constants import SCALE
class SwordState(Enum):
    INACTIVE=1
    ACTIVE=2

class Sword(arcade.TextureAnimationSprite):
    """
    Cette classe représente l'épée du joueur.

    J'ai choisi d'hériter de TextureAnimationSprite parce que :
    - l'épée doit être affichée dans le jeu
    - elle a une position (center_x, center_y)
    - elle possède une animation (animation d'attaque)

    En héritant de cette classe, je peux facilement :
    - la dessiner
    - lui donner une animation
    - gérer ses collisions (avec les crystaux)
    """
    def __init__(self, center_x, center_y):
        super().__init__(
            animation = ANIMATION_SWORD[Direction.SOUTH],
            scale=SCALE,
            center_x=center_x,
            center_y=center_y,
        )
        # l'épée n'est pas utilisée au début, elle est donc inactive
        self.state=SwordState.INACTIVE
        # sa direction actuelle est celle du joueur (south par défaut)
        self.direction=Direction.SOUTH
        # pour tenir compte du temps d'attaque :
        self.time= 0.0
    # J'ai besoin d'une méthode pour choisir la bonne animation selon la direction actuelle :
    def update_direction_animation(self):
        self.animation=ANIMATION_SWORD[self.direction]
