from __future__ import annotations

from typing import TYPE_CHECKING

import arcade

# TYPE_CHECKING vaut False à l'exécution : ces imports ne sont évalués
# que par les outils d'analyse statique (mypy, Pylance…), ce qui coupe
# les cycles tout en gardant les annotations correctes.
if TYPE_CHECKING:
    from player import Player
    from weapon_system import WeaponSystem
    from enemy_system import EnemySystem

# ActiveWeapon est une enum légère, sans dépendance inverse vers ce module ;
# on peut l'importer normalement. Si ça crée quand même un cycle, déplacez-le
# dans le bloc TYPE_CHECKING et remplacez le paramètre par `int` ou `str`.
from weapon_system import ActiveWeapon


class WorldRenderer:
    # Responsable unique du dessin : monde et interface.
    # Séparer le rendu de GameView améliore la lisibilité et l'architecture
    # (cf. fichier de design).

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

    # ------------------------------------------------------------------ monde

    def draw_world(self) -> None:
        self.grounds.draw()
        self.walls.draw()
        self.gate_sprites.draw()
        self.holes.draw()
        self.crystals.draw()
        self.shields.draw()
        self.switch_sprites.draw()

        # Ennemis
        self.enemies.bat_sprites.draw()
        self.enemies.slime_sprites.draw()
        self.enemies.spinner_sprites.draw()

        self.player_list.draw()

        # Armes actives
        if self.weapons.boomerang.is_active():
            self.weapons.boomerang_list.draw()
        if self.weapons.sword.is_active():
            self.weapons.sword_list.draw()

    # ------------------------------------------------------------------ UI

    def draw_ui(self, score: int, active_weapon: ActiveWeapon) -> None:
        """Délègue l'affichage de chaque élément d'interface."""
        self._draw_score(score)
        self._draw_weapon(active_weapon)
        self._draw_health()
        self._draw_shield()

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