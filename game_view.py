from __future__ import annotations

import random

import arcade

from constants import MAX_WINDOW_HEIGHT, MAX_WINDOW_WIDTH, SCALE, SHIELD_SCALE, SWITCH_SCALE, TILE_SIZE
from textures import (
    ANIMATION_CRYSTAL,
    ANIMATION_PLAYER_IDLE_DOWN,
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
from player import Player
from spinner import create_spinners
from bat import create_bats
from navmesh import create_navmesh
from slime import create_slimes
from switch import create_gates, create_switches, toggle_switch, update_gates
from utils import grid_to_pixels

from enemy_system import EnemySystem
from weapon_system import WeaponSystem
from collision_handler import CollisionHandler
from world_renderer import WorldRenderer


class GameView(arcade.View):
    def __init__(self, game_map: Map) -> None:
        super().__init__()

        self.map = game_map
        self.background_color = arcade.csscolor.CORNFLOWER_BLUE
        self.score = 0
        self.random = random.Random(None)

        self.world_width = self.map.width * TILE_SIZE
        self.world_height = self.map.height * TILE_SIZE

        self._setup_player()
        self._setup_world()
        self._setup_switches_and_gates()

        self.navmesh = create_navmesh(self.map)
        self._setup_enemies()
        self._setup_systems()
        self._setup_keyboard()

        self.physics_engine = arcade.PhysicsEngineSimple(self.player, self.walls)
        self.camera = arcade.camera.Camera2D()
        self.ui_camera = arcade.camera.Camera2D()

    # ==================================================
    # Setup
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
            texture = TEXTURE_SWITCH_ON if switch.is_on else TEXTURE_SWITCH_OFF
            self.switch_sprites.append(
                arcade.Sprite(texture, scale=SWITCH_SCALE,
                              center_x=grid_to_pixels(switch.x),
                              center_y=grid_to_pixels(switch.y))
            )

        for gate in self.gates:
            texture = TEXTURE_GATE_OPEN if gate.is_open else TEXTURE_GATE_CLOSED
            sprite = arcade.Sprite(texture, scale=SCALE,
                                   center_x=grid_to_pixels(gate.x),
                                   center_y=grid_to_pixels(gate.y))
            self.gate_sprites.append(sprite)
            if not gate.is_open:
                self.walls.append(sprite)

    def _setup_enemies(self) -> None:
        # Chaque ennemi connaît déjà sa propre animation (définie dans son __init__).
        # Pas besoin de patcher quoi que ce soit ici.
        bats = create_bats(self.map, self.random)
        slimes = create_slimes(self.map, self.navmesh, self.random)
        spinners = create_spinners(self.map)

        self.enemies = EnemySystem(
            bats=bats,
            slimes=slimes,
            spinners=spinners,
        )

    def _setup_systems(self) -> None:
        self.weapons = WeaponSystem(self.player)

        self.collisions = CollisionHandler(
            player=self.player,
            weapon_system=self.weapons,
            enemies=self.enemies,
            crystals=self.crystals,
            shields=self.shields,
            holes=self.holes,
            switches=self.switches,
            switch_sprites=self.switch_sprites,
            gates=self.gates,
            gate_sprites=self.gate_sprites,
            walls=self.walls,
            on_damage=self._damage_player,
            on_score=self._add_score,
            on_gate_sync=self._sync_gate,
        )

        self.renderer = WorldRenderer(
            player=self.player,
            weapons=self.weapons,
            enemies=self.enemies,
            grounds=self.grounds,
            walls=self.walls,
            gate_sprites=self.gate_sprites,
            holes=self.holes,
            crystals=self.crystals,
            shields=self.shields,
            switch_sprites=self.switch_sprites,
            player_list=self.player_list,
        )

    def _setup_keyboard(self) -> None:
        self.right = self.left = self.up = self.down = False

    # ==================================================
    # Arcade callbacks
    # ==================================================

    def on_show_view(self) -> None:
        self.window.width = min(MAX_WINDOW_WIDTH, self.world_width)
        self.window.height = min(MAX_WINDOW_HEIGHT, self.world_height)

    def on_draw(self) -> None:
        self.clear()
        with self.camera.activate():
            self.renderer.draw_world()
        with self.ui_camera.activate():
            self.renderer.draw_ui(self.score, self.weapons.active_weapon)

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        match symbol:
            case arcade.key.RIGHT:  self.right = True
            case arcade.key.LEFT:   self.left = True
            case arcade.key.UP:     self.up = True
            case arcade.key.DOWN:   self.down = True
            case arcade.key.R:      self.weapons.switch_weapon()
            case arcade.key.D:      self.weapons.use()
            case arcade.key.ESCAPE: self._restart_game()
        self.player.update_movement(self.right, self.left, self.up, self.down)

    def on_key_release(self, symbol: int, modifiers: int) -> None:
        match symbol:
            case arcade.key.RIGHT:  self.right = False
            case arcade.key.LEFT:   self.left = False
            case arcade.key.UP:     self.up = False
            case arcade.key.DOWN:   self.down = False
        self.player.update_movement(self.right, self.left, self.up, self.down)

    def on_update(self, delta_time: float) -> None:
        self.physics_engine.update()
        self.player.update_direction_animation()
        self.player.update_animation()
        self.player.update_invincibility(delta_time)
        self.player.update_shield(delta_time)

        for crystal in self.crystals:
            crystal.update_animation()

        self.enemies.update(
            navmesh=self.navmesh,
            rng=self.random,
            player_position=self.player.position,
            walls=self.walls,
        )
        self.enemies.update_animations()

        self.weapons.update(
            delta_time=delta_time,
            walls=self.walls,
            on_switch_hit=self.collisions.weapon_hits_switches,
            on_enemy_hit_boomerang=self.collisions.weapon_hits_enemies,
            on_enemy_hit_sword=self.collisions.weapon_hits_enemies,
            on_crystal_hit=self.collisions.weapon_hits_crystals,
        )
        self.weapons.update_animations()

        self.collisions.handle_player()
        self.camera.position = self.player.position

    # ==================================================
    # Switches et gates
    # ==================================================

    def _sync_gate(self, switch, switch_sprite: arcade.Sprite) -> None:
        toggle_switch(switch)

        if switch.is_on:
            switch_sprite.texture = TEXTURE_SWITCH_ON
        else:
            switch_sprite.texture = TEXTURE_SWITCH_OFF

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
    # Vie, dégâts, reset
    # ==================================================

    def _add_score(self) -> None:
        self.score += 1

    def _damage_player(self) -> None:
        took_damage = self.player.take_damage()
        if not took_damage:
            return
        if self.player.health <= 0:
            self._restart_game()
            return
        self._respawn_player()

    def _respawn_player(self) -> None:
        self.player.center_x = grid_to_pixels(self.map.player_start_x)
        self.player.center_y = grid_to_pixels(self.map.player_start_y)
        self.player.change_x = 0
        self.player.change_y = 0
        self.weapons.reset()

    def _restart_game(self) -> None:
        self.window.show_view(GameView(self.map))

    # ==================================================
    # Création de sprites monde
    # ==================================================

    def _create_cell_sprites(self, x: int, y: int) -> None:
        self.grounds.append(arcade.Sprite(
            TEXTURE_GRASS, scale=SCALE,
            center_x=grid_to_pixels(x), center_y=grid_to_pixels(y),
        ))

        cell = self.map.get(x, y)

        if cell == GridCell.BUSH:
            self.walls.append(arcade.Sprite(
                TEXTURE_BUSH, scale=SCALE,
                center_x=grid_to_pixels(x), center_y=grid_to_pixels(y),
            ))
        elif cell == GridCell.CRYSTAL:
            self.crystals.append(arcade.TextureAnimationSprite(
                animation=ANIMATION_CRYSTAL, scale=SCALE,
                center_x=grid_to_pixels(x), center_y=grid_to_pixels(y),
            ))
        elif cell == GridCell.SHIELD:
            self.shields.append(arcade.Sprite(
                TEXTURE_SHIELD, scale=SHIELD_SCALE,
                center_x=grid_to_pixels(x), center_y=grid_to_pixels(y),
            ))
        elif cell == GridCell.HOLE:
            self.holes.append(arcade.Sprite(
                TEXTURE_HOLE, scale=SCALE,
                center_x=grid_to_pixels(x), center_y=grid_to_pixels(y),
            ))