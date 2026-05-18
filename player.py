import arcade
from textures import *

from constants import (
    PLAYER_MOVEMENT_SPEED,
    PLAYER_MAX_HEALTH,
    PLAYER_INVINCIBILITY_DURATION,
)
from direction import Direction


class Player(arcade.TextureAnimationSprite):

    def __init__(self, animation, scale, center_x, center_y):

        # Player hérite de TextureAnimationSprite.
        # Cela permet d'avoir directement une position, une animation,
        # une hitbox, et la possibilité d'être dessiné par Arcade.
        super().__init__(
            animation=animation,
            scale=scale,
            center_x=center_x,
            center_y=center_y,
        )

        # Direction actuelle du joueur.
        # Elle sert à choisir la bonne animation et la direction des attaques.
        self.direction = Direction.SOUTH

        # =========================
        # Extension : système de vies
        # =========================

        # Nombre maximal de cœurs.
        # On le garde pour pouvoir afficher les cœurs vides aussi.
        self.max_health = PLAYER_MAX_HEALTH

        # Nombre de cœurs actuels.
        # Au début, le joueur commence avec toutes ses vies.
        self.health = PLAYER_MAX_HEALTH

        # Temps restant pendant lequel le joueur est invincible.
        # Au début, il n'est pas invincible, donc la valeur est 0.
        self.invincibility_time = 0.0

    def update_movement(self, right, left, up, down):

        # Cette méthode reçoit des booléens, pas directement des touches Arcade.
        # GameView transforme les touches en right/left/up/down.
        # Ainsi, Player ne dépend pas de arcade.key.

        # =========================
        # Direction du joueur
        # =========================
        # On garde la dernière direction appuyée.
        # Cette direction est utilisée pour l'animation
        # et pour orienter l'épée ou le boomerang.
        if down:
            self.direction = Direction.SOUTH
        elif up:
            self.direction = Direction.NORTH
        elif left:
            self.direction = Direction.WEST
        elif right:
            self.direction = Direction.EAST

        # =========================
        # Vitesse horizontale
        # =========================
        # Droite seulement -> vitesse positive.
        # Gauche seulement -> vitesse négative.
        # Les deux ou aucune -> pas de mouvement horizontal.
        if right and not left:
            self.change_x = PLAYER_MOVEMENT_SPEED
        elif left and not right:
            self.change_x = -PLAYER_MOVEMENT_SPEED
        else:
            self.change_x = 0

        # =========================
        # Vitesse verticale
        # =========================
        # Haut seulement -> vitesse positive.
        # Bas seulement -> vitesse négative.
        # Les deux ou aucune -> pas de mouvement vertical.
        if up and not down:
            self.change_y = PLAYER_MOVEMENT_SPEED
        elif down and not up:
            self.change_y = -PLAYER_MOVEMENT_SPEED
        else:
            self.change_y = 0

    def update_direction_animation(self):

        # Le joueur bouge si au moins une de ses vitesses est non nulle.
        is_moving = self.change_x != 0 or self.change_y != 0

        # On choisit l'animation selon la direction.
        # Pour chaque direction, il y a une animation idle
        # et une animation de course.
        #à refactoriser 
        if self.direction == Direction.SOUTH:
            if is_moving:
                self.animation = ANIMATION_PLAYER_RUN_DOWN
            else:
                self.animation = ANIMATION_PLAYER_IDLE_DOWN

        elif self.direction == Direction.NORTH:
            if is_moving:
                self.animation = ANIMATION_PLAYER_RUN_UP
            else:
                self.animation = ANIMATION_PLAYER_IDLE_UP

        elif self.direction == Direction.WEST:
            if is_moving:
                self.animation = ANIMATION_PLAYER_RUN_LEFT
            else:
                self.animation = ANIMATION_PLAYER_IDLE_LEFT

        elif self.direction == Direction.EAST:
            if is_moving:
                self.animation = ANIMATION_PLAYER_RUN_RIGHT
            else:
                self.animation = ANIMATION_PLAYER_IDLE_RIGHT

    def is_invincible(self) -> bool:

        # Le joueur est invincible tant que ce compteur est positif.
        return self.invincibility_time > 0

    def take_damage(self, amount: int = 1) -> bool:

        # Si le joueur est invincible, on ignore le dégât.
        # On retourne False pour dire à GameView :
        # "aucune vie n'a été perdue".
        if self.is_invincible():
            return False

        # On enlève amount vies.
        # max(0, ...) évite d'avoir une vie négative.
        self.health = max(0, self.health - amount)

        # Après un dégât, le joueur devient invincible pendant un court moment.
        # Cela évite qu'il perde plusieurs cœurs d'un coup.
        self.invincibility_time = PLAYER_INVINCIBILITY_DURATION

        # On retourne True pour dire que le dégât a bien été appliqué.
        return True

    def update_invincibility(self, delta_time: float) -> None:

        # Cette méthode est appelée à chaque frame depuis GameView.
        # Elle diminue le temps d'invincibilité restant.

        if self.invincibility_time > 0:

            # On enlève le temps écoulé depuis la frame précédente.
            # max(0, ...) évite que le compteur devienne négatif.
            self.invincibility_time = max(
                0,
                self.invincibility_time - delta_time,
            )

            # Effet visuel de clignotement :
            # on alterne entre transparent et normal.
            # Ce n'est pas obligatoire pour la logique,
            # mais ça aide à voir que le joueur est invincible.
            if int(self.invincibility_time * 10) % 2 == 0:
                self.alpha = 120
            else:
                self.alpha = 255

        else:
            # Si le joueur n'est plus invincible,
            # on le rend complètement visible.
            #alpha veut dire opacité / transparence
            self.alpha = 255