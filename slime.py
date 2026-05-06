from dataclasses import dataclass
import math
import random

from constants import TILE_SIZE
from map import GridCell, Map


# ==================================================
# Constantes des slimes
# ==================================================

# Comme les bats, les slimes bougent petit à petit à chaque frame.
# Ici, ils avancent de 1 pixel par frame.
SLIME_SPEED = 1.0

# Le slime patrouille dans un carré 7x7 autour de sa position de départ.
# Rayon 3 : 3 cases à gauche, 3 à droite, 3 en bas, 3 en haut.
PATROL_RADIUS = 3

# Si le slime est à moins de 4 pixels de sa destination,
# on considère qu'il est arrivé.
DESTINATION_EPSILON = 4.0


@dataclass
class Slime:
    # Position de départ en coordonnées de grille.
    # Elle sert à calculer la zone de patrouille.
    start_x: int
    start_y: int

    # Destination actuelle en pixels.
    # Contrairement à la bat qui suit un angle,
    # le slime suit une destination précise.
    destination_x: float
    destination_y: float

    # Position actuelle en pixels.
    # Comme pour les bats, on utilise des float pour avoir un mouvement fluide.
    x: float
    y: float

    # Toutes les cases où le slime peut choisir une destination.
    # Ces positions sont en coordonnées de grille.
    possible_destinations: list[tuple[int, int]]


def grid_to_pixels(i: int) -> int:
    # Convertit une coordonnée de grille en pixel.
    # On place le sprite au centre de la case.
    return i * TILE_SIZE + TILE_SIZE // 2


def is_inside_map(game_map: Map, x: int, y: int) -> bool:
    # Vérifie que la case existe dans la map.
    return 0 <= x < game_map.width and 0 <= y < game_map.height


def is_slime_obstacle(cell: GridCell) -> bool:
    # Le slime marche au sol.
    # Il ne choisit donc pas les buissons ni les trous comme destination.
    return cell in {
        GridCell.BUSH,
        GridCell.HOLE,
    }


def can_slime_stand_on(game_map: Map, x: int, y: int) -> bool:
    # Une case est accessible si elle est dans la map
    # et si ce n'est pas un obstacle.
    if not is_inside_map(game_map, x, y):
        return False

    return not is_slime_obstacle(game_map.get(x, y))


def find_cells(game_map: Map, target: GridCell) -> list[tuple[int, int]]:
    # Même idée que pour les autres monstres :
    # on parcourt toute la map pour trouver un type de case précis.
    return [
        (x, y)
        for y in range(game_map.height)
        for x in range(game_map.width)
        if game_map.get(x, y) == target
    ]


def find_slimes(game_map: Map) -> list[tuple[int, int]]:
    # On récupère toutes les positions où il y a un slime dans la map.
    return find_cells(game_map, GridCell.SLIME)


def slime_patrol_destinations(
    game_map: Map,
    start_x: int,
    start_y: int,
) -> list[tuple[int, int]]:
    # Calcule les destinations possibles du slime.
    #
    # Différence avec la bat :
    # - la bat rebondit dans une zone
    # - le slime choisit une destination dans sa zone, puis avance vers elle
    destinations: list[tuple[int, int]] = []

    for y in range(start_y - PATROL_RADIUS, start_y + PATROL_RADIUS + 1):
        for x in range(start_x - PATROL_RADIUS, start_x + PATROL_RADIUS + 1):
            if can_slime_stand_on(game_map, x, y):
                destinations.append((x, y))

    return destinations


def choose_random_destination(
    possible_destinations: list[tuple[int, int]],
    rng: random.Random,
) -> tuple[int, int]:
    # Choisit une case au hasard parmi les destinations possibles.
    return rng.choice(possible_destinations)


def set_random_destination(slime: Slime, rng: random.Random) -> None:
    # Choisit une nouvelle destination et la convertit en pixels.
    destination_x, destination_y = choose_random_destination(
        slime.possible_destinations,
        rng,
    )

    slime.destination_x = grid_to_pixels(destination_x)
    slime.destination_y = grid_to_pixels(destination_y)


def distance_between_points(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
) -> float:
    # Distance classique entre deux points.
    dx = x2 - x1
    dy = y2 - y1

    return math.sqrt(dx**2 + dy**2)


def has_reached_destination(slime: Slime) -> bool:
    # Vérifie si le slime est arrivé assez proche de sa destination.
    distance = distance_between_points(
        slime.x,
        slime.y,
        slime.destination_x,
        slime.destination_y,
    )

    return distance <= DESTINATION_EPSILON


def move_slime_towards_destination(slime: Slime) -> None:
    # Mouvement du slime.
    #
    # Ressemblance avec les bats :
    # dans les deux cas, on calcule un petit déplacement dx, dy.
    #
    # Différence :
    # - bat : dx, dy viennent de speed * cos(angle), speed * sin(angle)
    # - slime : dx, dy viennent de destination - position

    dx = slime.destination_x - slime.x
    dy = slime.destination_y - slime.y

    distance = math.sqrt(dx**2 + dy**2)

    if distance <= DESTINATION_EPSILON:
        return

    # On divise par distance pour garder seulement la direction.
    # Puis on multiplie par SLIME_SPEED pour avoir une vitesse constante.
    slime.x += SLIME_SPEED * dx / distance
    slime.y += SLIME_SPEED * dy / distance


def update_slime_random_movement(slime: Slime, rng: random.Random) -> None:
    # À chaque frame :
    # 1. si le slime est arrivé, il choisit une nouvelle destination
    # 2. il avance vers cette destination
    #
    # Pour l'instant, il ignore le joueur.
    # La poursuite du joueur viendra avec la line of sight + navmesh.
    if has_reached_destination(slime):
        set_random_destination(slime, rng)

    move_slime_towards_destination(slime)


def create_slime(
    game_map: Map,
    start_x: int,
    start_y: int,
    rng: random.Random,
) -> Slime:
    # Crée un slime à partir de sa position de départ.
    possible_destinations = slime_patrol_destinations(
        game_map,
        start_x,
        start_y,
    )

    # Sécurité : si aucune destination n'est possible,
    # il reste simplement sur sa case de départ.
    if len(possible_destinations) == 0:
        possible_destinations = [(start_x, start_y)]

    first_destination_x, first_destination_y = choose_random_destination(
        possible_destinations,
        rng,
    )

    return Slime(
        start_x=start_x,
        start_y=start_y,
        destination_x=grid_to_pixels(first_destination_x),
        destination_y=grid_to_pixels(first_destination_y),
        x=grid_to_pixels(start_x),
        y=grid_to_pixels(start_y),
        possible_destinations=possible_destinations,
    )


def create_slimes(game_map: Map, rng: random.Random) -> list[Slime]:
    # Crée tous les slimes trouvés dans la map.
    return [
        create_slime(game_map, x, y, rng)
        for x, y in find_slimes(game_map)
    ]