from __future__ import annotations

import math
from typing import TYPE_CHECKING, Callable

import arcade

from constants import HOLE_DEATH_DISTANCE
from textures import SOUND_COIN

if TYPE_CHECKING:
    from player import Player
    from enemy_system import EnemySystem
    from switch import Switch, Gate
    from weapon_system import WeaponSystem


class CollisionHandler:
    """
    Centralise toutes les collisions :
    joueur vs cristaux, boucliers, ennemis, trous
    armes vs ennemis, switches, cristaux
    """

    def __init__(
        self,
        player: Player,
        enemies: EnemySystem,
        crystals: arcade.SpriteList,
        shields: arcade.SpriteList,
        holes: arcade.SpriteList,
        switches: list[Switch],
        switch_sprites: arcade.SpriteList,
        gates: list[Gate],
        gate_sprites: arcade.SpriteList,
        walls: arcade.SpriteList,
        on_damage: Callable[[], None],
        on_score: Callable[[], None],
        on_gate_sync: Callable[[Switch, arcade.Sprite], None],
    ) -> None:
        self.player = player
        self.enemies = enemies
        self.crystals = crystals
        self.shields = shields
        self.holes = holes
        self.switches = switches
        self.switch_sprites = switch_sprites
        self.gates = gates
        self.gate_sprites = gate_sprites
        self.walls = walls
        self.on_damage = on_damage
        self.on_score = on_score
        self.on_gate_sync = on_gate_sync


    # Collisions du joueur

    def handle_player(self) -> None:
        """on gère ici les colliusions du joueur avec les crystaux, boucliers, ennemies et les trous"""
        self._collect_crystals(
            arcade.check_for_collision_with_list(self.player, self.crystals)
        )
        self._collect_shields(
            arcade.check_for_collision_with_list(self.player, self.shields)
        )
        self._handle_death_collisions()

    def _collect_crystals(self, hit: list[arcade.Sprite]) -> None:
        """ramassage des crystaux"""
        for crystal in hit:
            crystal.remove_from_sprite_lists()
            arcade.play_sound(SOUND_COIN)
            self.on_score()

    def _collect_shields(self, hit: list[arcade.Sprite]) -> None:
        """ramassage des boucliers"""
        for shield in hit:
            shield.remove_from_sprite_lists()
            self.player.activate_shield()
            arcade.play_sound(SOUND_COIN)

    def _handle_death_collisions(self) -> None:
        """application des dégâts si un ennemi est tocuhé, ou si on tombe dans un trou"""
        if self._player_touches_enemy() or self._player_touches_hole():
            self.on_damage()

    def _player_touches_enemy(self) -> bool:
        """on vérifie si on touche un ennemi"""
        return self.enemies.player_touches_enemy(self.player)

    def _player_touches_hole(self) -> bool:
        """on vérifie si on tombe dans un trou"""
        nearby = arcade.check_for_collision_with_list(self.player, self.holes)
        return any(
            math.dist(self.player.position, hole.position) <= HOLE_DEATH_DISTANCE
            for hole in nearby
        )


    #Collisions des armes:

    def weapon_hits_enemies(self, weapon: arcade.Sprite) -> bool:
        #on délègue la tâche à EnemySystem
        return self.enemies.weapon_hits(weapon)

    def weapon_hits_crystals(self, weapon: arcade.Sprite) -> bool:
        #permet à l'arme (donc l'épée ici) de ramasser les crystaux
        hit = arcade.check_for_collision_with_list(weapon, self.crystals)
        if hit :
            self._collect_crystals(hit)
            return True
        return False

    def weapon_hits_switches(self, weapon: arcade.Sprite) -> bool:
        #on active les interrupteurs touchés, et automatiquement on doit mettre à jour les portails
        touched = False

        for switch, switch_sprite in zip(self.switches, self.switch_sprites):
            is_touching = arcade.check_for_collision(weapon, switch_sprite)

            if is_touching and not switch.is_being_hit:
                switch.is_being_hit = True
                touched = True
                self.on_gate_sync(switch, switch_sprite)

            elif not is_touching:
                switch.is_being_hit = False

        return touched
