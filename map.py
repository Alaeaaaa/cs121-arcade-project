from enum import Enum, auto
from typing import Final


class GridCell(Enum):
    GRASS = auto()
    BUSH = auto()
    CRYSTAL = auto()
    SPINNER_HORIZONTAL = auto()
    SPINNER_VERTICAL = auto()
    HOLE = auto()
    BAT = auto()
    SLIME = auto()


class Map:
    width: Final[int]
    height: Final[int]
    player_start_x: Final[int]
    player_start_y: Final[int]
    _cells: Final[list[list[GridCell]]]

    def __init__(self, width: int, height: int, player_start_x: int, player_start_y: int) -> None:
        self.width = width
        self.height = height
        self.player_start_x = player_start_x
        self.player_start_y = player_start_y

        grid = []
        for _ in range(self.height):
            row = []
            for _ in range(self.width):
                row.append(GridCell.GRASS)
            grid.append(row)

        self._cells = grid

    def get(self, x: int, y: int) -> GridCell:
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            raise ValueError("Coordonnées hors de la grille")

        # _cells est une liste de lignes :
        # _cells[y] = ligne y
        # _cells[y][x] = case x dans cette ligne
        return self._cells[y][x]


class InvalidMapFileException(Exception):
    pass


def map_from_file(path: str) -> Map:
    with open(path, "r") as f:
        text = f.read()

    return map_from_string(text)


def map_from_string(text: str) -> Map:

    # Exemple text :
    # "\nwidth: 5\nheight: 3\n---\nP x  \n  *  \n---\n"
    #
    # strip() enlève les \n ou espaces au début/à la fin.
    # split("\n") coupe le texte en lignes.
    #
    # Résultat :
    # ["width: 5", "height: 3", "---", "P x  ", "  *  ", "---"]
    lines = text.strip().split("\n")

    if len(lines) < 4:
        raise InvalidMapFileException("Fichier de map invalide")

    if not lines[0].startswith("width:"):
        raise InvalidMapFileException("Largeur manquante dans la map")

    if not lines[1].startswith("height:"):
        raise InvalidMapFileException("Hauteur manquante dans la map")

    # Exemple : lines[0] = "width: 5"
    # split(":") donne ["width", " 5"]
    # [1] prend " 5"
    # strip() donne "5"
    # int("5") donne 5
    width = int(lines[0].split(":")[1].strip())

    # Même idée :
    # "height: 3" -> ["height", " 3"] -> "3" -> 3
    height = int(lines[1].split(":")[1].strip())

    if lines[2] != "---":
        raise InvalidMapFileException("Format de map invalide")

    # Exemple :
    # lines = ["width: 5", "height: 3", "---", "P x  ", "  *  ", "---"]
    #
    # lines[3:-1] prend les lignes de la grille :
    # à partir de l’indice 3, sans prendre le dernier "---".
    #
    # Résultat :
    # ["P x  ", "  *  "]
    grid_lines = lines[3:-1]

    if len(grid_lines) != height:
        raise InvalidMapFileException("La hauteur de la map ne correspond pas")

    player_x = None
    player_y = None
    cells = []

    for y in range(height):
        line = grid_lines[y]

        if len(line) != width:
            raise InvalidMapFileException(
                "Toutes les lignes de la map doivent avoir la même longueur"
            )

        row = []

        for x in range(width):
            char = line[x]

            if char == " ":
                row.append(GridCell.GRASS)
            elif char == "x":
                row.append(GridCell.BUSH)
            elif char == "*":
                row.append(GridCell.CRYSTAL)
            elif char == "O":
                row.append(GridCell.HOLE)
            elif char == "s":
                row.append(GridCell.SPINNER_HORIZONTAL)
            elif char == "S":
                row.append(GridCell.SPINNER_VERTICAL)
            elif char == "v":
                row.append(GridCell.BAT)
            # m = slime / blob
            elif char == "m":
                row.append(GridCell.SLIME)

            elif char == "P":
                if player_x is not None:
                    raise InvalidMapFileException(
                        "La map contient plusieurs positions de départ"
                    )

                player_x = x
                player_y = y

                # P indique seulement le départ du joueur.
                # La case elle-même reste de l’herbe.
                row.append(GridCell.GRASS)

            else:
                raise InvalidMapFileException(
                    f"Caractère inconnu dans la map : {char}"
                )

        cells.append(row)

    if player_x is None:
        raise InvalidMapFileException(
            "La map ne contient pas de position de départ"
        )

    game_map = Map(width, height, player_x, player_y)

    # On remplace la grille remplie d’herbe par la vraie grille lue.
    game_map._cells = cells

    return game_map


MAP_DECOUVERTE: Final[Map] = Map(40, 20, 2, 2)