from __future__ import annotations
from enemy import EnemyContext

import random
from typing import TYPE_CHECKING

import arcade

from bat import Bat
from slime import Slime
from spinner import Spinner

if TYPE_CHECKING:
    from navmesh import NavMesh, Point


class EnemySystem:
    """force de notre design, car gameview n'a plus à connaitre tous les détails des ennemis,
    c'est cette classe qui s'occupe des mises a jour, des animations, et collisions"""
    bats:list[Bat]
    slimes:list[Slime]
    spinners:list[Spinner]
    bat_sprites:arcade.SpriteList
    slime_sprites:arcade.SpriteList
    spinner_sprites:arcade.SpriteList
    def __init__(
        self,
        bats: list[Bat],
        slimes: list[Slime],
        spinners: list[Spinner],
    ) -> None:
        self.bats = bats
        self.slimes = slimes
        self.spinners = spinners

        self.bat_sprites: arcade.SpriteList = arcade.SpriteList()
        self.slime_sprites: arcade.SpriteList = arcade.SpriteList()
        self.spinner_sprites: arcade.SpriteList = arcade.SpriteList()

        for bat in bats:
            bat.sync_sprite()
            self.bat_sprites.append(bat)

        for slime in slimes:
            slime.sync_sprite()
            self.slime_sprites.append(slime)

        for spinner in spinners:
            spinner.sync_sprite()
            self.spinner_sprites.append(spinner)

    def update(
        self,
        context:EnemyContext
    ) -> None:
        """autre point fort du design, chaque entité gère sa propre logique.
        on appelle donc juste les bonnes méthodes en mettant à jour les sprites
        c'est également cette méthode qui sera appelée par gameview"""
        for bat in self.bats:
            bat.update_logic(context)
            bat.sync_sprite()

        for slime in self.slimes:
            slime.update_logic(context)
            slime.sync_sprite()

        for spinner in self.spinners:
            spinner.update_logic(context)
            spinner.sync_sprite()

    def update_animations(self) -> None:
        for sprite in self.bat_sprites:
            sprite.update_animation()
        for sprite in self.slime_sprites:
            sprite.update_animation()

    @property
    def all_sprites(self) -> list[arcade.SpriteList]:
        #returne les spritelists de tous les ennemis
        return [self.bat_sprites, self.slime_sprites, self.spinner_sprites]

    def player_touches_enemy(self, player: arcade.Sprite) -> bool:
        #indique si le joueur touch au moins un ennemi
        return any(
            arcade.check_for_collision_with_list(player, sprites)
            for sprites in self.all_sprites
        )

    def weapon_hits(self, weapon: arcade.Sprite) -> bool:
        # Supprime les ennemis touchés. Retourne True si au moins un touché.
        hit = False
        for sprite_list in self.all_sprites:
            hit |= self._remove_hits(weapon, sprite_list)
        return hit

    def _remove_hits(self, weapon: arcade.Sprite, sprite_list: arcade.SpriteList) -> bool:
        #supprime les sprites en contact avec l'arme
        hit_sprites = arcade.check_for_collision_with_list(weapon, sprite_list)
        for sprite in hit_sprites:
            sprite.remove_from_sprite_lists()
        return len(hit_sprites) > 0
