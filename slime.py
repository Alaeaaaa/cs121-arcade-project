from __future__ import annotations
from navmesh import can_slime_stand_on
import math
import random

import arcade

from constants import (
    SCALE,
    SLIME_SPEED,
    PATROL_RADIUS,
    DESTINATION_EPSILON,
    MAX_VIEW_DISTANCE,
    DIRECT_CHASE_DISTANCE,
    RECOMPUTE_PATH_DISTANCE,
)
from map import GridCell, Map
from navmesh import NavMesh, Point, shortest_path
from utils import grid_to_pixels, find_cells
from enemy import Enemy, EnemyContext
from textures import ANIMATION_SLIME


class Slime(Enemy):

    def __init__(
        self,
        start_x: int,
        start_y: int,
        destination_x: float,
        destination_y: float,
        x: float,
        y: float,
        possible_destinations: list[tuple[int, int]],
    ) -> None:
        super().__init__(animation=ANIMATION_SLIME, scale=SCALE)

        self.start_x = start_x
        self.start_y = start_y
        self.logic_x = x
        self.logic_y = y
        self.destination_x = destination_x
        self.destination_y = destination_y
        self.possible_destinations = possible_destinations
        self.current_path: list[Point] = []
        self.current_path_index: int = 0

    def update_logic(self, context:EnemyContext) -> None:
        slime_position = (self.logic_x, self.logic_y)
        distance_to_player = math.dist(slime_position, context.player_position)

        if self._can_see_player(context.player_position, context.walls):
            if distance_to_player <= DIRECT_CHASE_DISTANCE:
                self._move_directly_to(context.player_position)
                return
            self._set_destination_to_player(context.navmesh, context.player_position)

        elif self._has_reached_destination():
            self._set_random_destination(context.navmesh, context.rng)

        self._follow_current_path()

    def sync_sprite(self) -> None:
        self.center_x = self.logic_x
        self.center_y = self.logic_y

    # Déplacement

    def _move_directly_to(self, target: Point) -> None:
        """on déplace le slime en ligne droite vers un point"""
        tx, ty = target
        dx, dy = tx - self.logic_x, ty - self.logic_y
        distance = math.dist((self.logic_x, self.logic_y), target)

        if distance <= DESTINATION_EPSILON:
            return

        self.logic_x += SLIME_SPEED * dx / distance
        self.logic_y += SLIME_SPEED * dy / distance

    def _follow_current_path(self) -> None:
        """on fait simplement avancer le slime le long de son chemin actuel"""
        if not self.current_path:
            return

        point = self.current_path[self.current_path_index]

        if math.dist((self.logic_x, self.logic_y), point) <= DESTINATION_EPSILON:
            if self.current_path_index < len(self.current_path) - 1:
                self.current_path_index += 1
            point = self.current_path[self.current_path_index]

        self._move_directly_to(point)

    # Destination et chemin du slime

    def _set_random_destination(self, navmesh: NavMesh, rng: random.Random) -> None:
        """on choisit une destination au hasard parmi celles possibles, et on recalcule le chemin"""
        dest_x, dest_y = rng.choice(self.possible_destinations)
        self.destination_x = grid_to_pixels(dest_x)
        self.destination_y = grid_to_pixels(dest_y)
        self._recompute_path(navmesh)

    def _set_destination_to_player(self, navmesh: NavMesh, player_position: Point) -> None:
        """on selectionne la position du joueur comme destination, mais juste si elle a "assez changé" """
        destination = (self.destination_x, self.destination_y)
        if math.dist(destination, player_position) <= RECOMPUTE_PATH_DISTANCE:
            return
        self.destination_x, self.destination_y = player_position
        self._recompute_path(navmesh)

    def _recompute_path(self, navmesh: NavMesh) -> None:
        source = (self.logic_x, self.logic_y)
        target = (self.destination_x, self.destination_y)
        self.current_path = shortest_path(navmesh, source, target)
        self.current_path_index = 0

    #quelques méthodes utiles au slime :
    def _has_reached_destination(self) -> bool:
        """ici c'est pour dire si le slime est arrivé suffisament près de sa destination"""
        return math.dist(
            (self.logic_x, self.logic_y),
            (self.destination_x, self.destination_y),
        ) <= DESTINATION_EPSILON

    def _can_see_player(self, player_position: Point, walls: arcade.SpriteList) -> bool:
        """on vérifie si le slime voit le joueur"""
        slime_position = (self.logic_x, self.logic_y)
        if math.dist(slime_position, player_position) > MAX_VIEW_DISTANCE:
            return False
        return arcade.has_line_of_sight(slime_position, player_position, walls)


def _patrol_destinations(game_map: Map, start_x: int, start_y: int) -> list[tuple[int,int]]:
    """determine toutes les cases accessibles dans le rayon de patrouille du slime"""
    return [
        (x, y)
        for y in range(start_y - PATROL_RADIUS, start_y + PATROL_RADIUS + 1)
        for x in range(start_x - PATROL_RADIUS, start_x + PATROL_RADIUS + 1)
        if can_slime_stand_on(game_map, x, y)
    ]

def create_slime(
    game_map: Map,
    navmesh: NavMesh,
    start_x: int,
    start_y: int,
    rng: random.Random,
) -> Slime:
    #idée de refact pour après : on devrait rassembler cet aspet de création de sprites.
    possible_destinations = _patrol_destinations(game_map, start_x, start_y)

    if not possible_destinations:
        possible_destinations = [(start_x, start_y)]

    dest_x, dest_y = rng.choice(possible_destinations)

    slime = Slime(
        start_x=start_x,
        start_y=start_y,
        destination_x=grid_to_pixels(dest_x),
        destination_y=grid_to_pixels(dest_y),
        x=grid_to_pixels(start_x),
        y=grid_to_pixels(start_y),
        possible_destinations=possible_destinations,
    )

    slime._recompute_path(navmesh)
    return slime


def create_slimes(game_map: Map, navmesh: NavMesh, rng: random.Random) -> list[Slime]:
    return [
        create_slime(game_map, navmesh, x, y, rng)
        for x, y in find_cells(game_map, GridCell.SLIME)
    ]
