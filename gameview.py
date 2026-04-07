from typing import Final
import arcade
import math

from constants import *
from textures import *

from map import Map, GridCell
from spinner import create_spinners, Direction as SpinnerDirection, Spinner
from player import Player
from direction import Direction
from boomerang import Boomerang, BoomerangState
from sword import Sword, SwordState
from bat import *
from enum import Enum


def grid_to_pixels(i: int) -> int:
    """
    Cette fonction sert juste à convertir une coordonnée de grille en pixels.
    Par exemple, si une case est à x = 3 dans la map, ça me donne la vraie
    position en pixels au centre de cette case.
    """
    return i * TILE_SIZE + (TILE_SIZE // 2)

class ActiveWeapon(Enum):
    BOOMERANG = 1
    SWORD = 2

class GameView(arcade.View):
    """Main in-game view."""

    # Ici je déclare les attributs principaux de ma vue.
    # Ce n'est pas obligatoire pour que le code marche, mais ça aide à rendre
    # le code plus lisible et plus propre.
    world_width: Final[int]
    world_height: Final[int]
    player: Final[Player]
    player_list: Final[arcade.SpriteList[Player]]
    grounds: Final[arcade.SpriteList[arcade.Sprite]]
    walls: Final[arcade.SpriteList[arcade.Sprite]]
    crystals: Final[arcade.SpriteList[arcade.TextureAnimationSprite]]
    holes: Final[arcade.SpriteList[arcade.Sprite]]
    score: int
    spinners: list[Spinner]
    spinner_sprites: arcade.SpriteList[arcade.TextureAnimationSprite]
    active_weapon : ActiveWeapon
    boomerang: Boomerang
    boomerang_list: arcade.SpriteList[arcade.TextureAnimationSprite]
    sword : Sword
    sword_list : arcade.SpriteList[arcade.TextureAnimationSprite]
    physics_engine: Final[arcade.PhysicsEngineSimple]
    camera: Final[arcade.camera.Camera2D]
    ui_camera: Final[arcade.camera.Camera2D]

    def __init__(self, map: Map) -> None:
        # Toujours commencer par initialiser la vue arcade.
        super().__init__()

        # Je garde la map en mémoire car j'en ai besoin à plusieurs endroits
        # (position initiale du joueur, taille du monde, contenu des cases, etc.)
        self.map = map

        # Couleur de fond du jeu
        self.background_color = arcade.csscolor.CORNFLOWER_BLUE

        # Score de départ
        self.score = 0

        # Taille du monde en pixels
        # Je pars de la taille de la map en nombre de cases,
        # puis je multiplie par TILE_SIZE.
        self.world_width = self.map.width * TILE_SIZE
        self.world_height = self.map.height * TILE_SIZE

        # =========================
        # Création du joueur
        # =========================
        # Je crée le joueur à sa position de départ dans la map.
        # Au début il regarde vers le bas, donc je mets l'animation idle down.
        self.player = Player(
            animation=ANIMATION_PLAYER_IDLE_DOWN,
            scale=SCALE,
            center_x=grid_to_pixels(self.map.player_start_x),
            center_y=grid_to_pixels(self.map.player_start_y),
        )

        # Je mets le joueur dans une SpriteList pour pouvoir le dessiner facilement.
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player)

        # =========================
        # Création du boomerang
        # =========================
        # Je crée le boomerang au départ à la position du joueur.
        # Il est créé tout de suite, mais son état initial est INACTIVE,
        # donc il ne sera pas affiché tant qu'on ne l'a pas lancé.
        self.boomerang = Boomerang(
            center_x=grid_to_pixels(self.map.player_start_x),
            center_y=grid_to_pixels(self.map.player_start_y),
        )
        self.sword = Sword(
            center_x=grid_to_pixels(self.map.player_start_x),
            center_y=grid_to_pixels(self.map.player_start_y),
        )

        # Même idée que pour le joueur : je mets dans une liste de sprites le boomerang et l'épée
        self.boomerang_list = arcade.SpriteList()
        self.boomerang_list.append(self.boomerang)
        self.sword_list= arcade.SpriteList()
        self.sword_list.append(self.sword)

        # l'arme active au début est le boomerang, c'est cebque je précise ici :
        self.active_weapon = ActiveWeapon.BOOMERANG

        # =========================
        # Création du décor et des objets du monde
        # =========================
        self.grounds = arcade.SpriteList(use_spatial_hash=True)
        self.walls = arcade.SpriteList(use_spatial_hash=True)
        self.crystals = arcade.SpriteList()
        self.holes = arcade.SpriteList()

        # Ici je parcours toute la map case par case.
        for x in range(self.map.width):
            for y in range(self.map.height):

                # Dans tous les cas, je mets d'abord de l'herbe au sol.
                sprite = arcade.Sprite(
                    TEXTURE_GRASS,
                    scale=SCALE,
                    center_x=grid_to_pixels(x),
                    center_y=grid_to_pixels(y),
                )
                self.grounds.append(sprite)

                # Ensuite je regarde ce qu'il y a réellement dans la case.
                cell = self.map.get(x, y)

                # Si c'est un buisson, je crée un mur.
                if cell == GridCell.BUSH:
                    sprite = arcade.Sprite(
                        TEXTURE_BUSH,
                        scale=SCALE,
                        center_x=grid_to_pixels(x),
                        center_y=grid_to_pixels(y),
                    )
                    self.walls.append(sprite)

                # Si c'est un cristal, je crée un sprite animé.
                elif cell == GridCell.CRYSTAL:
                    sprite = arcade.TextureAnimationSprite(
                        animation=ANIMATION_CRYSTAL,
                        scale=SCALE,
                        center_x=grid_to_pixels(x),
                        center_y=grid_to_pixels(y),
                    )
                    self.crystals.append(sprite)

                # Si c'est un trou, je crée son sprite.
                elif cell == GridCell.HOLE:
                    sprite = arcade.Sprite(
                        TEXTURE_HOLE,
                        scale=SCALE,
                        center_x=grid_to_pixels(x),
                        center_y=grid_to_pixels(y),
                    )
                    self.holes.append(sprite)

        # =========================
        # Création des spinners
        # =========================
        # Ici create_spinners(self.map) crée la partie logique des spinners
        # (leur position, leur direction, leurs limites, etc.)
        self.spinners = create_spinners(self.map)

        # Ensuite je crée leur partie visuelle : les sprites animés affichés à l'écran.
        self.spinner_sprites = arcade.SpriteList()
        for spinner in self.spinners:
            sprite = arcade.TextureAnimationSprite(
                animation=ANIMATION_SPINNER,
                scale=SCALE,
                center_x=grid_to_pixels(spinner.x),
                center_y=grid_to_pixels(spinner.y),
            )
            self.spinner_sprites.append(sprite)
        # =========================
        # Création des chauve-souris
        # =========================
        # Ici create_bats(self.map) crée la partie logique des bats
        # (leur position, leur direction, leurs limites, etc.)
        self.val = random.Random(None)
        self.bats = create_bats(self.map, self.val)
        # Ensuite, je crée la partie visuelle : sprites.
        self.bat_sprites = arcade.SpriteList()
        for bat in self.bats :
            bat_sprite = arcade.TextureAnimationSprite(
                animation = ANIMATION_BAT,
                scale= SCALE,
                center_x=grid_to_pixels(bat.start_x),
                center_y=grid_to_pixels(bat.start_y),
            )
            self.bat_sprites.append(bat_sprite)

        # =========================
        # État du clavier
        # =========================
        # Ces booléens me servent à savoir quelles touches sont actuellement enfoncées.
        self.right = False
        self.left = False
        self.up = False
        self.down = False

        # =========================
        # Physique et caméras
        # =========================
        # Le moteur physique empêche le joueur de traverser les murs.
        self.physics_engine = arcade.PhysicsEngineSimple(self.player, self.walls)

        # camera = caméra du monde
        # ui_camera = caméra fixe pour l'interface (score)
        self.camera = arcade.camera.Camera2D()
        self.ui_camera = arcade.camera.Camera2D()

    def _remove_spinner_sprite(self, spinner_sprite: arcade.Sprite) -> None:
        """
        Cette méthode enlève un spinner à la fois du visuel et de la logique.
        J'en ai besoin quand une arme tue un spinner.

        Pourquoi enlever dans les deux listes ?
        - self.spinner_sprites = partie affichée
        - self.spinners = partie logique
        Si j'enlevais seulement le sprite, j'aurais un décalage entre les deux.
        """
        for i, sprite in enumerate(self.spinner_sprites):
            if sprite == spinner_sprite:
                self.spinner_sprites.pop(i)
                self.spinners.pop(i)
                return

    def _remove_bat_sprite (self, bat_sprite : arcade.TextureAnimationSprite):
        """
        Cette méthode enlève une chauve-souris à la fois du visuel et de la logique.
        J'en ai besoin quand une arme en tue une.

        Pourquoi enlever dans les deux listes ?
        - self.bat_sprites = partie affichée
        - self.bats = partie logique
        Si j'enlevais seulement le sprite, j'aurais un décalage entre les deux.
        """
        for i, sprite in enumerate(self.bat_sprites):
            if sprite == bat_sprite:
                self.bat_sprites.pop(i)
                self.bats.pop(i)
                return

    def on_show_view(self) -> None:
        """
        Cette méthode est appelée automatiquement quand cette vue devient active.
        Ici j'ajuste la taille de la fenêtre à la taille du monde,
        sans dépasser les dimensions maximales prévues.
        """
        self.window.width = min(MAX_WINDOW_WIDTH, self.world_width)
        self.window.height = min(MAX_WINDOW_HEIGHT, self.world_height)

    def on_draw(self) -> None:
        """Cette méthode dessine tout ce qu'on voit à l'écran."""
        self.clear()

        # =========================
        # Dessin du monde
        # =========================
        # Avec la caméra du monde, je dessine tout ce qui se déplace dans le jeu.
        with self.camera.activate():
            self.grounds.draw()
            self.walls.draw()
            self.holes.draw()
            self.player_list.draw()
            self.crystals.draw()
            self.spinner_sprites.draw()
            self.bat_sprites.draw()

            # Le boomerang n'est dessiné que s'il n'est pas inactif.
            # Donc au début il n'apparaît pas.
            if self.boomerang.state != BoomerangState.INACTIVE:
                self.boomerang_list.draw()
            if self.sword.state == SwordState.ACTIVE :
                self.sword_list.draw()

        # =========================
        # Dessin de l'interface
        # =========================
        # Ici j'utilise une autre caméra pour que le score reste fixe à l'écran.
        with self.ui_camera.activate():
            score_text = arcade.Text(
                f"Score: {self.score}",
                10,
                10,
                arcade.color.WHITE,
                20
            )
            score_text.draw()

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        """
        Cette méthode est appelée quand une touche est enfoncée.
        Je mets à jour l'état du clavier et je gère aussi le lancement du boomerang.
        """
        match symbol:
            case arcade.key.RIGHT:
                self.right = True
            case arcade.key.LEFT:
                self.left = True
            case arcade.key.UP:
                self.up = True
            case arcade.key.DOWN:
                self.down = True
            # je code ma touche R :
            case arcade.key.R:
                # je limite son usage à : les deux armes sont inactives, pour éviter un changement alors quye le boomerang est en plein vol par exemple
                if self.boomerang.state==BoomerangState.INACTIVE and self.sword.state==SwordState.INACTIVE :
                    # le changement se fait naturellement d'une arme à l'autre :
                    if self.active_weapon == ActiveWeapon.BOOMERANG :
                        self.active_weapon = ActiveWeapon.SWORD
                    else :
                        self.active_weapon = ActiveWeapon.BOOMERANG


            case arcade.key.D:
                if self.active_weapon== ActiveWeapon.BOOMERANG :
                    # Le boomerang ne peut être lancé que s'il est actuellement inactif.
                    if self.boomerang.state == BoomerangState.INACTIVE:
                        # Il passe à l'état LAUNCHING
                        self.boomerang.state = BoomerangState.LAUNCHING

                        # Il part depuis la position actuelle du joueur
                        self.boomerang.position = self.player.position

                        # Il part dans la direction dans laquelle regarde le joueur
                        self.boomerang.direction = self.player.direction

                        # Je remets la distance parcourue à zéro pour ce nouveau lancer
                        self.boomerang.distance_travelled = 0
                elif self.active_weapon == ActiveWeapon.SWORD :
                    # L'épée ne peut être utilisée que si elle est actuellement inactive ET le boomerang aussi :
                    if self.sword.state == SwordState.INACTIVE and self.boomerang.state== BoomerangState.INACTIVE :

                        # elle se situe à la position actuelle du joueur
                        self.sword.position = self.player.position

                        # elle est orientée selon la direction dans laquelle regarde le joueur
                        self.sword.direction = self.player.direction

                        # je dois mettre à jour l'animation selon la nouvelle direction :
                        self.sword.update_direction_animation()

                        # elle passe à l'état actif :
                        self.sword.state = SwordState.ACTIVE

                        # Je remets le temps écoulé à 0 :
                        self.sword.time = 0

            case arcade.key.ESCAPE:
                # Permet de relancer la partie
                new_view = GameView(self.map)
                self.window.show_view(new_view)

        # Après chaque changement de touche, je recalcule le mouvement du joueur.
        self.player.update_movement(self.right, self.left, self.up, self.down)

    def on_key_release(self, symbol: int, modifiers: int) -> None:
        """
        Cette méthode est appelée quand une touche est relâchée.
        Je remets le booléen correspondant à False.
        """
        match symbol:
            case arcade.key.RIGHT:
                self.right = False
            case arcade.key.LEFT:
                self.left = False
            case arcade.key.UP:
                self.up = False
            case arcade.key.DOWN:
                self.down = False

        # Je recalcule le mouvement après le relâchement d'une touche.
        self.player.update_movement(self.right, self.left, self.up, self.down)

    def on_update(self, delta_time: float) -> None:
        """
        Cette méthode est appelée à chaque frame.
        C'est vraiment ici que le jeu "avance" :
        mouvements, animations, collisions, score, boomerang, etc.
        """
        # =========================
        # Mise à jour du joueur
        # =========================
        self.physics_engine.update()

        # D'abord je choisis la bonne animation en fonction
        # de la direction et de si le joueur bouge ou non.
        self.player.update_direction_animation()

        # Ensuite je fais avancer l'animation.
        self.player.update_animation()

        # Mise à jour des animations des cristaux
        for crystal in self.crystals:
            crystal.update_animation()

        # Mise à jour des animations des spinners
        for spinner_sprite in self.spinner_sprites:
            spinner_sprite.update_animation()

        # Mise à jour de l'animation du boomerang seulement s'il est visible
        if self.boomerang.state != BoomerangState.INACTIVE:
            self.boomerang.update_animation()

        # =========================
        # Déplacement des spinners
        # =========================
        # Ici je fais avancer chaque spinner entre ses limites.
        # S'il atteint sa limite max, il repart dans l'autre sens, et inversement.
        for i in range(len(self.spinners)):
            spinner = self.spinners[i]
            sprite = self.spinner_sprites[i]

            if spinner.horizontal:
                if spinner.direction == SpinnerDirection.POSITIF:
                    sprite.center_x += SPINNER_MOVEMENT_SPEED

                    if sprite.center_x >= grid_to_pixels(spinner.limites.max_x):
                        sprite.center_x = grid_to_pixels(spinner.limites.max_x)
                        spinner.direction = SpinnerDirection.NEGATIF
                else:
                    sprite.center_x -= SPINNER_MOVEMENT_SPEED

                    if sprite.center_x <= grid_to_pixels(spinner.limites.min_x):
                        sprite.center_x = grid_to_pixels(spinner.limites.min_x)
                        spinner.direction = SpinnerDirection.POSITIF

            else:
                if spinner.direction == SpinnerDirection.POSITIF:
                    sprite.center_y += SPINNER_MOVEMENT_SPEED

                    if sprite.center_y >= grid_to_pixels(spinner.limites.max_y):
                        sprite.center_y = grid_to_pixels(spinner.limites.max_y)
                        spinner.direction = SpinnerDirection.NEGATIF
                else:
                    sprite.center_y -= SPINNER_MOVEMENT_SPEED

                    if sprite.center_y <= grid_to_pixels(spinner.limites.min_y):
                        sprite.center_y = grid_to_pixels(spinner.limites.min_y)
                        spinner.direction = SpinnerDirection.POSITIF
        # =========================
        # Déplacement des chauve-souris
        # =========================
        # Ici je fais avancer chaque chauve-souris entre ses limites, à vitesse constante.
        # Il arrive qu'elle modifie sa direction aléatoirement (comme demandé) pour simuler un mvt naturel.
        # si elle atteint les limites du rectangle d'action, elle rebondit et changeant de direction, à l'interieur
        # de la zone d'action toujours.

        # je choisis de parcourir la longueur de la liste, car la liste logique et visuelle ont la mm longueur,
        # de cette façon je parcours les deux en meme temps.
        for i in range(len(self.bats)):
            bat= self.bats[i]
            bat_sprite = self.bat_sprites[i]
            # je mets à jour son animation :
            bat_sprite.update_animation()
            # et donc, comme j'avance d'un frame, j'actualise leur compteur :
            bat.frames_direction_change -=1
            # dès qu'il ne reste plus de frames avant changement, on change de direction :
            if bat.frames_direction_change <= 0 :
                # je modifie légèrement l'angle
                bat.angle+=self.val.uniform(-0.5,0.5)
                # je remets le compteu rde frames à son état initial :
                bat.frames_direction_change = BAT_DIRECTION_CHANGE
            # à présent, je dois calculer le déplacement en fonction de l'angle et de la vitesse
            # c'est simplement des maths, on emploie des cosinus (horizontal) et des sinus (vertical) comme suit :
            dx = bat.speed*math.cos(bat.angle)
            dy = bat.speed*math.sin(bat.angle)
            # la nouvelle position ainsi caclulée est :
            new_x = bat_sprite.center_x + dx
            new_y = bat_sprite.center_y + dy
            # le problème : on ne sait pas si on sort de la zone, j'y remédie donc comme suit :
            # d'abord, je convertis les limites de la zone d'action en pixels pour pouvoir comparer :
            min_x = grid_to_pixels(bat.bounds.min_x)
            min_y = grid_to_pixels(bat.bounds.min_y)
            max_x = grid_to_pixels(bat.bounds.max_x)
            max_y = grid_to_pixels(bat.bounds.max_y)
            # la première exception est que la nouvelle position horizontale (new_x) est en dehors de l'intervalle :
            if new_x<min_x or new_x >max_x :
                # trigonométrie : la chauve-souris repartira dans l'autre sens par inversion du signe du cos
                bat.angle = math.pi - bat.angle
                new_x = bat_sprite.center_x + bat.speed*math.cos(bat.angle)
                new_y = bat_sprite.center_y + bat.speed*math.sin(bat.angle)
            # il reste à vérifier la même chose mais verticalement :
            if new_y < min_y or new_y > max_y :
                # encore une fois, c'est de la trigo, il faut qu'on inverse le signe du sin mais garder le cos qui est bon.
                bat.angle = - bat.angle
                new_x = bat_sprite.center_x + bat.speed*math.cos(bat.angle)
                new_y = bat_sprite.center_y + bat.speed*math.sin(bat.angle)
            # maintenant qu'on a tout vérifié, on peut mettre à jour la position de la chauve-souris :
            bat_sprite.center_x = new_x
            bat_sprite.center_y = new_y



        # =========================
        # Gestion du boomerang : phase de lancement
        # =========================
        if self.boomerang.state == BoomerangState.LAUNCHING:

            # Pendant le lancement, le boomerang part en ligne droite
            # dans la direction choisie au moment où on a appuyé sur D.
            if self.boomerang.direction == Direction.NORTH:
                self.boomerang.center_y += 8
            elif self.boomerang.direction == Direction.SOUTH:
                self.boomerang.center_y -= 8
            elif self.boomerang.direction == Direction.EAST:
                self.boomerang.center_x += 8
            elif self.boomerang.direction == Direction.WEST:
                self.boomerang.center_x -= 8

            # À chaque frame, j'ajoute 8 pixels à la distance parcourue.
            self.boomerang.distance_travelled += 8

            # Si le boomerang a parcouru l'équivalent de 8 cases,
            # il arrête de s'éloigner et passe en retour.
            if self.boomerang.distance_travelled >= 8 * TILE_SIZE:
                self.boomerang.state = BoomerangState.RETURNING

            # S'il touche un mur pendant le lancement, il passe aussi en retour.
            colliding_walls = arcade.check_for_collision_with_list(self.boomerang, self.walls)
            if len(colliding_walls) > 0:
                self.boomerang.state = BoomerangState.RETURNING

            # S'il touche un monstre pendant le lancement :
            # - le monstre meurt
            # - le boomerang repart en retour
            colliding_spinners_with_boomerang = arcade.check_for_collision_with_list(
                self.boomerang, self.spinner_sprites
            )
            colliding_bats_with_boomerang = arcade.check_for_collision_with_list(
                self.boomerang, self.bat_sprites
            )
            # attention aux monstres : si le boomerang en touche un, il doit retourner !
            # j'utilise donc if/elif comme ça il retourne dès qu'il en touche un (soit bat, soit spinner, pas les deux)
            if len(colliding_bats_with_boomerang) > 0:
                for bat_sprite in colliding_bats_with_boomerang:
                    self._remove_bat_sprite(bat_sprite)
                self.boomerang.state = BoomerangState.RETURNING

            elif len(colliding_spinners_with_boomerang) > 0:
                for spinner_sprite in colliding_spinners_with_boomerang:
                    self._remove_spinner_sprite(spinner_sprite)
                self.boomerang.state = BoomerangState.RETURNING

        # =========================
        # Gestion du boomerang : phase de retour
        # =========================
        if self.boomerang.state == BoomerangState.RETURNING:

            # Je calcule le vecteur allant du boomerang vers le joueur.
            dx = self.player.center_x - self.boomerang.center_x
            dy = self.player.center_y - self.boomerang.center_y
            distance = math.sqrt(dx ** 2 + dy ** 2)

            # Si le boomerang est suffisamment proche du joueur,
            # je considère qu'il est revenu.
            if distance <= 8:
                self.boomerang.state = BoomerangState.INACTIVE
                self.boomerang.distance_travelled = 0
                self.boomerang.position = self.player.position

            else:
                # Sinon je le fais avancer vers le joueur.
                # Comme je recalcule ça à chaque frame, si le joueur bouge,
                # le boomerang peut suivre une trajectoire courbe.
                self.boomerang.center_x += 8 * dx / distance
                self.boomerang.center_y += 8 * dy / distance

            # Pendant le retour, le boomerang traverse les murs,
            # mais il continue de tuer les monstres qu'il touche.
            colliding_bats_with_boomerang = arcade.check_for_collision_with_list(
                self.boomerang, self.bat_sprites
            )
            colliding_spinners_with_boomerang = arcade.check_for_collision_with_list(
                self.boomerang, self.spinner_sprites
            )
            if len(colliding_bats_with_boomerang) > 0:
                for bat_sprite in colliding_bats_with_boomerang:
                    self._remove_bat_sprite(bat_sprite)
            if len(colliding_spinners_with_boomerang) > 0:
                for spinner_sprite in colliding_spinners_with_boomerang:
                    self._remove_spinner_sprite(spinner_sprite)

        # =========================
        # Gestion de l'épée :
        # =========================
        if self.sword.state == SwordState.ACTIVE :
            # l'épée est centrée sur le joueur :
            self.sword.position = self.player.position
            #je fais avancer son aniumation :
            self.sword.update_animation()
            #je mets à jour le ctemps écoulé deouis le début de l'attaque :
            self.sword.time+=delta_time
            # si le temps écoulé dépasse : 6 x 50ms = 300 ms -> 0.3, l'attaque est achevée :
            if self.sword.time >= 0.3 :
                self.sword.state= SwordState.INACTIVE
                self.sword.time=0

            # gestion des collisions : épée et spinners :
            colliding_spinners_with_sword = arcade.check_for_collision_with_list(
                self.sword, self.spinner_sprites
            )
            for spinner_sprite in colliding_spinners_with_sword :
                self._remove_spinner_sprite(spinner_sprite)

            # gestion des collisions : épée et chauve-souris :
            colliding_bats_with_sword = arcade.check_for_collision_with_list(
                self.sword, self.bat_sprites
            )
            for bat_sprite in colliding_bats_with_sword:
                self._remove_bat_sprite(bat_sprite)

            # gestion des collisions : épée et cristaux :
            colliding_crystals_with_sword = arcade.check_for_collision_with_list(
                self.sword, self.crystals
            )
            for crystal in colliding_crystals_with_sword :
                crystal.remove_from_sprite_lists()
                arcade.play_sound(SOUND_COIN)
                self.score+=1


        # =========================
        # Collision joueur / cristaux
        # =========================
        # Si le joueur touche un cristal :
        # - il disparaît
        # - le son se joue
        # - le score augmente
        colliding_crystals = arcade.check_for_collision_with_list(self.player, self.crystals)
        for crystal in colliding_crystals:
            crystal.remove_from_sprite_lists()
            arcade.play_sound(SOUND_COIN)
            self.score += 1

        # =========================
        # Collision joueur / spinners
        # =========================
        # Si le joueur touche un spinner, on reset la partie.
        colliding_spinners = arcade.check_for_collision_with_list(self.player, self.spinner_sprites)
        if len(colliding_spinners) > 0:
            new_view = GameView(self.map)
            self.window.show_view(new_view)
            return
        # =========================
        # Collision joueur / bats
        # =========================
        # Si le joueur touche une chauve-souris, on reset la partie.
        colliding_bats = arcade.check_for_collision_with_list(
            self.player, self.bat_sprites
        )
        if len(colliding_bats)>0 :
            new_view= GameView(self.map)
            self.window.show_view(new_view)
            return

        # La caméra suit le joueur
        self.camera.position = self.player.position

        # =========================
        # Collision joueur / trous
        # =========================
        # Si le joueur est trop proche d'un trou, on reset aussi la partie.
        nearby_holes = arcade.check_for_collision_with_list(self.player, self.holes)
        for hole in nearby_holes:
            if math.dist(self.player.position, hole.position) <= 16:
                new_view = GameView(self.map)
                self.window.show_view(new_view)
                return
