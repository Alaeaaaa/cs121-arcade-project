from constants import SCALE
from __future__ import annotations

from map import GridCell, Map
from enemy import Enemy
from textures import ANIMATION_SPINNER


class SpinnerDirection:
    POSITIF = 1
    NEGATIF = -1


class Spinner(Enemy):
    """
    Spinner : se déplace en ligne droite (horizontal ou vertical),
    fait demi-tour en bout de course.
    """

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

        self.grid_x = x
        self.grid_y = y
        self.horizontal = horizontal
        self.grid_direction: int = SpinnerDirection.POSITIF
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y

    def update_logic(self, **kwargs) -> None:
        if self.horizontal:
            self.grid_x += self.grid_direction
            if self.grid_x >= self.max_x or self.grid_x <= self.min_x:
                self.grid_direction = -self.grid_direction
        else:
            self.grid_y += self.grid_direction
            if self.grid_y >= self.max_y or self.grid_y <= self.min_y:
                self.grid_direction = -self.grid_direction

    def sync_sprite(self) -> None:
        from utils import grid_to_pixels
        self.center_x = grid_to_pixels(self.grid_x)
        self.center_y = grid_to_pixels(self.grid_y)


# --------------------------------------------------
# Helpers module-privés
# --------------------------------------------------

def _is_blocking_cell(cell: GridCell) -> bool:
    return cell == GridCell.BUSH


def _is_inside_map(game_map: Map, x: int, y: int) -> bool:
    return 0 <= x < game_map.width and 0 <= y < game_map.height


def _scan_until_blocked(game_map: Map, x: int, y: int, dx: int, dy: int) -> tuple[int, int]:
    nx, ny = x + dx, y + dy
    while _is_inside_map(game_map, nx, ny) and not _is_blocking_cell(game_map.get(nx, ny)):
        x, y = nx, ny
        nx, ny = x + dx, y + dy
    return x, y


# --------------------------------------------------
# Factories
# --------------------------------------------------

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