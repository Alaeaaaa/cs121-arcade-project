from __future__ import annotations

from constants import SCALE, SPINNER_MOVEMENT_SPEED, TILE_SIZE
from map import GridCell, Map
from enemy import Enemy, EnemyContext
from textures import ANIMATION_SPINNER
from utils import grid_to_pixels,is_inside_map


class Spinner(Enemy):


    logic_x:float
    logic_y:float
    horizontal:bool
    direction:int
    min_x:float
    max_x:float
    min_y:float
    max_y:float


    #Spinner : se déplace en ligne droite (horizontal ou vertical),
    #fait demi-tour en bout de course.



    def __init__(
        self,
        x: int,
        y: int,
        horizontal: bool,
        min_x: int,
        max_x: int,
        min_y: int,
        max_y: int,
    ) -> None:
        super().__init__(animation=ANIMATION_SPINNER, scale=SCALE)

        #position logique en pixels:
        self.logic_x = float(grid_to_pixels(x))
        self.logic_y = float(grid_to_pixels(y))

        self.horizontal = horizontal
        self.direction: int = 1  # +1 ou -1

        # limites en pixels:
        self.min_x = float(grid_to_pixels(min_x))
        self.max_x = float(grid_to_pixels(max_x))
        self.min_y = float(grid_to_pixels(min_y))
        self.max_y = float(grid_to_pixels(max_y))

    def update_logic(self, context:EnemyContext) -> None:
        """on avance le spinner, et on inverse sa direction s'il atteint une limite"""
        if self.horizontal:
            self.logic_x += self.direction * SPINNER_MOVEMENT_SPEED
            if self.logic_x >= self.max_x or self.logic_x <= self.min_x:
                self.direction = -self.direction
                self.logic_x = max(self.min_x, min(self.logic_x, self.max_x))
        else:
            self.logic_y += self.direction * SPINNER_MOVEMENT_SPEED
            if self.logic_y >= self.max_y or self.logic_y <= self.min_y:
                self.direction = -self.direction
                self.logic_y = max(self.min_y, min(self.logic_y, self.max_y))

    def sync_sprite(self) -> None:
        self.center_x = self.logic_x
        self.center_y = self.logic_y



def _is_blocking_cell(cell: GridCell) -> bool:
    return cell == GridCell.BUSH


def _scan_until_blocked(game_map: Map, x: int, y: int, dx: int, dy: int) -> tuple[int, int]:
    """on avance dans une direction jusqu'à rencontrer un obstacle ou un bord"""
    nx, ny = x + dx, y + dy
    while is_inside_map(game_map, nx, ny) and not _is_blocking_cell(game_map.get(nx, ny)):
        x, y = nx, ny
        nx, ny = x + dx, y + dy
    return x, y


def create_spinner(game_map: Map, x: int, y: int) -> Spinner:
    cell = game_map.get(x, y)
    horizontal = cell == GridCell.SPINNER_HORIZONTAL

    if horizontal:
        min_x, _ = _scan_until_blocked(game_map, x, y, dx=-1, dy=0)
        max_x, _ = _scan_until_blocked(game_map, x, y, dx=1, dy=0)
        min_y = max_y = y
    else:
        _, min_y = _scan_until_blocked(game_map, x, y, dx=0, dy=-1)
        _, max_y = _scan_until_blocked(game_map, x, y, dx=0, dy=1)
        min_x = max_x = x

    return Spinner(
        x=x,
        y=y,
        horizontal=horizontal,
        min_x=min_x,
        max_x=max_x,
        min_y=min_y,
        max_y=max_y,
    )


def create_spinners(game_map: Map) -> list[Spinner]:
    return [
        create_spinner(game_map, x, y)
        for y in range(game_map.height)
        for x in range(game_map.width)
        if game_map.get(x, y) in {GridCell.SPINNER_HORIZONTAL, GridCell.SPINNER_VERTICAL}
    ]
