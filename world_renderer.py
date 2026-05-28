from __future__ import annotations
from constants import SCALE
from textures import BOOMERANG_ICON, SWORD_ICON

import arcade

from player import Player
from weapon_system import WeaponSystem
from enemy_system import EnemySystem
from weapon_system import ActiveWeapon

class WorldRenderer:
    """c'est le responsable unique du dessin. pourquoi c'est intéressant ? parce qu'à présent c'est
    ici que le dessin de tout ce qui apparaît à l'écran se fait. On a ainsi centralisé tout ce qui touche
    à l'aspect visuel de notre jeu dans cette classe!"""

    player: Player
    weapons: WeaponSystem
    enemies: EnemySystem
    grounds: arcade.SpriteList
    walls: arcade.SpriteList
    gate_sprites: arcade.SpriteList
    holes: arcade.SpriteList
    crystals: arcade.SpriteList
    shields: arcade.SpriteList
    switch_sprites: arcade.SpriteList
    player_list: arcade.SpriteList

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

    # le monde:
    def draw_world(self) -> None:
        self.grounds.draw()
        self.walls.draw()
        self.gate_sprites.draw()
        self.holes.draw()
        self.crystals.draw()
        self.shields.draw()
        self.switch_sprites.draw()

        #Ennemis:
        self.enemies.bat_sprites.draw()
        self.enemies.slime_sprites.draw()
        self.enemies.spinner_sprites.draw()

        self.player_list.draw()

        #armes actives:
        if self.weapons.boomerang.is_active():
            self.weapons.boomerang_list.draw()
        if self.weapons.sword.is_active():
            self.weapons.sword_list.draw()

    # UI:
    def draw_ui(self, score: int, active_weapon: ActiveWeapon) -> None:
        """Délègue l'affichage de chaque élément d'interface."""
        self._draw_score(score)
        self._draw_weapon(active_weapon)
        self._draw_health()
        self._draw_shield()
        #on dessine les icones des armes :
        texture = (
            BOOMERANG_ICON
            if active_weapon == ActiveWeapon.BOOMERANG
            else SWORD_ICON )

        arcade.draw_sprite(
            arcade.Sprite(
                texture,
                scale=SCALE,
                center_x=20,
                center_y=400,
            )
)

    def _draw_score(self, score: int) -> None:
        """Score en bas à gauche."""
        arcade.Text(f"Score: {score}", 10, 10, arcade.color.WHITE, 20).draw()

    def _draw_weapon(self, active_weapon: ActiveWeapon) -> None:
        """Nom de l'arme sélectionnée."""
        name = "Boomerang" if active_weapon == ActiveWeapon.BOOMERANG else "Sword"
        arcade.Text(f"Weapon: {name}", 10, 40, arcade.color.WHITE, 20).draw()

    def _draw_health(self) -> None:
        """Vies restantes sous forme de cœurs."""
        full  = "♥ " * self.player.health
        empty = "♡ " * (self.player.max_health - self.player.health)
        arcade.Text(f"Vies: {full}{empty}", 10, 70, arcade.color.RED, 22).draw()

    def _draw_shield(self) -> None:
        """Durée restante du bouclier."""
        if self.player.has_active_shield():
            value = f"Bouclier: {self.player.shield_time:.1f}s"
        else:
            value = "Bouclier: non"
        arcade.Text(value, 10, 100, arcade.color.LIGHT_BLUE, 20).draw()
