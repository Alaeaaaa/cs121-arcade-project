from enum import Enum, auto

import arcade

from direction import Direction
from textures import ANIMATION_SWORD

#voir la taille dial sword 

class SwordState(Enum):
    # L'épée existe dans le jeu, mais elle n'est pas en train d'attaquer.
    INACTIVE = auto()

    # L'épée est utilisée par le joueur : elle peut toucher les ennemis.
    ACTIVE = auto()


class Sword(arcade.TextureAnimationSprite):

    def __init__(self):
        # On crée l'épée comme un sprite animé Arcade.
        # On met une animation par défaut vers le bas.
        super().__init__(
            animation=ANIMATION_SWORD[Direction.SOUTH],
            scale=1,
        )

        # Au début, le joueur n'attaque pas.
        self.state = SwordState.INACTIVE

        # Direction actuelle de l'épée.
        # Elle sera mise à jour avec la direction du joueur dans gameview.py.
        self.direction = Direction.SOUTH

        # Compteur utilisé pour savoir depuis combien de temps l'attaque est active.
        self.time = 0

    def update_direction_animation(self):
        # ANIMATION_SWORD est un dictionnaire :
        # chaque direction correspond à une animation d'attaque.
        #
        # Exemple :
        # si self.direction vaut Direction.NORTH,
        # alors ANIMATION_SWORD[self.direction] donne l'animation d'attaque vers le haut.
        self.animation = ANIMATION_SWORD[self.direction]