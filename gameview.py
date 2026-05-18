from __future__ import annotations

from enum import Enum
from typing import Final
import math
import random

import arcade

from constants import (
    MAX_WINDOW_HEIGHT,
    MAX_WINDOW_WIDTH,
    SCALE,
    SHIELD_SCALE,
    SPINNER_MOVEMENT_SPEED,
    TILE_SIZE,
)

from textures import (
    ANIMATION_BAT,
    ANIMATION_CRYSTAL,
    ANIMATION_PLAYER_IDLE_DOWN,
    ANIMATION_SPINNER,
    SOUND_COIN,
    TEXTURE_BUSH,
    TEXTURE_GATE_CLOSED,
    TEXTURE_GATE_OPEN,
    TEXTURE_GRASS,
    TEXTURE_HOLE,
    TEXTURE_SHIELD,
    TEXTURE_SWITCH_OFF,
    TEXTURE_SWITCH_ON,
)

from map import GridCell, Map
from direction import Direction
from player import Player

from spinner import Direction as SpinnerDirection
from spinner import Spinner, create_spinners

from bat import Bat, create_bats

from navmesh import NavMesh, create_navmesh
from slime import Slime, create_slimes, update_slime_movement

from switch import (
    Gate,
    Switch,
    create_gates,
    create_switches,
    toggle_switch,
    update_gates,
)

from boomerang import Boomerang, BoomerangState
from sword import Sword


# ==================================================
# Constantes propres à GameView
# ==================================================

BOOMERANG_SPEED: Final[int] = 8
BOOMERANG_MAX_DISTANCE: Final[int] = 8 * TILE_SIZE
BOOMERANG_CATCH_DISTANCE: Final[int] = 8

SWORD_ATTACK_DURATION: Final[float] = 0.3

HOLE_DEATH_DISTANCE: Final[int] = 16

SWITCH_SCALE: Final[float] = 0.25


def grid_to_pixels(i: int) -> int:
    # Convertit une position de grille en position pixel.
    # Exemple : la case 0 devient le centre de la première case.
    return i * TILE_SIZE + TILE_SIZE // 2


class ActiveWeapon(Enum):
    BOOMERANG = 1
    SWORD = 2


class GameView(arcade.View):
    world_width: Final[int]
    world_height: Final[int]

    player: Final[Player]
    player_list: Final[arcade.SpriteList[Player]]

    grounds: Final[arcade.SpriteList[arcade.Sprite]]
    walls: Final[arcade.SpriteList[arcade.Sprite]]
    crystals: Final[arcade.SpriteList[arcade.TextureAnimationSprite]]
    shields: Final[arcade.SpriteList[arcade.Sprite]]
    holes: Final[arcade.SpriteList[arcade.Sprite]]

    switches: list[Switch]
    switch_sprites: arcade.SpriteList[arcade.Sprite]

    gates: list[Gate]
    gate_sprites: arcade.SpriteList[arcade.Sprite]

    spinners: list[Spinner]
    spinner_sprites: arcade.SpriteList[arcade.TextureAnimationSprite]

    bats: list[Bat]
    bat_sprites: arcade.SpriteList[arcade.TextureAnimationSprite]

    navmesh: NavMesh
    slimes: list[Slime]
    slime_sprites: arcade.SpriteList[arcade.TextureAnimationSprite]

    active_weapon: ActiveWeapon

    boomerang: Boomerang
    boomerang_list: arcade.SpriteList[arcade.TextureAnimationSprite]

    sword: Sword
    sword_list: arcade.SpriteList[arcade.TextureAnimationSprite]

    physics_engine: Final[arcade.PhysicsEngineSimple]
    camera: Final[arcade.camera.Camera2D]
    ui_camera: Final[arcade.camera.Camera2D]

    def __init__(self, game_map: Map) -> None:
        super().__init__()

        self.map = game_map

        self.background_color = arcade.csscolor.CORNFLOWER_BLUE
        self.score = 0

        self.world_width = self.map.width * TILE_SIZE
        self.world_height = self.map.height * TILE_SIZE

        self.random = random.Random(None)

        self._setup_player()
        self._setup_weapons()
        self._setup_world()
        self._setup_switches_and_gates()
        self._setup_spinners()
        self._setup_bats()

        self.navmesh = create_navmesh(self.map)
        self._setup_slimes()

        self._setup_keyboard()
        self._setup_physics_and_cameras()

    # ==================================================
    # Extension : système de vies
    # ==================================================

    def _reset_weapons(self) -> None:
        # Cette méthode remet les armes dans un état propre.
        # Elle est appelée après un dégât, quand le joueur est replacé
        # à sa position de départ.

        # Maintenant, chaque arme sait elle-même comment se désactiver.
        self.boomerang.deactivate()
        self.sword.deactivate()

        # On replace le boomerang sur le joueur.
        self.boomerang.position = self.player.position

        # On replace aussi l'épée sur le joueur.
        self.sword.position = self.player.position

    def _respawn_player(self) -> None:
        # Cette méthode replace le joueur à sa position de départ
        # après avoir perdu une vie.
        #
        # On ne recommence pas toute la partie ici :
        # les cristaux collectés restent collectés,
        # les ennemis tués restent morts,
        # et le score reste le même.

        # On remet le joueur sur la case de départ de la map.
        self.player.center_x = grid_to_pixels(self.map.player_start_x)
        self.player.center_y = grid_to_pixels(self.map.player_start_y)

        # On arrête son mouvement.
        # Sinon, il pourrait continuer à bouger juste après le respawn.
        self.player.change_x = 0
        self.player.change_y = 0

        # On remet les armes dans un état propre.
        self._reset_weapons()

    def _damage_player(self) -> bool:
        # Cette méthode centralise toutes les collisions dangereuses.
        # Au lieu de répéter la logique pour les spinners, bats, trous, slimes,
        # on appelle toujours _damage_player().
        #
        # Elle retourne True si une vie a vraiment été perdue.
        # Elle retourne False si le joueur était invincible ou protégé.

        # On demande au joueur de prendre un dégât.
        took_damage = self.player.take_damage()

        # Si le joueur était invincible ou protégé par le bouclier,
        # aucune vie n'est perdue.
        if not took_damage:
            return False

        # Si le joueur n'a plus de vies, on recommence complètement.
        if self.player.health <= 0:
            self._restart_game()
            return True

        # Sinon, il a encore des vies :
        # on le replace simplement au début.
        self._respawn_player()
        return True

    # ==================================================
    # Setup général
    # ==================================================

    def _setup_player(self) -> None:
        self.player = Player(
            animation=ANIMATION_PLAYER_IDLE_DOWN,
            scale=SCALE,
            center_x=grid_to_pixels(self.map.player_start_x),
            center_y=grid_to_pixels(self.map.player_start_y),
        )

        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player)

    def _setup_weapons(self) -> None:
        self.active_weapon = ActiveWeapon.BOOMERANG

        self.boomerang = Boomerang()
        self.boomerang.position = self.player.position

        self.sword = Sword()
        self.sword.position = self.player.position

        self.boomerang_list = arcade.SpriteList()
        self.boomerang_list.append(self.boomerang)

        self.sword_list = arcade.SpriteList()
        self.sword_list.append(self.sword)

    def _setup_world(self) -> None:
        self.grounds = arcade.SpriteList(use_spatial_hash=True)
        self.walls = arcade.SpriteList(use_spatial_hash=True)
        self.crystals = arcade.SpriteList()
        self.shields = arcade.SpriteList()
        self.holes = arcade.SpriteList()

        for y in range(self.map.height):
            for x in range(self.map.width):
                self._create_cell_sprites(x, y)

    def _setup_switches_and_gates(self) -> None:
        self.switches = create_switches(self.map)
        self.gates = create_gates(self.map, self.switches)

        self.switch_sprites = arcade.SpriteList()
        self.gate_sprites = arcade.SpriteList()

        for switch in self.switches:
            switch_sprite = self._create_switch_sprite(switch)
            self.switch_sprites.append(switch_sprite)

        for gate in self.gates:
            gate_sprite = self._create_gate_sprite(gate)
            self.gate_sprites.append(gate_sprite)

            if not gate.is_open:
                self.walls.append(gate_sprite)

    def _setup_spinners(self) -> None:
        self.spinners = create_spinners(self.map)
        self.spinner_sprites = arcade.SpriteList()

        for spinner in self.spinners:
            self.spinner_sprites.append(
                self._create_animated_sprite(
                    animation=ANIMATION_SPINNER,
                    x=spinner.x,
                    y=spinner.y,
                )
            )

    def _setup_bats(self) -> None:
        self.bats = create_bats(self.map, self.random)
        self.bat_sprites = arcade.SpriteList()

        for bat in self.bats:
            bat_sprite = arcade.TextureAnimationSprite(
                animation=ANIMATION_BAT,
                scale=SCALE,
                center_x=bat.x,
                center_y=bat.y,
            )

            self.bat_sprites.append(bat_sprite)

    def _setup_slimes(self) -> None:
        self.slimes = create_slimes(
            self.map,
            self.navmesh,
            self.random,
        )

        self.slime_sprites = arcade.SpriteList()

        for slime in self.slimes:
            slime_sprite = arcade.TextureAnimationSprite(
                animation=ANIMATION_BAT,   # error AJOUTER L'ANIMATION
                scale=SCALE,
                center_x=slime.x,
                center_y=slime.y,
            )

            self.slime_sprites.append(slime_sprite)

    def _setup_keyboard(self) -> None:
        self.right = False
        self.left = False
        self.up = False
        self.down = False

    def _setup_physics_and_cameras(self) -> None:
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player,
            self.walls,
        )

        self.camera = arcade.camera.Camera2D()
        self.ui_camera = arcade.camera.Camera2D()

    # ==================================================
    # Création de sprites
    # ==================================================

    def _create_static_sprite(
        self,
        texture: arcade.Texture,
        x: int,
        y: int,
    ) -> arcade.Sprite:
        return arcade.Sprite(
            texture,
            scale=SCALE,
            center_x=grid_to_pixels(x),
            center_y=grid_to_pixels(y),
        )

    def _create_shield_sprite(
        self,
        x: int,
        y: int,
    ) -> arcade.Sprite:
        return arcade.Sprite(
            TEXTURE_SHIELD,
            scale=SHIELD_SCALE,
            center_x=grid_to_pixels(x),
            center_y=grid_to_pixels(y),
        )

    def _create_animated_sprite(
        self,
        animation: arcade.TextureAnimation,
        x: int,
        y: int,
    ) -> arcade.TextureAnimationSprite:
        return arcade.TextureAnimationSprite(
            animation=animation,
            scale=SCALE,
            center_x=grid_to_pixels(x),
            center_y=grid_to_pixels(y),
        )

    def _create_switch_sprite(self, switch: Switch) -> arcade.Sprite:
        if switch.is_on:
            texture = TEXTURE_SWITCH_ON
        else:
            texture = TEXTURE_SWITCH_OFF

        return arcade.Sprite(
            texture,
            scale=SWITCH_SCALE,
            center_x=grid_to_pixels(switch.x),
            center_y=grid_to_pixels(switch.y),
        )

    def _create_gate_sprite(self, gate: Gate) -> arcade.Sprite:
        if gate.is_open:
            texture = TEXTURE_GATE_OPEN
        else:
            texture = TEXTURE_GATE_CLOSED

        return arcade.Sprite(
            texture,
            scale=SCALE,
            center_x=grid_to_pixels(gate.x),
            center_y=grid_to_pixels(gate.y),
        )

    def _create_cell_sprites(self, x: int, y: int) -> None:
        # Chaque cellule reçoit d'abord du sol.
        self.grounds.append(
            self._create_static_sprite(TEXTURE_GRASS, x, y)
        )

        cell = self.map.get(x, y)

        if cell == GridCell.BUSH:
            self.walls.append(
                self._create_static_sprite(TEXTURE_BUSH, x, y)
            )

        elif cell == GridCell.CRYSTAL:
            self.crystals.append(
                self._create_animated_sprite(ANIMATION_CRYSTAL, x, y)
            )

        elif getattr(GridCell, "SHIELD", None) is not None and cell == GridCell.SHIELD:
            self.shields.append(
                self._create_shield_sprite(x, y)
            )

        elif cell == GridCell.HOLE:
            self.holes.append(
                self._create_static_sprite(TEXTURE_HOLE, x, y)
            )

        # Important :
        # SWITCH et GATE ne sont pas créés ici.
        # Ils sont créés dans _setup_switches_and_gates.

    # ==================================================
    # Méthodes Arcade principales
    # ==================================================

    def on_show_view(self) -> None:
        self.window.width = min(MAX_WINDOW_WIDTH, self.world_width)
        self.window.height = min(MAX_WINDOW_HEIGHT, self.world_height)

    def on_draw(self) -> None:
        self.clear()

        with self.camera.activate():
            self._draw_world()

        with self.ui_camera.activate():
            self._draw_ui()

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        match symbol:
            case arcade.key.RIGHT:
                self.right = True
            case arcade.key.LEFT:
                self.left = True
            case arcade.key.UP:
                self.up = True
            case arcade.key.DOWN:
                self.down = True
            case arcade.key.R:
                self._switch_weapon()
            case arcade.key.D:
                self._use_active_weapon()
            case arcade.key.ESCAPE:
                self._restart_game()

        self._update_player_movement()

    def on_key_release(self, symbol: int, modifiers: int) -> None:
        match symbol:
            case arcade.key.RIGHT:
                self.right = False
            case arcade.key.LEFT:
                self.left = False
            case arcade.key.UP:
                self.up = False
            case arcade.key.DOWN:
                self.down = False

        self._update_player_movement()

    def on_update(self, delta_time: float) -> None:
        self._update_player(delta_time)
        self._update_animations()
        self._update_enemies()
        self._update_weapons(delta_time)
        self._handle_player_collisions()

        self.camera.position = self.player.position

    # ==================================================
    # Dessin
    # ==================================================

    def _draw_world(self) -> None:
        self.grounds.draw()

        # self.walls contient les buissons et les portails fermés.
        self.walls.draw()

        # On dessine aussi tous les portails.
        # Les portails fermés sont déjà dans self.walls,
        # mais on les redessine ici avec leur texture de portail.
        self.gate_sprites.draw()

        self.holes.draw()
        self.crystals.draw()
        self.shields.draw()
        self.switch_sprites.draw()

        self.spinner_sprites.draw()
        self.bat_sprites.draw()
        self.slime_sprites.draw()

        self.player_list.draw()

        # Grâce à Weapon, GameView peut juste demander si l'arme est active.
        if self.boomerang.is_active():
            self.boomerang_list.draw()

        # Même chose pour l'épée.
        if self.sword.is_active():
            self.sword_list.draw()

    def _draw_ui(self) -> None:
        score_text = arcade.Text(
            f"Score: {self.score}",
            10,
            10,
            arcade.color.WHITE,
            20,
        )
        score_text.draw()

        if self.active_weapon == ActiveWeapon.BOOMERANG:
            weapon_name = "Boomerang"
        else:
            weapon_name = "Sword"

        weapon_text = arcade.Text(
            f"Weapon: {weapon_name}",
            10,
            40,
            arcade.color.WHITE,
            20,
        )
        weapon_text.draw()

        # =========================
        # Extension : affichage des vies
        # =========================

        # On affiche un cœur plein pour chaque vie restante.
        full_hearts = "♥ " * self.player.health

        # On affiche un cœur vide pour chaque vie perdue.
        empty_hearts = "♡ " * (self.player.max_health - self.player.health)

        # Exemple :
        # 3 vies -> ♥ ♥ ♥
        # 2 vies -> ♥ ♥ ♡
        # 1 vie  -> ♥ ♡ ♡
        hearts = full_hearts + empty_hearts

        hearts_text = arcade.Text(
            f"Vies: {hearts}",
            10,
            70,
            arcade.color.RED,
            22,
        )
        hearts_text.draw()

        # =========================
        # Extension : affichage du bouclier
        # =========================

        if self.player.has_active_shield():
            shield_text_value = f"Bouclier: {self.player.shield_time:.1f}s"
        else:
            shield_text_value = "Bouclier: non"

        shield_text = arcade.Text(
            shield_text_value,
            10,
            100,
            arcade.color.LIGHT_BLUE,
            20,
        )
        shield_text.draw()

    # ==================================================
    # Clavier et armes
    # ==================================================

    def _update_player_movement(self) -> None:
        self.player.update_movement(
            self.right,
            self.left,
            self.up,
            self.down,
        )

    def _switch_weapon(self) -> None:
        if not self._all_weapons_are_inactive():
            return

        if self.active_weapon == ActiveWeapon.BOOMERANG:
            self.active_weapon = ActiveWeapon.SWORD
        else:
            self.active_weapon = ActiveWeapon.BOOMERANG

    def _use_active_weapon(self) -> None:
        if self.active_weapon == ActiveWeapon.BOOMERANG:
            self._launch_boomerang()
        elif self.active_weapon == ActiveWeapon.SWORD:
            self._start_sword_attack()

    def _all_weapons_are_inactive(self) -> bool:
        # On utilise la méthode commune définie dans Weapon.
        return not self.boomerang.is_active() and not self.sword.is_active()

    def _launch_boomerang(self) -> None:
        if not self._all_weapons_are_inactive():
            return

        # Le boomerang gère lui-même son état, sa direction,
        # sa position et sa distance parcourue.
        self.boomerang.launch(
            self.player.direction,
            self.player.center_x,
            self.player.center_y,
        )

    def _start_sword_attack(self) -> None:
        if not self._all_weapons_are_inactive():
            return

        self.sword.position = self.player.position

        # L'épée gère elle-même son état, sa direction,
        # son animation et son timer.
        self.sword.activate(self.player.direction)

    # ==================================================
    # Update général
    # ==================================================

    def _update_player(self, delta_time: float) -> None:
        self.physics_engine.update()
        self.player.update_direction_animation()
        self.player.update_animation()

        # =========================
        # Extension : invincibilité
        # =========================
        # Après un dégât, le joueur devient invincible pendant un court moment.
        # Cette méthode diminue le compteur et fait clignoter le joueur.
        self.player.update_invincibility(delta_time)
        self.player.update_shield(delta_time)

    def _update_animations(self) -> None:
        for crystal in self.crystals:
            crystal.update_animation()

        for spinner_sprite in self.spinner_sprites:
            spinner_sprite.update_animation()

        # Grâce à Weapon, on n'a plus besoin de vérifier directement l'état interne.
        if self.boomerang.is_active():
            self.boomerang.update_animation()

        if self.sword.is_active():
            self.sword.update_animation()

    def _update_enemies(self) -> None:
        self._update_spinners()
        self._update_bats()
        self._update_slimes()

    def _update_weapons(self, delta_time: float) -> None:
        self._update_boomerang()
        self._update_sword(delta_time)

    # ==================================================
    # Spinners
    # ==================================================

    def _update_spinners(self) -> None:
        for spinner, sprite in zip(self.spinners, self.spinner_sprites):
            self._update_spinner(spinner, sprite)

    def _update_spinner(
        self,
        spinner: Spinner,
        sprite: arcade.TextureAnimationSprite,
    ) -> None:
        if spinner.horizontal:
            self._update_horizontal_spinner(spinner, sprite)
        else:
            self._update_vertical_spinner(spinner, sprite)

    def _update_horizontal_spinner(
        self,
        spinner: Spinner,
        sprite: arcade.TextureAnimationSprite,
    ) -> None:
        if spinner.direction == SpinnerDirection.POSITIF:
            self._move_spinner_right(spinner, sprite)
        else:
            self._move_spinner_left(spinner, sprite)

    def _update_vertical_spinner(
        self,
        spinner: Spinner,
        sprite: arcade.TextureAnimationSprite,
    ) -> None:
        if spinner.direction == SpinnerDirection.POSITIF:
            self._move_spinner_up(spinner, sprite)
        else:
            self._move_spinner_down(spinner, sprite)

    def _move_spinner_right(
        self,
        spinner: Spinner,
        sprite: arcade.TextureAnimationSprite,
    ) -> None:
        sprite.center_x += SPINNER_MOVEMENT_SPEED

        right_limit = grid_to_pixels(spinner.limites.max_x)

        if sprite.center_x >= right_limit:
            sprite.center_x = right_limit
            spinner.direction = SpinnerDirection.NEGATIF

    def _move_spinner_left(
        self,
        spinner: Spinner,
        sprite: arcade.TextureAnimationSprite,
    ) -> None:
        sprite.center_x -= SPINNER_MOVEMENT_SPEED

        left_limit = grid_to_pixels(spinner.limites.min_x)

        if sprite.center_x <= left_limit:
            sprite.center_x = left_limit
            spinner.direction = SpinnerDirection.POSITIF

    def _move_spinner_up(
        self,
        spinner: Spinner,
        sprite: arcade.TextureAnimationSprite,
    ) -> None:
        sprite.center_y += SPINNER_MOVEMENT_SPEED

        top_limit = grid_to_pixels(spinner.limites.max_y)

        if sprite.center_y >= top_limit:
            sprite.center_y = top_limit
            spinner.direction = SpinnerDirection.NEGATIF

    def _move_spinner_down(
        self,
        spinner: Spinner,
        sprite: arcade.TextureAnimationSprite,
    ) -> None:
        sprite.center_y -= SPINNER_MOVEMENT_SPEED

        bottom_limit = grid_to_pixels(spinner.limites.min_y)

        if sprite.center_y <= bottom_limit:
            sprite.center_y = bottom_limit
            spinner.direction = SpinnerDirection.POSITIF

    # ==================================================
    # Bats
    # ==================================================

    def _update_bats(self) -> None:
        for bat, bat_sprite in zip(self.bats, self.bat_sprites):
            self._update_bat(bat, bat_sprite)

    def _update_bat(
        self,
        bat: Bat,
        bat_sprite: arcade.TextureAnimationSprite,
    ) -> None:
        bat_sprite.update_animation()

        bat.x += bat.dx
        bat.y += bat.dy

        if bat.x < bat.bounds.min_x or bat.x > bat.bounds.max_x:
            bat.dx = -bat.dx
            bat.x += bat.dx

        if bat.y < bat.bounds.min_y or bat.y > bat.bounds.max_y:
            bat.dy = -bat.dy
            bat.y += bat.dy

        bat_sprite.center_x = bat.x
        bat_sprite.center_y = bat.y

    # ==================================================
    # Slimes
    # ==================================================

    def _update_slimes(self) -> None:
        for slime, slime_sprite in zip(self.slimes, self.slime_sprites):
            self._update_slime(slime, slime_sprite)

    def _update_slime(
        self,
        slime: Slime,
        slime_sprite: arcade.TextureAnimationSprite,
    ) -> None:
        update_slime_movement(
            slime,
            self.navmesh,
            self.random,
            self.player.position,
            self.walls,
        )

        slime_sprite.center_x = slime.x
        slime_sprite.center_y = slime.y
        slime_sprite.update_animation()

    # ==================================================
    # Boomerang
    # ==================================================

    def _update_boomerang(self) -> None:
        if self.boomerang.state == BoomerangState.LAUNCHING:
            self._update_boomerang_launching()

        elif self.boomerang.state == BoomerangState.RETURNING:
            self._update_boomerang_returning()

    def _update_boomerang_launching(self) -> None:
        self._move_boomerang_forward()
        self.boomerang.distance_travelled += BOOMERANG_SPEED

        if self.boomerang.distance_travelled >= BOOMERANG_MAX_DISTANCE:
            self._start_boomerang_return()

        if self._weapon_hits_switches(self.boomerang):
            self._start_boomerang_return()

        if self._boomerang_hits_wall():
            self._start_boomerang_return()

        if self._boomerang_hits_enemy():
            self._start_boomerang_return()

    def _move_boomerang_forward(self) -> None:
        if self.boomerang.direction == Direction.NORTH:
            self.boomerang.center_y += BOOMERANG_SPEED
        elif self.boomerang.direction == Direction.SOUTH:
            self.boomerang.center_y -= BOOMERANG_SPEED
        elif self.boomerang.direction == Direction.EAST:
            self.boomerang.center_x += BOOMERANG_SPEED
        elif self.boomerang.direction == Direction.WEST:
            self.boomerang.center_x -= BOOMERANG_SPEED

    def _start_boomerang_return(self) -> None:
        # Le boomerang sait lui-même comment passer en mode retour.
        self.boomerang.return_to_player()

    def _boomerang_hits_wall(self) -> bool:
        return self._has_collision(self.boomerang, self.walls)

    def _boomerang_hits_enemy(self) -> bool:
        killed_bat = self._weapon_hits_bats(self.boomerang)
        killed_spinner = self._weapon_hits_spinners(self.boomerang)
        killed_slime = self._weapon_hits_slimes(self.boomerang)

        return killed_bat or killed_spinner or killed_slime

    def _update_boomerang_returning(self) -> None:
        dx = self.player.center_x - self.boomerang.center_x
        dy = self.player.center_y - self.boomerang.center_y

        distance = math.sqrt(dx**2 + dy**2)

        if distance <= BOOMERANG_CATCH_DISTANCE:
            self._catch_boomerang()
            return

        self.boomerang.center_x += BOOMERANG_SPEED * dx / distance
        self.boomerang.center_y += BOOMERANG_SPEED * dy / distance

        self._weapon_hits_switches(self.boomerang)
        self._boomerang_hits_enemy()

    def _catch_boomerang(self) -> None:
        # Le boomerang sait lui-même comment se désactiver.
        self.boomerang.deactivate()
        self.boomerang.position = self.player.position

    # ==================================================
    # Sword
    # ==================================================

    def _update_sword(self, delta_time: float) -> None:
        if not self.sword.is_active():
            return

        self.sword.position = self.player.position
        self.sword.time += delta_time

        if self.sword.time >= SWORD_ATTACK_DURATION:
            self._stop_sword_attack()
            return

        self._sword_hits_enemies()
        self._sword_hits_crystals()
        self._weapon_hits_switches(self.sword)

    def _stop_sword_attack(self) -> None:
        # L'épée sait elle-même comment se désactiver.
        self.sword.deactivate()

        for switch in self.switches:
            switch.is_being_hit = False

    def _sword_hits_enemies(self) -> None:
        self._weapon_hits_spinners(self.sword)
        self._weapon_hits_bats(self.sword)
        self._weapon_hits_slimes(self.sword)

    def _sword_hits_crystals(self) -> None:
        crystals = self._collisions(self.sword, self.crystals)
        self._collect_crystals(crystals)

    # ==================================================
    # Switches et gates
    # ==================================================

    def _weapon_hits_switches(self, weapon: arcade.Sprite) -> bool:
        touched_switch = False

        for switch, switch_sprite in zip(self.switches, self.switch_sprites):
            is_touching = arcade.check_for_collision(
                weapon,
                switch_sprite,
            )

            if is_touching and not switch.is_being_hit:
                switch.is_being_hit = True
                touched_switch = True

                toggle_switch(switch)
                self._sync_switch_texture(switch, switch_sprite)
                self._sync_gates()

            elif not is_touching:
                switch.is_being_hit = False

        return touched_switch

    def _sync_switch_texture(
        self,
        switch: Switch,
        switch_sprite: arcade.Sprite,
    ) -> None:
        if switch.is_on:
            switch_sprite.texture = TEXTURE_SWITCH_ON
        else:
            switch_sprite.texture = TEXTURE_SWITCH_OFF

    def _sync_gates(self) -> None:
        update_gates(self.switches, self.gates)

        for gate, gate_sprite in zip(self.gates, self.gate_sprites):
            if gate.is_open:
                gate_sprite.texture = TEXTURE_GATE_OPEN

                if gate_sprite in self.walls:
                    self.walls.remove(gate_sprite)

            else:
                gate_sprite.texture = TEXTURE_GATE_CLOSED

                if gate_sprite not in self.walls:
                    self.walls.append(gate_sprite)

    # ==================================================
    # Collisions avec les armes
    # ==================================================

    def _weapon_hits_spinners(self, weapon: arcade.Sprite) -> bool:
        colliding_spinners = self._collisions(weapon, self.spinner_sprites)

        for spinner_sprite in colliding_spinners:
            self._remove_spinner_sprite(spinner_sprite)

        return len(colliding_spinners) > 0

    def _weapon_hits_bats(self, weapon: arcade.Sprite) -> bool:
        colliding_bats = self._collisions(weapon, self.bat_sprites)

        for bat_sprite in colliding_bats:
            self._remove_bat_sprite(bat_sprite)

        return len(colliding_bats) > 0

    def _weapon_hits_slimes(self, weapon: arcade.Sprite) -> bool:
        colliding_slimes = self._collisions(weapon, self.slime_sprites)

        for slime_sprite in colliding_slimes:
            self._remove_slime_sprite(slime_sprite)

        return len(colliding_slimes) > 0

    def _remove_spinner_sprite(self, spinner_sprite: arcade.Sprite) -> None:
        self._remove_sprite_and_matching_logic(
            target_sprite=spinner_sprite,
            sprites=self.spinner_sprites,
            logic_objects=self.spinners,
        )

    def _remove_bat_sprite(self, bat_sprite: arcade.Sprite) -> None:
        self._remove_sprite_and_matching_logic(
            target_sprite=bat_sprite,
            sprites=self.bat_sprites,
            logic_objects=self.bats,
        )

    def _remove_slime_sprite(self, slime_sprite: arcade.Sprite) -> None:
        self._remove_sprite_and_matching_logic(
            target_sprite=slime_sprite,
            sprites=self.slime_sprites,
            logic_objects=self.slimes,
        )

    def _remove_sprite_and_matching_logic(
        self,
        target_sprite: arcade.Sprite,
        sprites: arcade.SpriteList,
        logic_objects: list,
    ) -> None:
        # Les listes sont parallèles :
        # sprites[i] correspond à logic_objects[i].
        for i, sprite in enumerate(sprites):
            if sprite == target_sprite:
                sprite.remove_from_sprite_lists()
                logic_objects.pop(i)
                return

    # ==================================================
    # Collisions du joueur
    # ==================================================

    def _handle_player_collisions(self) -> None:
        self._handle_player_collect_crystals()
        self._handle_player_collect_shields()
        self._handle_player_death_collisions()

    def _handle_player_collect_crystals(self) -> None:
        crystals = self._collisions(self.player, self.crystals)
        self._collect_crystals(crystals)

    def _handle_player_collect_shields(self) -> None:
        shields = self._collisions(self.player, self.shields)

        for shield in shields:
            shield.remove_from_sprite_lists()
            self.player.activate_shield()
            arcade.play_sound(SOUND_COIN)

    def _collect_crystals(
        self,
        crystals: list[arcade.TextureAnimationSprite],
    ) -> None:
        for crystal in crystals:
            crystal.remove_from_sprite_lists()
            arcade.play_sound(SOUND_COIN)
            self.score += 1

    def _handle_player_death_collisions(self) -> None:
        # Avant l'extension, le joueur recommençait directement la partie.
        # Maintenant, une collision dangereuse enlève une vie.

        if self._player_touches_enemy():
            self._damage_player()
            return

        if self._player_touches_hole():
            self._damage_player()
            return

    def _player_touches_enemy(self) -> bool:
        return (
            self._has_collision(self.player, self.spinner_sprites)
            or self._has_collision(self.player, self.bat_sprites)
            or self._has_collision(self.player, self.slime_sprites)
        )

    def _player_touches_hole(self) -> bool:
        nearby_holes = self._collisions(self.player, self.holes)

        for hole in nearby_holes:
            if math.dist(self.player.position, hole.position) <= HOLE_DEATH_DISTANCE:
                return True

        return False

    # ==================================================
    # Fonctions générales de collision
    # ==================================================

    def _collisions(
        self,
        sprite: arcade.Sprite,
        sprite_list: arcade.SpriteList,
    ) -> list[arcade.Sprite]:
        return arcade.check_for_collision_with_list(sprite, sprite_list)

    def _has_collision(
        self,
        sprite: arcade.Sprite,
        sprite_list: arcade.SpriteList,
    ) -> bool:
        return len(self._collisions(sprite, sprite_list)) > 0

    # ==================================================
    # Reset
    # ==================================================

    def _restart_game(self) -> None:
        new_view = GameView(self.map)
        self.window.show_view(new_view)