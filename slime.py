from __future__ import annotations

from dataclasses import dataclass
import math
import random

from constants import TILE_SIZE
from map import GridCell, Map
from navmesh import NavMesh, Point, shortest_path


# ==================================================
# Constantes des slimes
# ==================================================

SLIME_SPEED = 1.0

PATROL_RADIUS = 3

DESTINATION_EPSILON = 4.0


@dataclass
class Slime:
    # Position de départ en coordonnées de grille.
    start_x: int
    start_y: int

    # Destination finale actuelle en pixels.
    destination_x: float
    destination_y: float

    # Position actuelle en pixels.
    x: float
    y: float

    # Destinations possibles en coordonnées de grille.
    possible_destinations: list[tuple[int, int]]

    # Chemin actuel en pixels.
    #
    # Avant :
    # le slime allait directement vers destination_x, destination_y.
    #
    # Maintenant :
    # il suit current_path point par point.
    current_path: list[Point]

    # Position du prochain point à suivre dans current_path.
    current_path_index: int


def grid_to_pixels(i: int) -> int:
    return i * TILE_SIZE + TILE_SIZE // 2


def is_inside_map(game_map: Map, x: int, y: int) -> bool:
    return 0 <= x < game_map.width and 0 <= y < game_map.height


def is_slime_obstacle(cell: GridCell) -> bool:
    return cell in {
        GridCell.BUSH,
        GridCell.HOLE,
    }


def can_slime_stand_on(game_map: Map, x: int, y: int) -> bool:
    if not is_inside_map(game_map, x, y):
        return False

    return not is_slime_obstacle(game_map.get(x, y))


def find_cells(game_map: Map, target: GridCell) -> list[tuple[int, int]]:
    return [
        (x, y)
        for y in range(game_map.height)
        for x in range(game_map.width)
        if game_map.get(x, y) == target
    ]


def find_slimes(game_map: Map) -> list[tuple[int, int]]:
    return find_cells(game_map, GridCell.SLIME)


def slime_patrol_destinations(
    game_map: Map,
    start_x: int,
    start_y: int,
) -> list[tuple[int, int]]:
    # Zone 7x7 autour du slime.
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
    return rng.choice(possible_destinations)


def set_random_destination(
    slime: Slime,
    navmesh: NavMesh,
    rng: random.Random,
) -> None:
    # Le slime choisit une destination valide dans sa zone.
    destination_x, destination_y = choose_random_destination(
        slime.possible_destinations,
        rng,
    )

    slime.destination_x = grid_to_pixels(destination_x)
    slime.destination_y = grid_to_pixels(destination_y)

    # Différence avec l'étape précédente :
    # au lieu d'aller en ligne droite, on demande un chemin au navmesh.
    recompute_path(slime, navmesh)


def recompute_path(slime: Slime, navmesh: NavMesh) -> None:
    # Calcule un nouveau plus court chemin depuis la position du slime
    # jusqu'à sa destination actuelle.
    source = (slime.x, slime.y)
    target = (slime.destination_x, slime.destination_y)

    slime.current_path = shortest_path(navmesh, source, target)
    slime.current_path_index = 0


def distance_between_points(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
) -> float:
    dx = x2 - x1
    dy = y2 - y1

    return math.sqrt(dx**2 + dy**2)


def has_reached_point(
    slime: Slime,
    point: Point,
) -> bool:
    # Vérifie si le slime est arrivé au prochain point du chemin.
    point_x, point_y = point

    distance = distance_between_points(
        slime.x,
        slime.y,
        point_x,
        point_y,
    )

    return distance <= DESTINATION_EPSILON


def has_reached_destination(slime: Slime) -> bool:
    # Vérifie si le slime est arrivé à sa destination finale.
    return distance_between_points(
        slime.x,
        slime.y,
        slime.destination_x,
        slime.destination_y,
    ) <= DESTINATION_EPSILON


def current_target_point(slime: Slime) -> Point:
    # Donne le prochain point du chemin.
    return slime.current_path[slime.current_path_index]


def go_to_next_path_point(slime: Slime) -> None:
    # Passe au point suivant dans le chemin.
    if slime.current_path_index < len(slime.current_path) - 1:
        slime.current_path_index += 1


def move_slime_towards_point(slime: Slime, point: Point) -> None:
    # Même idée que le mouvement précédent :
    # dx, dy = target - position.
    #
    # Mais maintenant la cible n'est pas forcément la destination finale.
    # C'est le prochain point du chemin.
    point_x, point_y = point

    dx = point_x - slime.x
    dy = point_y - slime.y

    distance = math.sqrt(dx**2 + dy**2)

    if distance <= DESTINATION_EPSILON:
        return

    slime.x += SLIME_SPEED * dx / distance
    slime.y += SLIME_SPEED * dy / distance


def follow_current_path(slime: Slime) -> None:
    # Le slime avance point par point dans son chemin.
    if len(slime.current_path) == 0:
        return

    point = current_target_point(slime)

    if has_reached_point(slime, point):
        go_to_next_path_point(slime)
        point = current_target_point(slime)

    move_slime_towards_point(slime, point)


def update_slime_random_movement(
    slime: Slime,
    navmesh: NavMesh,
    rng: random.Random,
) -> None:
    # À chaque frame :
    #
    # 1. Si le slime est arrivé à sa destination finale,
    #    il choisit une nouvelle destination.
    #
    # 2. Il calcule alors un chemin avec le navmesh.
    #
    # 3. Il suit ce chemin point par point.

    if has_reached_destination(slime):
        set_random_destination(slime, navmesh, rng)

    follow_current_path(slime)


def create_slime(
    game_map: Map,
    navmesh: NavMesh,
    start_x: int,
    start_y: int,
    rng: random.Random,
) -> Slime:
    possible_destinations = slime_patrol_destinations(
        game_map,
        start_x,
        start_y,
    )

    if len(possible_destinations) == 0:
        possible_destinations = [(start_x, start_y)]

    first_destination_x, first_destination_y = choose_random_destination(
        possible_destinations,
        rng,
    )

    slime = Slime(
        start_x=start_x,
        start_y=start_y,
        destination_x=grid_to_pixels(first_destination_x),
        destination_y=grid_to_pixels(first_destination_y),
        x=grid_to_pixels(start_x),
        y=grid_to_pixels(start_y),
        possible_destinations=possible_destinations,
        current_path=[],
        current_path_index=0,
    )

    recompute_path(slime, navmesh)

    return slime


def create_slimes(
    game_map: Map,
    navmesh: NavMesh,
    rng: random.Random,
) -> list[Slime]:
    return [
        create_slime(game_map, navmesh, x, y, rng)
        for x, y in find_slimes(game_map)
    ]