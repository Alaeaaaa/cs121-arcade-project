from dataclasses import dataclass
from enum import Enum

from map import GridCell, Map


class Direction(Enum):
    # POSITIF : droite pour un spinner horizontal, haut pour un spinner vertical.
    POSITIF = 1

    # NEGATIF : gauche pour un spinner horizontal, bas pour un spinner vertical.
    NEGATIF = -1


@dataclass
class Limites:
    # Limites de déplacement du spinner dans la grille.
    min_x: int
    max_x: int
    min_y: int
    max_y: int


@dataclass
class Spinner:
    # Position actuelle du spinner dans la grille.
    x: int
    y: int

    # True si le spinner bouge horizontalement, False s'il bouge verticalement.
    horizontal: bool

    # Sens actuel du déplacement : POSITIF ou NEGATIF.
    direction: Direction

    # Zone dans laquelle le spinner a le droit de bouger.
    limites: Limites


def is_spinner_cell(cell: GridCell) -> bool:
    # Vérifie si une case contient un spinner horizontal ou vertical.
    return cell in {
        GridCell.SPINNER_HORIZONTAL,
        GridCell.SPINNER_VERTICAL,
    }


def is_blocking_cell(cell: GridCell) -> bool:
    # Pour l'instant, un buisson bloque le déplacement d'un spinner.
    return cell == GridCell.BUSH


def is_inside_map(game_map: Map, x: int, y: int) -> bool:
    # Vérifie si la position (x, y) est encore dans la carte.
    return 0 <= x < game_map.width and 0 <= y < game_map.height


def scan_until_blocked(
    game_map: Map,
    x: int,
    y: int,
    dx: int,
    dy: int,
) -> tuple[int, int]:
    # Avance depuis (x, y) dans la direction (dx, dy)
    # jusqu'à sortir de la map ou rencontrer un obstacle.
    next_x = x + dx
    next_y = y + dy

    while is_inside_map(game_map, next_x, next_y) and not is_blocking_cell(game_map.get(next_x, next_y)):
        x = next_x
        y = next_y
        next_x += dx
        next_y += dy

    return x, y


def compute_horizontal_bounds(game_map: Map, x: int, y: int) -> Limites:
    # Cherche la limite à gauche puis la limite à droite.
    min_x, _ = scan_until_blocked(game_map, x, y, dx=-1, dy=0)
    max_x, _ = scan_until_blocked(game_map, x, y, dx=1, dy=0)

    return Limites(
        min_x=min_x,
        max_x=max_x,
        min_y=y,
        max_y=y,
    )


def compute_vertical_bounds(game_map: Map, x: int, y: int) -> Limites:
    # Cherche la limite en bas puis la limite en haut.
    _, min_y = scan_until_blocked(game_map, x, y, dx=0, dy=-1)
    _, max_y = scan_until_blocked(game_map, x, y, dx=0, dy=1)

    return Limites(
        min_x=x,
        max_x=x,
        min_y=min_y,
        max_y=max_y,
    )


def compute_spinner_bounds(game_map: Map, x: int, y: int) -> Limites:
    # Calcule les limites selon le type de spinner présent à la position (x, y).
    cell = game_map.get(x, y)

    if cell == GridCell.SPINNER_HORIZONTAL:
        return compute_horizontal_bounds(game_map, x, y)

    if cell == GridCell.SPINNER_VERTICAL:
        return compute_vertical_bounds(game_map, x, y)

    # Sécurité : cette fonction doit être appelée seulement sur une case spinner.
    raise ValueError("Pas de spinner à cette position")


def find_spinners(game_map: Map) -> list[tuple[int, int]]:
    # Parcourt toute la carte et retourne les positions des spinners.
    return [
        (x, y)
        for y in range(game_map.height)
        for x in range(game_map.width)
        if is_spinner_cell(game_map.get(x, y))
    ]


def create_spinner(game_map: Map, x: int, y: int) -> Spinner:
    # Crée un objet Spinner à partir de sa position dans la grille.
    cell = game_map.get(x, y)

    return Spinner(
        x=x,
        y=y,
        horizontal=(cell == GridCell.SPINNER_HORIZONTAL),
        direction=Direction.POSITIF,
        limites=compute_spinner_bounds(game_map, x, y),
    )


def create_spinners(game_map: Map) -> list[Spinner]:
    # Crée tous les spinners présents dans la map.
    return [
        create_spinner(game_map, x, y)
        for x, y in find_spinners(game_map)
    ]