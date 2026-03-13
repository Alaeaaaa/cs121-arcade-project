from enum import Enum
from typing import Final


# Types de cellules possibles dans la map
class GridCell(Enum):
    GRASS = 1
    BUSH = 2
    CRYSTAL = 3
    SPINNER_HORIZONTAL = 4
    SPINNER_VERTICAL = 5
    HOLE = 6


class Map:
    width: Final[int]
    height: Final[int]
    player_start_x: Final[int]
    player_start_y: Final[int]
    _cells: Final[list[list[GridCell]]]

    def __init__(self, width: int, height: int, player_start_x: int, player_start_y: int) -> None:
        # on garde juste les infos principales
        self.width = width
        self.height = height
        self.player_start_x = player_start_x
        self.player_start_y = player_start_y

        # ici je crée la grille de base
        # au début je mets tout en GRASS par défaut
        grid = []
        for _ in range(self.height):
            row = []
            for _ in range(self.width):
                row.append(GridCell.GRASS)
            grid.append(row)

        self._cells = grid

    def get(self, x: int, y: int) -> GridCell:
        # petite sécurité : si on demande une case hors de la map
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            raise ValueError("Coordonnées hors de la grille")

        # sinon on renvoie la cellule correspondante
        return self._cells[y][x]


# exception spéciale pour les erreurs de map
# le but est d'éviter un gros traceback incompréhensible pour l'utilisateur
class InvalidMapFileException(Exception):
    pass


def map_from_file(path: str) -> Map:
    # fonction simple : elle lit juste le fichier
    # puis appelle map_from_string qui fait le vrai travail
    with open(path, "r") as f:
        text = f.read()

    return map_from_string(text)


def map_from_string(text: str) -> Map:

    # je transforme tout le texte en liste de lignes
    lines = text.strip().split("\n")

    # si le fichier est trop petit c'est sûrement invalide
    if len(lines) < 4:
        raise InvalidMapFileException("Fichier de map invalide")

    # normalement la première ligne contient width
    if not lines[0].startswith("width:"):
        raise InvalidMapFileException("Largeur manquante dans la map")

    # deuxième ligne contient height
    if not lines[1].startswith("height:"):
        raise InvalidMapFileException("Hauteur manquante dans la map")

    # je récupère les valeurs
    width = int(lines[0].split(":")[1].strip())
    height = int(lines[1].split(":")[1].strip())

    # la troisième ligne doit être ---
    if lines[2] != "---":
        raise InvalidMapFileException("Format de map invalide")

    # ici je récupère seulement les lignes de la grille
    # donc j'enlève l'entête et le dernier ---
    grid_lines = lines[3:-1]

    # vérifie que le nombre de lignes correspond à height
    if len(grid_lines) != height:
        raise InvalidMapFileException("La hauteur de la map ne correspond pas")

    player_x = None
    player_y = None

    # cette liste va contenir la vraie grille
    cells = []

    # je parcours chaque ligne de la map
    for y in range(height):

        line = grid_lines[y]

        # vérifie que toutes les lignes ont la bonne largeur
        if len(line) != width:
            raise InvalidMapFileException(
                "Toutes les lignes de la map doivent avoir la même longueur"
            )

        row = []

        # maintenant je lis chaque caractère de la ligne
        for x in range(width):

            char = line[x]

            # espace = herbe
            if char == " ":
                row.append(GridCell.GRASS)

            # x = buisson
            elif char == "x":
                row.append(GridCell.BUSH)

            # * = cristal
            elif char == "*":
                row.append(GridCell.CRYSTAL)

            elif char == "O":
                row.append(GridCell.HOLE)

            # s = spinner horizontal
            elif char == "s":
                row.append(GridCell.SPINNER_HORIZONTAL)

            # S = spinner vertical
            elif char == "S":
                row.append(GridCell.SPINNER_VERTICAL)

            # P = position de départ du joueur
            elif char == "P":

                # si on trouve deux P c'est une erreur
                if player_x is not None:
                    raise InvalidMapFileException(
                        "La map contient plusieurs positions de départ"
                    )

                player_x = x
                player_y = y

                # on met quand même GRASS dans la cellule
                # car P indique seulement le départ du joueur
                row.append(GridCell.GRASS)

            else:
                # si le caractère est inconnu on stoppe
                raise InvalidMapFileException(
                    f"Caractère inconnu dans la map : {char}"
                )

        # on ajoute la ligne construite à la grille
        cells.append(row)

    # si on n'a jamais trouvé P
    if player_x is None:
        raise InvalidMapFileException(
            "La map ne contient pas de position de départ"
        )

    # on crée la map finale
    game_map = Map(width, height, player_x, player_y)

    # on remplace la grille par celle qu'on vient de construire
    game_map._cells = cells

    return game_map


# map simple utilisée au début du projet
MAP_DECOUVERTE: Final[Map] = Map(40, 20, 2, 2)