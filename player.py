import arcade
from textures import *

from constants import PLAYER_MOVEMENT_SPEED
from direction import Direction


class Player(arcade.TextureAnimationSprite):

    def __init__(self, animation, scale, center_x, center_y):

        super().__init__(
            animation=animation,
            scale=scale,
            center_x=center_x,
            center_y=center_y
        )
        self.direction = Direction.SOUTH

    def update_movement(self, right, left, up, down):

        # mise à jour de la direction (priorité demandée)
        if down:
            self.direction = Direction.SOUTH
        elif up:
            self.direction = Direction.NORTH
        elif left:
            self.direction = Direction.WEST
        elif right:
            self.direction = Direction.EAST

        # mouvement horizontal
        if right and not left:
            self.change_x = PLAYER_MOVEMENT_SPEED
        elif left and not right:
            self.change_x = -PLAYER_MOVEMENT_SPEED
        else:
            self.change_x = 0

        # mouvement vertical
        if up and not down:
            self.change_y = PLAYER_MOVEMENT_SPEED
        elif down and not up:
            self.change_y = -PLAYER_MOVEMENT_SPEED
        else:
            self.change_y = 0

    def update_direction_animation(self):

        is_moving = (self.change_x != 0 or self.change_y != 0)

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