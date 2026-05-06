import arcade
from textures import *

from constants import PLAYER_MOVEMENT_SPEED
from direction import Direction


# Refactoring :
# Avant, on avait un gros if/elif pour choisir l'animation selon la direction.
# Ici, on utilise des dictionnaires :
# direction -> animation correspondante.
#
# Exemple :
# IDLE_ANIMATIONS[Direction.SOUTH] donne ANIMATION_PLAYER_IDLE_DOWN
# RUN_ANIMATIONS[Direction.WEST] donne ANIMATION_PLAYER_RUN_LEFT

IDLE_ANIMATIONS = {
    Direction.SOUTH: ANIMATION_PLAYER_IDLE_DOWN,
    Direction.NORTH: ANIMATION_PLAYER_IDLE_UP,
    Direction.WEST: ANIMATION_PLAYER_IDLE_LEFT,
    Direction.EAST: ANIMATION_PLAYER_IDLE_RIGHT,
}

RUN_ANIMATIONS = {
    Direction.SOUTH: ANIMATION_PLAYER_RUN_DOWN,
    Direction.NORTH: ANIMATION_PLAYER_RUN_UP,
    Direction.WEST: ANIMATION_PLAYER_RUN_LEFT,
    Direction.EAST: ANIMATION_PLAYER_RUN_RIGHT,
}


class Player(arcade.TextureAnimationSprite):

    def __init__(self, animation, scale, center_x, center_y):
        # On crée un sprite animé Arcade avec une animation, une taille et une position.
        super().__init__(
            animation=animation,
            scale=scale,
            center_x=center_x,
            center_y=center_y,
        )

        # Direction par défaut : le joueur regarde vers le bas.
        self.direction = Direction.SOUTH

    def update_movement(self, right, left, up, down):
        # On met à jour la direction regardée.
        # L'ordre donne une priorité : down > up > left > right.
        if down:
            self.direction = Direction.SOUTH
        elif up:
            self.direction = Direction.NORTH
        elif left:
            self.direction = Direction.WEST
        elif right:
            self.direction = Direction.EAST

        # Mouvement horizontal :
        # droite = vitesse positive, gauche = vitesse négative.
        # si droite et gauche sont appuyées ensemble, elles s'annulent.
        self.change_x = 0
        if right and not left:
            self.change_x = PLAYER_MOVEMENT_SPEED
        elif left and not right:
            self.change_x = -PLAYER_MOVEMENT_SPEED

        # Mouvement vertical :
        # haut = vitesse positive, bas = vitesse négative.
        self.change_y = 0
        if up and not down:
            self.change_y = PLAYER_MOVEMENT_SPEED
        elif down and not up:
            self.change_y = -PLAYER_MOVEMENT_SPEED

    def update_direction_animation(self):
        # Le joueur bouge si au moins une vitesse est non nulle.
        is_moving = self.change_x != 0 or self.change_y != 0

        # Refactoring :
        # on choisit le dictionnaire selon l'état du joueur,
        # puis on utilise la direction comme clé.
        #
        # Exemple :
        # si is_moving = True et self.direction = Direction.EAST,
        # alors animations[Direction.EAST] donne ANIMATION_PLAYER_RUN_RIGHT.
        if is_moving:
            animations = RUN_ANIMATIONS
        else:
            animations = IDLE_ANIMATIONS

        self.animation = animations[self.direction]