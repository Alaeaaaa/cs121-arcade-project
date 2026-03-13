from map import Map, GridCell
from enum import Enum
from typing import Final
from dataclasses import dataclass

class Direction(Enum):
    POSITIF = 1
    NEGATIF = -1

@dataclass
class Limites:
    min_x: int
    max_x: int
    min_y: int
    max_y: int
        
def compute_spinner_bounds(game_map: Map, x: int, y: int) -> Limites:

    # d'abord je regarde ce qu'il y a dans la case (x,y)
    # normalement ça doit être un spinner
    cell = game_map.get(x, y)

    # -----------------------------
    # cas 1 : spinner horizontal
    # -----------------------------
    if cell == GridCell.SPINNER_HORIZONTAL:

        # je pars de la position actuelle
        min_x = x

        # je regarde vers la gauche
        # tant que je ne sors pas de la map
        # et que je ne tombe pas sur un buisson
        # je continue à reculer
        while min_x - 1 >= 0 and game_map.get(min_x - 1, y) != GridCell.BUSH:
            min_x -= 1

        # maintenant je fais pareil mais vers la droite
        max_x = x
        while max_x + 1 < game_map.width and game_map.get(max_x + 1, y) != GridCell.BUSH:
            max_x += 1

        # comme il est horizontal il ne bouge pas sur y
        return Limites(
            min_x=min_x,
            max_x=max_x,
            min_y=y,
            max_y=y
        )

    # -----------------------------
    # cas 2 : spinner vertical
    # -----------------------------
    if cell == GridCell.SPINNER_VERTICAL:

        # même idée mais cette fois on regarde sur y

        # vers le bas
        min_y = y
        while min_y - 1 >= 0 and game_map.get(x, min_y - 1) != GridCell.BUSH:
            min_y -= 1

        # vers le haut
        max_y = y
        while max_y + 1 < game_map.height and game_map.get(x, max_y + 1) != GridCell.BUSH:
            max_y += 1

        # comme il est vertical il ne bouge pas sur x
        return Limites(
            min_x=x,
            max_x=x,
            min_y=min_y,
            max_y=max_y
        )

    # si jamais on appelle la fonction sur une case qui n'est pas un spinner
    # normalement ça ne devrait pas arriver mais c'est une sécurité
    raise ValueError("Pas de spinner à cette position")

def find_spinners(game_map: Map) -> list[tuple[int, int]]:

    # ici je vais stocker les positions de tous les spinners trouvés
    spinners = []

    # je parcours toute la map case par case
    for x in range(game_map.width):
        for y in range(game_map.height):

            # je regarde ce qu'il y a dans la case actuelle
            cell = game_map.get(x, y)

            # si c'est un spinner horizontal ou vertical
            # alors j'ajoute sa position dans la liste
            if cell == GridCell.SPINNER_HORIZONTAL or cell == GridCell.SPINNER_VERTICAL:
                spinners.append((x, y))

    # à la fin je renvoie toutes les positions trouvées
    return spinners

@dataclass
class Spinner:
    x: int
    y: int
    horizontal: bool #si faux donc il est vertical
    direction: Direction
    limites: Limites

def create_spinners(game_map: Map) -> list[Spinner]:

    # ici je vais stocker tous les objets Spinner que je vais créer
    spinners = []

    # je récupère d'abord les positions de tous les spinners dans la map
    positions = find_spinners(game_map)

    # je parcours chaque position trouvée
    for x, y in positions:

        # je regarde ce qu'il y a dans cette case
        cell = game_map.get(x, y)

        # je calcule les limites du spinner à partir de la map
        limites = compute_spinner_bounds(game_map, x, y)

        # ici je veux juste savoir s'il est horizontal ou pas
        # si la case est un spinner horizontal -> True
        # sinon ce sera False donc vertical
        horizontal = (cell == GridCell.SPINNER_HORIZONTAL)

        # d'après l'énoncé :
        # - spinner horizontal commence vers la droite
        # - spinner vertical commence vers le haut
        # dans les deux cas ça correspond au sens positif
        direction = Direction.POSITIF

        # maintenant je crée l'objet Spinner avec toutes ses infos
        spinner = Spinner(
            x=x,
            y=y,
            horizontal=horizontal,
            direction=direction,
            limites=limites
        )

        # j'ajoute ce spinner dans la liste finale
        spinners.append(spinner)

    # à la fin je renvoie la liste de tous les spinners créés
    return spinners

