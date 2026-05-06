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
from boomerang import Boomerang, BoomerangState
from sword import Sword, SwordState


# ==================================================
# Constantes propres à GameView
# ==================================================
# Ces constantes évitent d'avoir des nombres "magiques" dans le code.
# Par exemple, écrire BOOMERANG_SPEED est plus clair qu'écrire 8 partout.

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
    # Cette enum indique quelle arme est actuellement sélectionnée.
    # Le joueur peut changer d'arme avec la touche R.
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

    active_weapon: ActiveWeapon
    boomerang: Boomerang
    boomerang_list: arcade.SpriteList[arcade.TextureAnimationSprite]

    sword: Sword
    sword_list: arcade.SpriteList[arcade.TextureAnimationSprite]

    physics_engine: Final[arcade.PhysicsEngineSimple]
    camera: Final[arcade.camera.Camera2D]
    ui_camera: Final[arcade.camera.Camera2D]

    def __init__(self, game_map: Map) -> None:
        # Initialisation obligatoire de arcade.View.
        super().__init__()

        # On garde la map, car elle sert à créer tout le jeu :
        # taille du monde, joueur, murs, cristaux, ennemis, etc.
        self.map = game_map

        # État général du jeu.
        self.background_color = arcade.csscolor.CORNFLOWER_BLUE
        self.score = 0

        # La map donne une taille en cases.
        # Le monde Arcade a besoin d'une taille en pixels.
        self.world_width = self.map.width * TILE_SIZE
        self.world_height = self.map.height * TILE_SIZE

        # Générateur aléatoire utilisé pour les chauves-souris.
        self.random = random.Random(None)

        # Le constructeur reste court.
        # Chaque ligne prépare une grande partie du jeu.
        self._setup_player()
        self._setup_weapons()
        self._setup_world()
        self._setup_spinners()
        self._setup_bats()
        self._setup_keyboard()
        self._setup_physics_and_cameras()

    # ==================================================
    # Setup général du jeu
    # ==================================================

    def _setup_player(self) -> None:
        # On crée le joueur à sa position de départ.
        # La position de départ est stockée dans la map en coordonnées de grille.
        self.player = Player(
            animation=ANIMATION_PLAYER_IDLE_DOWN,
            scale=SCALE,
            center_x=grid_to_pixels(self.map.player_start_x),
            center_y=grid_to_pixels(self.map.player_start_y),
        )

        # Même s'il n'y a qu'un seul joueur, Arcade le dessine plus facilement
        # s'il est dans une SpriteList.
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player)

    def _setup_weapons(self) -> None:
        # Au début du jeu, l'arme sélectionnée est le boomerang.
        self.active_weapon = ActiveWeapon.BOOMERANG

        # Le boomerang existe dès le début, mais il est inactif.
        # Sa classe ne prend pas center_x / center_y dans le constructeur,
        # donc on le crée d'abord, puis on le place sur le joueur.
        self.boomerang = Boomerang()
        self.boomerang.position = self.player.position

        # Même idée pour l'épée.
        self.sword = Sword()
        self.sword.position = self.player.position

        # Comme pour le joueur, on met les armes dans des SpriteList
        # pour pouvoir les dessiner facilement.
        self.boomerang_list = arcade.SpriteList()
        self.boomerang_list.append(self.boomerang)

        self.sword_list = arcade.SpriteList()
        self.sword_list.append(self.sword)

    def _setup_world(self) -> None:
        # Ces listes contiennent les éléments du décor.
        self.grounds = arcade.SpriteList(use_spatial_hash=True)
        self.walls = arcade.SpriteList(use_spatial_hash=True)
        self.crystals = arcade.SpriteList()
        self.holes = arcade.SpriteList()

        # On parcourt toute la map case par case.
        # Pour chaque case, on crée les sprites correspondants.
        for y in range(self.map.height):
            for x in range(self.map.width):
                self._create_cell_sprites(x, y)

    def _setup_spinners(self) -> None:
        # Les spinners ont deux parties :
        # - self.spinners : la logique du spinner
        # - self.spinner_sprites : l'image affichée du spinner
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
        # Même idée que les spinners :
        # - self.bats : logique
        # - self.bat_sprites : affichage
        self.bats = create_bats(self.map, self.random)
        self.bat_sprites = arcade.SpriteList()

        for bat in self.bats:
            self.bat_sprites.append(
                self._create_animated_sprite(
                    animation=ANIMATION_BAT,
                    x=bat.start_x,
                    y=bat.start_y,
                )
            )

    def _setup_keyboard(self) -> None:
        # Ces booléens mémorisent les touches actuellement enfoncées.
        # On ne déplace pas directement le joueur ici.
        # On stocke seulement l'état du clavier.
        self.right = False
        self.left = False
        self.up = False
        self.down = False

    def _setup_physics_and_cameras(self) -> None:
        # Le moteur physique empêche le joueur de traverser les murs.
        self.physics_engine = arcade.PhysicsEngineSimple(self.player, self.walls)

        # camera : caméra du monde, elle suit le joueur.
        # ui_camera : caméra de l'interface, elle reste fixe.
        self.camera = arcade.camera.Camera2D()
        self.ui_camera = arcade.camera.Camera2D()

    # ==================================================
    # Petites fonctions de création de sprites
    # ==================================================

    def _create_static_sprite(
        self,
        texture: arcade.Texture,
        x: int,
        y: int,
    ) -> arcade.Sprite:
        # Crée un sprite simple à partir d'une texture.
        # x et y sont en coordonnées de grille, donc on les convertit en pixels.
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
        # Crée un sprite animé à partir d'une animation.
        return arcade.TextureAnimationSprite(
            animation=animation,
            scale=SCALE,
            center_x=grid_to_pixels(x),
            center_y=grid_to_pixels(y),
        )

    def _create_cell_sprites(self, x: int, y: int) -> None:
        # Chaque case reçoit toujours de l'herbe.
        # Ensuite, selon le type de case, on ajoute un élément par-dessus.
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
        # Cette méthode est appelée quand la vue devient active.
        # On adapte la fenêtre à la taille du monde, sans dépasser les max.
        self.window.width = min(MAX_WINDOW_WIDTH, self.world_width)
        self.window.height = min(MAX_WINDOW_HEIGHT, self.world_height)

    def on_draw(self) -> None:
        # Cette méthode dessine tout à l'écran.
        # Arcade l'appelle automatiquement.
        self.clear()

        # D'abord, on dessine le monde avec la caméra du monde.
        with self.camera.activate():
            self._draw_world()

        # Ensuite, on dessine l'interface avec une caméra fixe.
        with self.ui_camera.activate():
            self._draw_ui()

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        # Cette méthode est appelée quand une touche est enfoncée.
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

        # Après chaque touche, on recalcule le mouvement du joueur.
        self._update_player_movement()

    def on_key_release(self, symbol: int, modifiers: int) -> None:
        # Cette méthode est appelée quand une touche est relâchée.
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
        # Cette méthode est appelée à chaque frame.
        # C'est elle qui fait avancer le jeu.
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
        # On dessine d'abord le sol, puis les objets, puis le joueur et les armes.
        self.grounds.draw()
        self.walls.draw()
        self.holes.draw()
        self.crystals.draw()

        self.spinner_sprites.draw()
        self.bat_sprites.draw()

        self.player_list.draw()

        # Le boomerang est dessiné seulement s'il est actif.
        if self.boomerang.state != BoomerangState.INACTIVE:
            self.boomerang_list.draw()

        # L'épée est dessinée seulement pendant l'attaque.
        if self.sword.state == SwordState.ACTIVE:
            self.sword_list.draw()

    def _draw_ui(self) -> None:
        # L'interface reste fixe à l'écran grâce à ui_camera.
        score_text = arcade.Text(
            f"Score: {self.score}",
            10,
            10,
            arcade.color.WHITE,
            20,
        )
        score_text.draw()

        # On affiche aussi l'arme actuellement sélectionnée.
        # Comme ça, quand on appuie sur R, on voit directement le changement.
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
        # On transmet l'état du clavier au joueur.
        # Le joueur décide ensuite sa vitesse dans player.py.
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
        # La touche D utilise l'arme actuellement sélectionnée.
        if self.active_weapon == ActiveWeapon.BOOMERANG:
            self._launch_boomerang()
        elif self.active_weapon == ActiveWeapon.SWORD:
            self._start_sword_attack()

    def _all_weapons_are_inactive(self) -> bool:
        # Renvoie True si aucune arme n'est en cours d'utilisation.
        return (
            self.boomerang.state == BoomerangState.INACTIVE
            and self.sword.state == SwordState.INACTIVE
        )

    def _launch_boomerang(self) -> None:
        # On peut lancer le boomerang seulement s'il est inactif.
        if self.boomerang.state != BoomerangState.INACTIVE:
            return

        # Le boomerang part depuis le joueur.
        self.boomerang.position = self.player.position

        # Il part dans la direction où regarde le joueur.
        self.boomerang.direction = self.player.direction

        # On initialise son état de lancement.
        self.boomerang.state = BoomerangState.LAUNCHING
        self.boomerang.distance_travelled = 0

    def _start_sword_attack(self) -> None:
        # L'épée ne peut être utilisée que si les deux armes sont libres.
        if not self._all_weapons_are_inactive():
            return

        # L'épée commence sur le joueur et dans sa direction.
        self.sword.position = self.player.position
        self.sword.direction = self.player.direction
        self.sword.update_direction_animation()

        # L'attaque commence.
        self.sword.state = SwordState.ACTIVE
        self.sword.time = 0

    # ==================================================
    # Update général
    # ==================================================

    def _update_player(self) -> None:
        # Le moteur physique applique le mouvement du joueur
        # tout en l'empêchant de traverser les murs.
        self.physics_engine.update()

        # On choisit la bonne animation selon la direction et le mouvement.
        self.player.update_direction_animation()

        # On fait avancer l'animation.
        self.player.update_animation()

    def _update_animations(self) -> None:
        # Tous les sprites animés doivent être mis à jour à chaque frame.
        for crystal in self.crystals:
            crystal.update_animation()

        for spinner_sprite in self.spinner_sprites:
            spinner_sprite.update_animation()

        if self.boomerang.state != BoomerangState.INACTIVE:
            self.boomerang.update_animation()

    def _update_enemies(self) -> None:
        # Cette méthode regroupe tous les ennemis.
        self._update_spinners()
        self._update_bats()

    def _update_weapons(self, delta_time: float) -> None:
        # Cette méthode regroupe toutes les armes.
        self._update_boomerang()
        self._update_sword(delta_time)

    # ==================================================
    # Spinners
    # ==================================================

    def _update_spinners(self) -> None:
        # self.spinners contient la logique.
        # self.spinner_sprites contient l'affichage.
        # zip permet de les parcourir ensemble.
        for spinner, sprite in zip(self.spinners, self.spinner_sprites):
            self._update_spinner(spinner, sprite)

    def _update_spinner(
        self,
        spinner: Spinner,
        sprite: arcade.TextureAnimationSprite,
    ) -> None:
        # Un spinner est soit horizontal, soit vertical.
        if spinner.horizontal:
            self._update_horizontal_spinner(spinner, sprite)
        else:
            self._update_vertical_spinner(spinner, sprite)

    def _update_horizontal_spinner(
        self,
        spinner: Spinner,
        sprite: arcade.TextureAnimationSprite,
    ) -> None:
        # POSITIF = droite, NEGATIF = gauche.
        if spinner.direction == SpinnerDirection.POSITIF:
            self._move_spinner_right(spinner, sprite)
        else:
            self._move_spinner_left(spinner, sprite)

    def _update_vertical_spinner(
        self,
        spinner: Spinner,
        sprite: arcade.TextureAnimationSprite,
    ) -> None:
        # POSITIF = haut, NEGATIF = bas.
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
    # Chauves-souris
    # ==================================================

    def _update_bats(self) -> None:
        # Chaque bat a une partie logique et un sprite correspondant.
        for bat, bat_sprite in zip(self.bats, self.bat_sprites):
            self._update_bat(bat, bat_sprite)

    def _update_bat(
        self,
        bat: Bat,
        bat_sprite: arcade.TextureAnimationSprite,
    ) -> None:
        # 1. L'animation visuelle avance.
        bat_sprite.update_animation()

        # 2. La bat peut changer légèrement de direction.
        self._maybe_change_bat_direction(bat)

        # 3. On calcule la position qu'elle veut atteindre.
        new_x, new_y = self._compute_next_bat_position(bat, bat_sprite)

        # 4. Si cette position sort de sa zone, on fait rebondir la bat.
        new_x, new_y = self._bounce_bat_if_needed(
            bat,
            bat_sprite,
            new_x,
            new_y,
        )

        # 5. On applique la position finale.
        bat_sprite.center_x = new_x
        bat_sprite.center_y = new_y

    def _maybe_change_bat_direction(self, bat: Bat) -> None:
        # Chaque bat a un compteur.
        # Quand le compteur arrive à 0, elle change un peu d'angle.
        bat.frames_direction_change -= 1

        if bat.frames_direction_change <= 0:
            bat.angle += self.random.uniform(-0.5, 0.5)
            bat.frames_direction_change = BAT_DIRECTION_CHANGE

    def _compute_next_bat_position(
        self,
        bat: Bat,
        bat_sprite: arcade.TextureAnimationSprite,
    ) -> tuple[float, float]:
        # La bat avance selon un angle.
        #
        # cos(angle) donne la partie horizontale du mouvement.
        # sin(angle) donne la partie verticale du mouvement.
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
        # Les limites de bat.bounds sont en coordonnées de grille.
        # On les convertit en pixels pour comparer avec la position du sprite.
        min_x = grid_to_pixels(int(bat.bounds.min_x))
        max_x = grid_to_pixels(int(bat.bounds.max_x))
        min_y = grid_to_pixels(int(bat.bounds.min_y))
        max_y = grid_to_pixels(int(bat.bounds.max_y))

        # Si la bat sort à gauche ou à droite,
        # on inverse la composante horizontale de son angle.
        if new_x < min_x or new_x > max_x:
            bat.angle = math.pi - bat.angle
            new_x, new_y = self._compute_next_bat_position(bat, bat_sprite)

        # Si la bat sort en haut ou en bas,
        # on inverse la composante verticale de son angle.
        if new_y < min_y or new_y > max_y:
            bat.angle = -bat.angle
            new_x, new_y = self._compute_next_bat_position(bat, bat_sprite)

        return new_x, new_y

    # ==================================================
    # Boomerang
    # ==================================================

    def _update_boomerang(self) -> None:
        # Le boomerang est une machine à états :
        # INACTIVE -> LAUNCHING -> RETURNING -> INACTIVE
        if self.boomerang.state == BoomerangState.LAUNCHING:
            self._update_boomerang_launching()

        elif self.boomerang.state == BoomerangState.RETURNING:
            self._update_boomerang_returning()

    def _update_boomerang_launching(self) -> None:
        # Pendant cette phase, le boomerang part en ligne droite.
        self._move_boomerang_forward()
        self.boomerang.distance_travelled += BOOMERANG_SPEED

        # Le boomerang revient s'il a atteint sa distance maximale.
        if self.boomerang.distance_travelled >= BOOMERANG_MAX_DISTANCE:
            self._start_boomerang_return()

        # Le boomerang revient aussi s'il touche un mur.
        if self._boomerang_hits_wall():
            self._start_boomerang_return()

        # Le boomerang revient aussi s'il touche un ennemi.
        if self._boomerang_hits_enemy():
            self._start_boomerang_return()

    def _move_boomerang_forward(self) -> None:
        # La direction du boomerang a été copiée depuis le joueur au moment du lancer.
        if self.boomerang.direction == Direction.NORTH:
            self.boomerang.center_y += BOOMERANG_SPEED
        elif self.boomerang.direction == Direction.SOUTH:
            self.boomerang.center_y -= BOOMERANG_SPEED
        elif self.boomerang.direction == Direction.EAST:
            self.boomerang.center_x += BOOMERANG_SPEED
        elif self.boomerang.direction == Direction.WEST:
            self.boomerang.center_x -= BOOMERANG_SPEED

    def _start_boomerang_return(self) -> None:
        # Passe le boomerang en mode retour.
        self.boomerang.state = BoomerangState.RETURNING

    def _boomerang_hits_wall(self) -> bool:
        # Renvoie True si le boomerang touche un mur.
        return self._has_collision(self.boomerang, self.walls)

    def _boomerang_hits_enemy(self) -> bool:
        # Le boomerang peut tuer les bats et les spinners.
        killed_bat = self._weapon_hits_bats(self.boomerang)
        killed_spinner = self._weapon_hits_spinners(self.boomerang)

        return killed_bat or killed_spinner

    def _update_boomerang_returning(self) -> None:
        # Pendant le retour, le boomerang se dirige vers la position actuelle du joueur.
        dx = self.player.center_x - self.boomerang.center_x
        dy = self.player.center_y - self.boomerang.center_y

        distance = math.sqrt(dx**2 + dy**2)

        # S'il est assez proche du joueur, on considère qu'il est attrapé.
        if distance <= BOOMERANG_CATCH_DISTANCE:
            self._catch_boomerang()
            return

        # dx / distance et dy / distance donnent une direction de longueur 1.
        # On multiplie par BOOMERANG_SPEED pour garder une vitesse constante.
        self.boomerang.center_x += BOOMERANG_SPEED * dx / distance
        self.boomerang.center_y += BOOMERANG_SPEED * dy / distance

        # Même pendant le retour, le boomerang peut tuer des ennemis.
        self._boomerang_hits_enemy()

    def _catch_boomerang(self) -> None:
        # Le boomerang redevient disponible.
        self.boomerang.state = BoomerangState.INACTIVE
        self.boomerang.distance_travelled = 0
        self.boomerang.position = self.player.position

    # ==================================================
    # Épée
    # ==================================================

    def _update_sword(self, delta_time: float) -> None:
        # Si l'épée n'est pas active, il n'y a rien à faire.
        if self.sword.state != SwordState.ACTIVE:
            return

        # Pendant l'attaque, l'épée reste centrée sur le joueur.
        self.sword.position = self.player.position

        # On fait avancer son animation.
        self.sword.update_animation()

        # On augmente le temps écoulé depuis le début de l'attaque.
        self.sword.time += delta_time

        # Après 0.3 seconde, l'attaque se termine.
        if self.sword.time >= SWORD_ATTACK_DURATION:
            self._stop_sword_attack()

        # L'épée peut tuer les ennemis et collecter les cristaux.
        self._sword_hits_enemies()
        self._sword_hits_crystals()

    def _stop_sword_attack(self) -> None:
        # L'épée redevient inactive.
        self.sword.state = SwordState.INACTIVE
        self.sword.time = 0

    def _sword_hits_enemies(self) -> None:
        # L'épée tue les spinners et les bats touchés.
        self._weapon_hits_spinners(self.sword)
        self._weapon_hits_bats(self.sword)

    def _sword_hits_crystals(self) -> None:
        # L'épée peut aussi collecter les cristaux touchés.
        crystals = self._collisions(self.sword, self.crystals)
        self._collect_crystals(crystals)

    # ==================================================
    # Collisions avec armes
    # ==================================================

    def _weapon_hits_spinners(self, weapon: arcade.Sprite) -> bool:
        # Supprime tous les spinners touchés par une arme.
        colliding_spinners = self._collisions(weapon, self.spinner_sprites)

        for spinner_sprite in colliding_spinners:
            self._remove_spinner_sprite(spinner_sprite)

        return len(colliding_spinners) > 0

    def _weapon_hits_bats(self, weapon: arcade.Sprite) -> bool:
        # Supprime toutes les bats touchées par une arme.
        colliding_bats = self._collisions(weapon, self.bat_sprites)

        for bat_sprite in colliding_bats:
            self._remove_bat_sprite(bat_sprite)

        return len(colliding_bats) > 0

    def _remove_spinner_sprite(self, spinner_sprite: arcade.Sprite) -> None:
        # On doit supprimer le spinner dans deux listes :
        # - spinner_sprites : affichage
        # - spinners : logique
        self._remove_sprite_and_matching_logic(
            target_sprite=spinner_sprite,
            sprites=self.spinner_sprites,
            logic_objects=self.spinners,
        )

    def _remove_bat_sprite(self, bat_sprite: arcade.Sprite) -> None:
        # Même principe pour les bats.
        self._remove_sprite_and_matching_logic(
            target_sprite=bat_sprite,
            sprites=self.bat_sprites,
            logic_objects=self.bats,
        )

    def _remove_sprite_and_matching_logic(
        self,
        target_sprite: arcade.Sprite,
        sprites: arcade.SpriteList,
        logic_objects: list,
    ) -> None:
        # Les listes logique et visuelle sont parallèles.
        # Cela veut dire :
        # sprites[0] correspond à logic_objects[0]
        # sprites[1] correspond à logic_objects[1]
        # etc.
        #
        # Donc quand on supprime un sprite, on supprime l'objet logique au même indice.
        for i, sprite in enumerate(sprites):
            if sprite == target_sprite:
                sprites.pop(i)
                logic_objects.pop(i)
                return

    # ==================================================
    # Collisions du joueur
    # ==================================================

    def _handle_player_collisions(self) -> None:
        # Cette méthode regroupe toutes les collisions importantes du joueur.
        self._handle_player_collect_crystals()
        self._handle_player_death_collisions()

    def _handle_player_collect_crystals(self) -> None:
        # Si le joueur touche un cristal, il le collecte.
        crystals = self._collisions(self.player, self.crystals)
        self._collect_crystals(crystals)

    def _collect_crystals(
        self,
        crystals: list[arcade.TextureAnimationSprite],
    ) -> None:
        # Pour chaque cristal collecté :
        # - on le retire de l'écran
        # - on joue un son
        # - on augmente le score
        for crystal in crystals:
            crystal.remove_from_sprite_lists()
            arcade.play_sound(SOUND_COIN)
            self.score += 1

    def _handle_player_death_collisions(self) -> None:
        # Si le joueur touche un danger, on recommence la partie.
        if self._player_touches_enemy():
            self._restart_game()
            return

        if self._player_touches_hole():
            self._restart_game()
            return

    def _player_touches_enemy(self) -> bool:
        # Le joueur meurt s'il touche un spinner ou une bat.
        return (
            self._has_collision(self.player, self.spinner_sprites)
            or self._has_collision(self.player, self.bat_sprites)
        )

    def _player_touches_hole(self) -> bool:
        # On vérifie d'abord les trous proches avec Arcade.
        nearby_holes = self._collisions(self.player, self.holes)

        # Puis on utilise une distance plus précise.
        for hole in nearby_holes:
            if math.dist(self.player.position, hole.position) <= HOLE_DEATH_DISTANCE:
                return True

        return False

    # ==================================================
    # Petites fonctions générales de collision
    # ==================================================

    def _collisions(
        self,
        sprite: arcade.Sprite,
        sprite_list: arcade.SpriteList,
    ) -> list[arcade.Sprite]:
        # Fonction générale :
        # renvoie la liste des sprites touchés par sprite.
        return arcade.check_for_collision_with_list(sprite, sprite_list)

    def _has_collision(
        self,
        sprite: arcade.Sprite,
        sprite_list: arcade.SpriteList,
    ) -> bool:
        # Fonction générale :
        # renvoie True si sprite touche au moins un élément de sprite_list.
        return len(self._collisions(sprite, sprite_list)) > 0

    # ==================================================
    # Reset du jeu
    # ==================================================

    def _restart_game(self) -> None:
        # Pour recommencer la partie, on recrée une nouvelle GameView avec la même map.
        new_view = GameView(self.map)
        self.window.show_view(new_view)