from __future__ import annotations

from typing import TYPE_CHECKING

import arcade

#TYPE_CHECKING permet d'éviter les imports circulaires
if TYPE_CHECKING:
    from player import Player
    from weapon_system import WeaponSystem, ActiveWeapon
    from enemy_system import EnemySystem


class WorldRenderer:
    #responsable unique du dessin : monde et interface
    #ça évite les grand blocs de code dans gameview, et comme
    #ça, meme en terme d'architecture c'est plus intéressant en séparant le dessin,
    #c'est même un de nos points forts comme mentionné dans le fichier du design
    player: Player
    weapons:WeaponSystem
    enemies:EnemySystem
    grounds:arcade.SpriteList
    walls:arcade.SpriteList
    gate_sprites:arcade.SpriteList
    holes:arcade.SpriteList
    crystals:arcade.SpriteList
    shields:arcade.SpriteList
    switch_sprites:arcade.SpriteList
    player_list:arcade.SpriteList
    def __init__(
        self,
        player: Player,
        weapons: WeaponSystem,
        enemies: EnemySystem,
        grounds: arcade.SpriteList,
        walls: arcade.SpriteList,
        gate_sprites: arcade.SpriteList,
        holes: arcade.SpriteList,
        crystals: arcade.SpriteList,
        shields: arcade.SpriteList,
        switch_sprites: arcade.SpriteList,
        player_list: arcade.SpriteList,
    ) -> None:
        self.player = player
        self.weapons = weapons
        self.enemies = enemies
        self.grounds = grounds
        self.walls = walls
        self.gate_sprites = gate_sprites
        self.holes = holes
        self.crystals = crystals
        self.shields = shields
        self.switch_sprites = switch_sprites
        self.player_list = player_list

    #dessin du monde :

    def draw_world(self) -> None:
        self.grounds.draw()
        self.walls.draw()
        self.gate_sprites.draw()
        self.holes.draw()
        self.crystals.draw()
        self.shields.draw()
        self.switch_sprites.draw()

        # Dessin de tous les ennemis.
        self.enemies.bat_sprites.draw()
        self.enemies.slime_sprites.draw()
        self.enemies.spinner_sprites.draw()

        self.player_list.draw()

        # Dessin des armes actives.
        if self.weapons.boomerang.is_active():
            self.weapons.boomerang_list.draw()
        if self.weapons.sword.is_active():
            self.weapons.sword_list.draw()

    #score et interface

    def draw_ui(self, score: int, active_weapon: ActiveWeapon) -> None:
        """délégue tout le reste du dessin"""
        self._draw_score(score)
        self._draw_weapon(active_weapon)
        self._draw_health()
        self._draw_shield()

    def _draw_score(self, score: int) -> None:
        """affichage du score en bas de l'écran, 10, 10 pour assurer qu'on le voit"""
        arcade.Text(f"Score: {score}", 10, 10, arcade.color.WHITE, 20).draw()

    def _draw_weapon(self, active_weapon: ActiveWeapon) -> None:
        """affiche le nom de l'arme actuellement selectionnée"""
        from weapon_system import ActiveWeapon as AW
        name = "Boomerang" if active_weapon == AW.BOOMERANG else "Sword"
        arcade.Text(f"Weapon: {name}", 10, 40, arcade.color.WHITE, 20).draw()

    def _draw_health(self) -> None:
        """affiche les vies restantes au joueur"""
        full = "♥ " * self.player.health
        empty = "♡ " * (self.player.max_health - self.player.health)
        arcade.Text(f"Vies: {full}{empty}", 10, 70, arcade.color.RED, 22).draw()

    def _draw_shield(self) -> None:
        """affiche le temps restant au bouclier"""
        if self.player.has_active_shield():
            value = f"Bouclier: {self.player.shield_time:.1f}s"
        else:
            value = "Bouclier: non"
        arcade.Text(value, 10, 100, arcade.color.LIGHT_BLUE, 20).draw()
