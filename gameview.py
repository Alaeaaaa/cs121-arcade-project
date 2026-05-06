from enum import Enum
from typing import Final
import math
import random

import arcade

from constants import (
    MAX_WINDOW_HEIGHT,
    MAX_WINDOW_WIDTH,
    SCALE,
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
    TEXTURE_GRASS,
    TEXTURE_HOLE,
)

from map import GridCell, Map
from direction import Direction
from player import Player
from spinner import Direction as SpinnerDirection
from spinner import Spinner, create_spinners
from bat import BAT_DIRECTION_CHANGE, Bat, create_bats
from slime import Slime, create_slimes, update_slime_random_movement
from boomerang import Boomerang, BoomerangState
from sword import Sword, SwordState


# ==================================================
# Constantes propres à GameView
# ==================================================

BOOMERANG_SPEED: Final[int] = 8
BOOMERANG_MAX_DISTANCE: Final[int] = 8 * TILE_SIZE
BOOMERANG_CATCH_DISTANCE: Final[int] = 8

SWORD_ATTACK_DURATION: Final[float] = 0.3

HOLE_DEATH_DISTANCE: Final[int] = 16


def grid_to_pixels(i: int) -> int:
    # La map utilise des coordonnées de grille : 0, 1, 2, 3, ...
    # Arcade utilise des coordonnées en pixels.
    #
    # Exemple avec TILE_SIZE = 64 :
    # case 0 -> centre à 32 pixels
    # case 1 -> centre à 96 pixels
    #
    # On ajoute TILE_SIZE // 2 car Arcade place les sprites par leur centre.
    return i * TILE_SIZE + TILE_SIZE // 2


class ActiveWeapon(Enum):
    # Arme actuellement sélectionnée.
    BOOMERANG = 1
    SWORD = 2


class GameView(arcade.View):
    # GameView est la vue principale du jeu.
    #
    # Son rôle :
    # - créer le monde
    # - afficher le monde
    # - lire le clavier
    # - mettre à jour les objets à chaque frame
    # - gérer les collisions

    world_width: Final[int]
    world_height: Final[int]

    player: Final[Player]
    player_list: Final[arcade.SpriteList[Player]]

    grounds: Final[arcade.SpriteList[arcade.Sprite]]
    walls: Final[arcade.SpriteList[arcade.Sprite]]
    crystals: Final[arcade.SpriteList[arcade.TextureAnimationSprite]]
    holes: Final[arcade.SpriteList[arcade.Sprite]]

    spinners: list[Spinner]
    spinner_sprites: arcade.SpriteList[arcade.TextureAnimationSprite]

    bats: list[Bat]
    bat_sprites: arcade.SpriteList[arcade.TextureAnimationSprite]

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

        # Même générateur aléatoire pour bats + slimes.
        self.random = random.Random(None)

        self._setup_player()
        self._setup_weapons()
        self._setup_world()
        self._setup_spinners()
        self._setup_bats()
        self._setup_slimes()
        self._setup_keyboard()
        self._setup_physics_and_cameras()

    # ==================================================
    # Setup général
    # ==================================================

    def _setup_player(self) -> None:
        # On crée le joueur à sa position de départ.
        self.player = Player(
            animation=ANIMATION_PLAYER_IDLE_DOWN,
            scale=SCALE,
            center_x=grid_to_pixels(self.map.player_start_x),
            center_y=grid_to_pixels(self.map.player_start_y),
        )

        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player)

    def _setup_weapons(self) -> None:
        # Au début, l'arme sélectionnée est le boomerang.
        self.active_weapon = ActiveWeapon.BOOMERANG

        # Boomerang() et Sword() ne prennent pas center_x / center_y.
        # Donc on les crée d'abord, puis on les place sur le joueur.
        self.boomerang = Boomerang()
        self.boomerang.position = self.player.position

        self.sword = Sword()
        self.sword.position = self.player.position

        self.boomerang_list = arcade.SpriteList()
        self.boomerang_list.append(self.boomerang)

        self.sword_list = arcade.SpriteList()
        self.sword_list.append(self.sword)

    def _setup_world(self) -> None:
        # Listes du décor.
        self.grounds = arcade.SpriteList(use_spatial_hash=True)
        self.walls = arcade.SpriteList(use_spatial_hash=True)
        self.crystals = arcade.SpriteList()
        self.holes = arcade.SpriteList()

        # On parcourt la map case par case.
        for y in range(self.map.height):
            for x in range(self.map.width):
                self._create_cell_sprites(x, y)

    def _setup_spinners(self) -> None:
        # Partie logique des spinners.
        self.spinners = create_spinners(self.map)

        # Partie visuelle des spinners.
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
        # Partie logique des bats.
        self.bats = create_bats(self.map, self.random)

        # Partie visuelle des bats.
        self.bat_sprites = arcade.SpriteList()

        for bat in self.bats:
            self.bat_sprites.append(
                self._create_animated_sprite(
                    animation=ANIMATION_BAT,
                    x=bat.start_x,
                    y=bat.start_y,
                )
            )

    def _setup_slimes(self) -> None:
        # Même idée que pour les bats :
        # - self.slimes contient la logique
        # - self.slime_sprites contient les images affichées
        #
        # Pour l'instant, on utilise ANIMATION_BAT comme image temporaire.
        # Plus tard, on pourra mettre une vraie texture de slime.
        self.slimes = create_slimes(self.map, self.random)
        self.slime_sprites = arcade.SpriteList()

        for slime in self.slimes:
            slime_sprite = arcade.TextureAnimationSprite(
                animation=ANIMATION_BAT,
                scale=SCALE,
                center_x=slime.x,
                center_y=slime.y,
            )
            self.slime_sprites.append(slime_sprite)

    def _setup_keyboard(self) -> None:
        # Ces booléens mémorisent les touches actuellement appuyées.
        self.right = False
        self.left = False
        self.up = False
        self.down = False

    def _setup_physics_and_cameras(self) -> None:
        # Le joueur ne peut pas traverser les murs.
        self.physics_engine = arcade.PhysicsEngineSimple(self.player, self.walls)

        # camera suit le monde.
        # ui_camera reste fixe pour le score et l'arme active.
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
        # Crée un sprite simple à partir d'une texture.
        # x et y sont en coordonnées de grille.
        return arcade.Sprite(
            texture,
            scale=SCALE,
            center_x=grid_to_pixels(x),
            center_y=grid_to_pixels(y),
        )

    def _create_animated_sprite(
        self,
        animation: arcade.TextureAnimation,
        x: int,
        y: int,
    ) -> arcade.TextureAnimationSprite:
        # Crée un sprite animé.
        # x et y sont en coordonnées de grille.
        return arcade.TextureAnimationSprite(
            animation=animation,
            scale=SCALE,
            center_x=grid_to_pixels(x),
            center_y=grid_to_pixels(y),
        )

    def _create_cell_sprites(self, x: int, y: int) -> None:
        # Chaque case reçoit toujours de l'herbe.
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

        elif cell == GridCell.HOLE:
            self.holes.append(
                self._create_static_sprite(TEXTURE_HOLE, x, y)
            )

    # ==================================================
    # Méthodes Arcade principales
    # ==================================================

    def on_show_view(self) -> None:
        # Appelé quand la vue devient active.
        self.window.width = min(MAX_WINDOW_WIDTH, self.world_width)
        self.window.height = min(MAX_WINDOW_HEIGHT, self.world_height)

    def on_draw(self) -> None:
        # Dessine tout le jeu.
        self.clear()

        with self.camera.activate():
            self._draw_world()

        with self.ui_camera.activate():
            self._draw_ui()

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        # Appelé quand une touche est appuyée.
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
        # Appelé quand une touche est relâchée.
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
        # Appelé à chaque frame.
        self._update_player()
        self._update_animations()
        self._update_enemies()
        self._update_weapons(delta_time)
        self._handle_player_collisions()

        # La caméra suit le joueur.
        self.camera.position = self.player.position

    # ==================================================
    # Dessin
    # ==================================================

    def _draw_world(self) -> None:
        # L'ordre de dessin est important.
        self.grounds.draw()
        self.walls.draw()
        self.holes.draw()
        self.crystals.draw()

        self.spinner_sprites.draw()
        self.bat_sprites.draw()
        self.slime_sprites.draw()

        self.player_list.draw()

        if self.boomerang.state != BoomerangState.INACTIVE:
            self.boomerang_list.draw()

        if self.sword.state == SwordState.ACTIVE:
            self.sword_list.draw()

    def _draw_ui(self) -> None:
        # Score.
        score_text = arcade.Text(
            f"Score: {self.score}",
            10,
            10,
            arcade.color.WHITE,
            20,
        )
        score_text.draw()

        # Arme active.
        # Ça permet de voir si R change bien d'arme.
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
        # On ne change pas d'arme si une arme est déjà utilisée.
        if not self._all_weapons_are_inactive():
            return

        if self.active_weapon == ActiveWeapon.BOOMERANG:
            self.active_weapon = ActiveWeapon.SWORD
        else:
            self.active_weapon = ActiveWeapon.BOOMERANG

    def _use_active_weapon(self) -> None:
        # D utilise l'arme sélectionnée.
        if self.active_weapon == ActiveWeapon.BOOMERANG:
            self._launch_boomerang()
        elif self.active_weapon == ActiveWeapon.SWORD:
            self._start_sword_attack()

    def _all_weapons_are_inactive(self) -> bool:
        return (
            self.boomerang.state == BoomerangState.INACTIVE
            and self.sword.state == SwordState.INACTIVE
        )

    def _launch_boomerang(self) -> None:
        if self.boomerang.state != BoomerangState.INACTIVE:
            return

        self.boomerang.position = self.player.position
        self.boomerang.direction = self.player.direction
        self.boomerang.state = BoomerangState.LAUNCHING
        self.boomerang.distance_travelled = 0

    def _start_sword_attack(self) -> None:
        if not self._all_weapons_are_inactive():
            return

        self.sword.position = self.player.position
        self.sword.direction = self.player.direction
        self.sword.update_direction_animation()

        self.sword.state = SwordState.ACTIVE
        self.sword.time = 0

    # ==================================================
    # Update général
    # ==================================================

    def _update_player(self) -> None:
        self.physics_engine.update()
        self.player.update_direction_animation()
        self.player.update_animation()

    def _update_animations(self) -> None:
        for crystal in self.crystals:
            crystal.update_animation()

        for spinner_sprite in self.spinner_sprites:
            spinner_sprite.update_animation()

        if self.boomerang.state != BoomerangState.INACTIVE:
            self.boomerang.update_animation()

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

        self._maybe_change_bat_direction(bat)

        new_x, new_y = self._compute_next_bat_position(bat, bat_sprite)

        new_x, new_y = self._bounce_bat_if_needed(
            bat,
            bat_sprite,
            new_x,
            new_y,
        )

        bat_sprite.center_x = new_x
        bat_sprite.center_y = new_y

    def _maybe_change_bat_direction(self, bat: Bat) -> None:
        bat.frames_direction_change -= 1

        if bat.frames_direction_change <= 0:
            bat.angle += self.random.uniform(-0.5, 0.5)
            bat.frames_direction_change = BAT_DIRECTION_CHANGE

    def _compute_next_bat_position(
        self,
        bat: Bat,
        bat_sprite: arcade.TextureAnimationSprite,
    ) -> tuple[float, float]:
        # Bat :
        # dx, dy viennent d'un angle.
        dx = bat.speed * math.cos(bat.angle)
        dy = bat.speed * math.sin(bat.angle)

        return bat_sprite.center_x + dx, bat_sprite.center_y + dy

    def _bounce_bat_if_needed(
        self,
        bat: Bat,
        bat_sprite: arcade.TextureAnimationSprite,
        new_x: float,
        new_y: float,
    ) -> tuple[float, float]:
        min_x = grid_to_pixels(int(bat.bounds.min_x))
        max_x = grid_to_pixels(int(bat.bounds.max_x))
        min_y = grid_to_pixels(int(bat.bounds.min_y))
        max_y = grid_to_pixels(int(bat.bounds.max_y))

        if new_x < min_x or new_x > max_x:
            bat.angle = math.pi - bat.angle
            new_x, new_y = self._compute_next_bat_position(bat, bat_sprite)

        if new_y < min_y or new_y > max_y:
            bat.angle = -bat.angle
            new_x, new_y = self._compute_next_bat_position(bat, bat_sprite)

        return new_x, new_y

    # ==================================================
    # Slimes
    # ==================================================

    def _update_slimes(self) -> None:
        # Même structure que les bats :
        # on garde une liste logique et une liste visuelle.
        for slime, slime_sprite in zip(self.slimes, self.slime_sprites):
            self._update_slime(slime, slime_sprite)

    def _update_slime(
        self,
        slime: Slime,
        slime_sprite: arcade.TextureAnimationSprite,
    ) -> None:
        # Slime :
        # contrairement à la bat, il ne suit pas un angle.
        # Il choisit une destination, puis avance vers cette destination.
        update_slime_random_movement(slime, self.random)

        # On copie la position logique vers le sprite affiché.
        slime_sprite.center_x = slime.x
        slime_sprite.center_y = slime.y

        # Animation temporaire.
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
        self.boomerang.state = BoomerangState.RETURNING

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

        # Pendant le retour, il peut encore tuer des ennemis.
        self._boomerang_hits_enemy()

    def _catch_boomerang(self) -> None:
        self.boomerang.state = BoomerangState.INACTIVE
        self.boomerang.distance_travelled = 0
        self.boomerang.position = self.player.position

    # ==================================================
    # Sword
    # ==================================================

    def _update_sword(self, delta_time: float) -> None:
        if self.sword.state != SwordState.ACTIVE:
            return

        self.sword.position = self.player.position
        self.sword.update_animation()

        self.sword.time += delta_time

        if self.sword.time >= SWORD_ATTACK_DURATION:
            self._stop_sword_attack()

        self._sword_hits_enemies()
        self._sword_hits_crystals()

    def _stop_sword_attack(self) -> None:
        self.sword.state = SwordState.INACTIVE
        self.sword.time = 0

    def _sword_hits_enemies(self) -> None:
        self._weapon_hits_spinners(self.sword)
        self._weapon_hits_bats(self.sword)
        self._weapon_hits_slimes(self.sword)

    def _sword_hits_crystals(self) -> None:
        crystals = self._collisions(self.sword, self.crystals)
        self._collect_crystals(crystals)

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
        # Les deux listes sont parallèles :
        # sprites[i] correspond à logic_objects[i].
        for i, sprite in enumerate(sprites):
            if sprite == target_sprite:
                sprites.pop(i)
                logic_objects.pop(i)
                return

    # ==================================================
    # Collisions du joueur
    # ==================================================

    def _handle_player_collisions(self) -> None:
        self._handle_player_collect_crystals()
        self._handle_player_death_collisions()

    def _handle_player_collect_crystals(self) -> None:
        crystals = self._collisions(self.player, self.crystals)
        self._collect_crystals(crystals)

    def _collect_crystals(
        self,
        crystals: list[arcade.TextureAnimationSprite],
    ) -> None:
        for crystal in crystals:
            crystal.remove_from_sprite_lists()
            arcade.play_sound(SOUND_COIN)
            self.score += 1

    def _handle_player_death_collisions(self) -> None:
        if self._player_touches_enemy():
            self._restart_game()
            return

        if self._player_touches_hole():
            self._restart_game()
            return

    def _player_touches_enemy(self) -> bool:
        # Le joueur meurt s'il touche un spinner, une bat ou un slime.
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