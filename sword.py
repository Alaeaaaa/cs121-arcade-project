import arcade
from enum import Enum
from textures import *
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
    def __init__(self, center_x, center_y, direction):
        super().__init__()
        self.center_x=center_x
        self.center_y=center_y
        self.direction=direction
        self.animation = ANIMATION_SWORD[direction]
        self.state=SwordState.INACTIVE
