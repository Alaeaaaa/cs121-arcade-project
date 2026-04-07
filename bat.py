from dataclasses import dataclass
import math
import random
from map import Map, GridCell
from constants import TILE_SIZE
""" Pour représenter la chauve-souris, j'ai choisi de garder un code
    similaire à celui des spinners pour rester familiarisés avec le code
    utilisé. """
# Je détermine d'abord les constantes :
# vitesse :
BAT_SPEED = 2.0
# dimensions de rectangle d'action :
BAT_WIDTH = 6
BAT_HEIGHT = 4
# nombre de frames pour changer de direction :
BAT_DIRECTION_CHANGE = 20
# pour représenter les limites du rectangle d'action :
@dataclass
class BatBounds :
    min_x: float
    min_y: float
    max_x: float
    max_y: float


@dataclass
class Bat :
    # position de départ (grille) :
    start_x : int
    start_y : int
    # direction actuelle (en rad) :
    angle : float
    # vitesse constante :
    speed : float
    # limites du rectangle d'action :
    bounds : BatBounds
    # nombre de frames avant changement de direction :
    frames_direction_change : int

# pour trouver les chauve-souris dans la map :
def find_bats(game_map : Map):
    #ici je vais stocker les positions de tous les bats trouvés :
    bats=[]
    # je parcours toute la map case par case
    for x in range(game_map.width):
        for y in range(game_map.height):

            # je regarde ce qu'il y a dans la case actuelle
            cell = game_map.get(x, y)

            # si c'est une chauve-souris, j'ajoute sa position dans la liste :
            if cell == GridCell.BAT :
                bats.append((x, y))
    # je renvoie la liste des positions ainsi trouvées :
    return bats
# à présent, je dois déterminer le rectangle d'action de la chauve-souris :
# et ce à partir de sa position de départ :
def compute_bat_bounds(game_map : Map, x: int, y : int):
    # je dois créer le rectangle, tout en faisant attention à rester dans la map !
    # aussi, la zone est delimitée dans l'aire du rectangle qui est calculée comme
    # vu en ajoutant/retirant la moitié de la largeur/hauteur car on considère x et y
    # comme le milieu.
    min_x = max(0,x-BAT_WIDTH//2)
    min_y = max(0,y-BAT_HEIGHT//2)
    max_x = min(game_map.width-1, x+BAT_WIDTH//2)
    max_y = min(game_map.height-1, y + BAT_HEIGHT//2)
    return BatBounds (
        min_x=min_x,
        min_y=min_y,
        max_x=max_x,
        max_y=max_y,
    )
# à présent, je dois créer les chauve-souris qui sont présents sur la map :
def create_bats (game_map : Map, val : random.Random):
    # je crée la liste qui contiendra toutes les chauve-souris :
    bats = []
    # je récupère ensuite la liste de toutes les positions :
    positions = find_bats(game_map)
    # je parcours ensuite la liste des tuple de coordonnées pour créer les bats :
    for x,y in positions :
        # je calcule les limites du rectangle d'action :
        bounds = compute_bat_bounds(game_map, x, y)
        bat = Bat (
            # la position de départ est celle trouvée :
            start_x=x,
            start_y = y,
            # l'angle (direction) est aléatoire comme demandé, variant entre 0 et 2pi :
            angle = val.uniform(0,2*math.pi),
            # la vitesse est constante :
            speed = BAT_SPEED,
            # les limites ont été calculées plus haut :
            bounds= bounds,
            # le nombre de frames pour changer de riection :
            frames_direction_change=BAT_DIRECTION_CHANGE,
        )
        bats.append(bat)
    return bats
