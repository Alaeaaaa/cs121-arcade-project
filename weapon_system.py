from __future__ import annotations

import math
from enum import Enum, auto
from typing import TYPE_CHECKING

import arcade

from constants import (
    BOOMERANG_CATCH_DISTANCE,
    BOOMERANG_MAX_DISTANCE_IN_TILES,
    BOOMERANG_SPEED,
    SWORD_ATTACK_DURATION,
    TILE_SIZE,
)
from direction import Direction
from boomerang import Boomerang, BoomerangState
from sword import Sword

if TYPE_CHECKING:
    from player import Player

BOOMERANG_MAX_DISTANCE = BOOMERANG_MAX_DISTANCE_IN_TILES * TILE_SIZE


class ActiveWeapon(Enum):
    BOOMERANG = auto()
    SWORD = auto()


class WeaponSystem:
    #Gère les deux armes du joueur : boomerang et épée.

    def __init__(self, player: Player) -> None:
        self.player = player
        self.active_weapon = ActiveWeapon.BOOMERANG

        self.boomerang = Boomerang()
        self.boomerang.position = player.position

        self.sword = Sword()
        self.sword.position = player.position

        self.boomerang_list: arcade.SpriteList = arcade.SpriteList()
        self.boomerang_list.append(self.boomerang)

        self.sword_list: arcade.SpriteList = arcade.SpriteList()
        self.sword_list.append(self.sword)

    # --------------------------------------------------
    # État général
    # --------------------------------------------------

    def all_inactive(self) -> bool:
        return not self.boomerang.is_active() and not self.sword.is_active()

    def switch_weapon(self) -> None:
        if not self.all_inactive():
            return
        if self.active_weapon == ActiveWeapon.BOOMERANG:
            self.active_weapon = ActiveWeapon.SWORD
        else:
            self.active_weapon = ActiveWeapon.BOOMERANG

    def use(self) -> None:
        if self.active_weapon == ActiveWeapon.BOOMERANG:
            self._launch_boomerang()
        else:
            self._start_sword_attack()

    def reset(self) -> None:
        #Remet les armes dans un état propre après un dégât.
        self.boomerang.deactivate()
        self.sword.deactivate()
        self.boomerang.position = self.player.position
        self.sword.position = self.player.position

    # --------------------------------------------------
    # Update principal
    # --------------------------------------------------

    def update(
        self,
        delta_time: float,
        walls: arcade.SpriteList,
        on_switch_hit: callable,
        on_enemy_hit_boomerang: callable,
        on_enemy_hit_sword: callable,
        on_crystal_hit: callable,
    ) -> None:
        self._update_boomerang(walls, on_switch_hit, on_enemy_hit_boomerang)
        self._update_sword(delta_time, on_switch_hit, on_enemy_hit_sword, on_crystal_hit)

    def update_animations(self) -> None:
        if self.boomerang.is_active():
            self.boomerang.update_animation()
        if self.sword.is_active():
            self.sword.update_animation()

    # --------------------------------------------------
    # Boomerang
    # --------------------------------------------------

    def _launch_boomerang(self) -> None:
        if not self.all_inactive():
            return
        self.boomerang.launch(
            self.player.direction,
            self.player.center_x,
            self.player.center_y,
        )

    def _update_boomerang(
        self,
        walls: arcade.SpriteList,
        on_switch_hit: callable,
        on_enemy_hit: callable,
    ) -> None:
        if self.boomerang.state == BoomerangState.LAUNCHING:
            self._update_boomerang_launching(walls, on_switch_hit, on_enemy_hit)
        elif self.boomerang.state == BoomerangState.RETURNING:
            self._update_boomerang_returning(on_switch_hit, on_enemy_hit)

    def _update_boomerang_launching(
        self,
        walls: arcade.SpriteList,
        on_switch_hit: callable,
        on_enemy_hit: callable,
    ) -> None:
        self._move_boomerang_forward()
        self.boomerang.distance_travelled += BOOMERANG_SPEED

        should_return = (
            self.boomerang.distance_travelled >= BOOMERANG_MAX_DISTANCE
            or on_switch_hit(self.boomerang)
            or self._boomerang_hits_wall(walls)
            or on_enemy_hit(self.boomerang)
        )

        if should_return:
            self.boomerang.return_to_player()

    def _move_boomerang_forward(self) -> None:
        match self.boomerang.direction:
            case Direction.NORTH:
                self.boomerang.center_y += BOOMERANG_SPEED
            case Direction.SOUTH:
                self.boomerang.center_y -= BOOMERANG_SPEED
            case Direction.EAST:
                self.boomerang.center_x += BOOMERANG_SPEED
            case Direction.WEST:
                self.boomerang.center_x -= BOOMERANG_SPEED

    def _boomerang_hits_wall(self, walls: arcade.SpriteList) -> bool:
        return bool(arcade.check_for_collision_with_list(self.boomerang, walls))

    def _update_boomerang_returning(
        self,
        on_switch_hit: callable,  #ajouter les types 
        on_enemy_hit: callable,
    ) -> None:
        dx = self.player.center_x - self.boomerang.center_x
        dy = self.player.center_y - self.boomerang.center_y
        distance = math.sqrt(dx**2 + dy**2)

        if distance <= BOOMERANG_CATCH_DISTANCE:
            self.boomerang.deactivate()
            self.boomerang.position = self.player.position
            return

        self.boomerang.center_x += BOOMERANG_SPEED * dx / distance
        self.boomerang.center_y += BOOMERANG_SPEED * dy / distance

        on_switch_hit(self.boomerang)
        on_enemy_hit(self.boomerang)

    # --------------------------------------------------
    # Épée
    # --------------------------------------------------

    def _start_sword_attack(self) -> None:
        if not self.all_inactive():
            return
        self.sword.position = self.player.position
        self.sword.activate(self.player.direction)

    def _update_sword(
        self,
        delta_time: float,
        on_switch_hit: callable,
        on_enemy_hit: callable,
        on_crystal_hit: callable,
    ) -> None:
        if not self.sword.is_active():
            return

        self.sword.position = self.player.position
        self.sword.time += delta_time

        if self.sword.time >= SWORD_ATTACK_DURATION:
            self.sword.deactivate()
            return

        on_enemy_hit(self.sword)
        on_crystal_hit(self.sword)
        on_switch_hit(self.sword)