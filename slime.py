from __future__ import annotations

from dataclasses import dataclass
import math
import random

import arcade

from constants import TILE_SIZE
from map import GridCell, Map
from navmesh import NavMesh, Point, shortest_path


# ==================================================
# Constantes des slimes
# ==================================================

SLIME_SPEED = 1.0

PATROL_RADIUS = 3

DESTINATION_EPSILON = 4.0

# Distance de vue du slime.
MAX_VIEW_DISTANCE = 12 * TILE_SIZE

# Si le joueur est très proche, le slime avance directement vers lui.
# Ça évite de recalculer un chemin trop souvent.
DIRECT_CHASE_DISTANCE = 2 * TILE_SIZE

# Le slime recalcule son chemin seulement si le joueur a assez bougé.
RECOMPUTE_PATH_DISTANCE = TILE_SIZE // 2


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

    # Destinations aléatoires possibles en coordonnées de grille.
    possible_destinations: list[tuple[int, int]]

    # Chemin actuel en pixels.
    current_path: list[Point]

    # Index du prochain point à suivre dans current_path.
    current_path_index: int


def grid_to_pixels(i: int) -> int:
    return i * TILE_SIZE + TILE_SIZE // 2


def is_inside_map(game_map: Map, x: int, y: int) -> bool:
    return 0 <= x < game_map.width and 0 <= y < game_map.height


def is_slime_obstacle(cell: GridCell) -> bool:
    # Obstacles pour le déplacement du slime.
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
    # Destinations aléatoires autour de la position de départ.
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


def distance_between_points(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
) -> float:
    dx = x2 - x1
    dy = y2 - y1

    return math.sqrt(dx**2 + dy**2)


def distance_between_point_tuples(p1: Point, p2: Point) -> float:
    x1, y1 = p1
    x2, y2 = p2

    return distance_between_points(x1, y1, x2, y2)


def slime_can_see_player(
    slime: Slime,
    player_position: Point,
    walls: arcade.SpriteList,
) -> bool:
    # Le slime voit le joueur seulement si :
    # 1. le joueur est assez proche
    # 2. aucun buisson/mur ne bloque la ligne de vue
    slime_position = (slime.x, slime.y)

    if distance_between_point_tuples(slime_position, player_position) > MAX_VIEW_DISTANCE:
        return False

    return arcade.has_line_of_sight(
        slime_position,
        player_position,
        walls,
    )


def recompute_path(slime: Slime, navmesh: NavMesh) -> None:
    # Calcule un chemin avec le navmesh.
    source = (slime.x, slime.y)
    target = (slime.destination_x, slime.destination_y)

    slime.current_path = shortest_path(navmesh, source, target)
    slime.current_path_index = 0


def set_random_destination(
    slime: Slime,
    navmesh: NavMesh,
    rng: random.Random,
) -> None:
    # Si le slime ne voit pas le joueur, il patrouille.
    destination_x, destination_y = choose_random_destination(
        slime.possible_destinations,
        rng,
    )

    slime.destination_x = grid_to_pixels(destination_x)
    slime.destination_y = grid_to_pixels(destination_y)

    recompute_path(slime, navmesh)


def set_destination_to_player(
    slime: Slime,
    navmesh: NavMesh,
    player_position: Point,
) -> None:
    # Important :
    # On ne recalcule pas le chemin à chaque frame.
    # Sinon le slime reset son chemin tout le temps et il peut trembler.
    player_x, player_y = player_position

    distance_to_old_destination = distance_between_points(
        slime.destination_x,
        slime.destination_y,
        player_x,
        player_y,
    )

    if distance_to_old_destination <= RECOMPUTE_PATH_DISTANCE:
        return

    slime.destination_x = player_x
    slime.destination_y = player_y

    recompute_path(slime, navmesh)


def has_reached_point(
    slime: Slime,
    point: Point,
) -> bool:
    point_x, point_y = point

    return (
        distance_between_points(
            slime.x,
            slime.y,
            point_x,
            point_y,
        )
        <= DESTINATION_EPSILON
    )


def has_reached_destination(slime: Slime) -> bool:
    return (
        distance_between_points(
            slime.x,
            slime.y,
            slime.destination_x,
            slime.destination_y,
        )
        <= DESTINATION_EPSILON
    )


def current_target_point(slime: Slime) -> Point:
    return slime.current_path[slime.current_path_index]


def go_to_next_path_point(slime: Slime) -> None:
    if slime.current_path_index < len(slime.current_path) - 1:
        slime.current_path_index += 1


def move_slime_towards_point(slime: Slime, point: Point) -> None:
    point_x, point_y = point

    dx = point_x - slime.x
    dy = point_y - slime.y

    distance = math.sqrt(dx**2 + dy**2)

    if distance <= DESTINATION_EPSILON:
        return

    slime.x += SLIME_SPEED * dx / distance
    slime.y += SLIME_SPEED * dy / distance


def move_slime_directly_to_player(
    slime: Slime,
    player_position: Point,
) -> None:
    # Quand le slime est proche du joueur,
    # on n'utilise pas le navmesh.
    # Il avance directement vers lui.
    player_x, player_y = player_position

    dx = player_x - slime.x
    dy = player_y - slime.y

    distance = math.sqrt(dx**2 + dy**2)

    if distance <= DESTINATION_EPSILON:
        return

    slime.x += SLIME_SPEED * dx / distance
    slime.y += SLIME_SPEED * dy / distance


def follow_current_path(slime: Slime) -> None:
    if len(slime.current_path) == 0:
        return

    point = current_target_point(slime)

    if has_reached_point(slime, point):
        go_to_next_path_point(slime)
        point = current_target_point(slime)

    move_slime_towards_point(slime, point)


def update_slime_movement(
    slime: Slime,
    navmesh: NavMesh,
    rng: random.Random,
    player_position: Point,
    walls: arcade.SpriteList,
) -> None:
    # Logique complète :
    #
    # 1. Si le slime voit le joueur :
    #    - s'il est très proche, il avance directement vers lui
    #    - sinon, il utilise le navmesh
    #
    # 2. Si le slime ne voit pas le joueur :
    #    il patrouille normalement.
    slime_position = (slime.x, slime.y)

    distance_to_player = distance_between_point_tuples(
        slime_position,
        player_position,
    )

    if slime_can_see_player(slime, player_position, walls):
        if distance_to_player <= DIRECT_CHASE_DISTANCE:
            move_slime_directly_to_player(slime, player_position)
            return

        set_destination_to_player(slime, navmesh, player_position)

    elif has_reached_destination(slime):
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