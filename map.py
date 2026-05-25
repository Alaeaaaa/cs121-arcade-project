from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Final, Any
from abc import ABC, abstractmethod

import yaml


# ==================================================
# Types de cellules possibles dans la map
# ==================================================

class GridCell(Enum):
    GRASS = auto()
    BUSH = auto()
    CRYSTAL = auto()
    SHIELD = auto()
    SPINNER_HORIZONTAL = auto()
    SPINNER_VERTICAL = auto()
    HOLE = auto()
    BAT = auto()
    SLIME = auto()
    SWITCH = auto()
    GATE = auto()


# ==================================================
# Exceptions
# ==================================================

class InvalidMapFileException(Exception):
    pass


# ==================================================
# Formules logiques pour les portails
# ==================================================

class GateCondition(ABC):
    @abstractmethod
    def evaluate(self, switch_states: dict[str, bool]) -> bool: 
        ...
        


@dataclass(frozen=True)
class SwitchIsOn(GateCondition):
    switch_id: str

    def evaluate(self, switch_states: dict[str, bool]) -> bool:
        if self.switch_id not in switch_states:
            raise InvalidMapFileException(
                f"Switch inconnu dans une condition : {self.switch_id}"
                # La map est invalide, car elle parle d'un switch qui n'existe pas.
            )
        return switch_states[self.switch_id]


@dataclass(frozen=True)
class NotCondition(GateCondition):
    condition: GateCondition

    def evaluate(self, switch_states: dict[str, bool]) -> bool:
        return not self.condition.evaluate(switch_states)


@dataclass(frozen=True)
class AndCondition(GateCondition):
    left: GateCondition
    right: GateCondition

    def evaluate(self, switch_states: dict[str, bool]) -> bool:
        return (
            self.left.evaluate(switch_states)
            and self.right.evaluate(switch_states)
        )


@dataclass(frozen=True)
class OrCondition(GateCondition):
    left: GateCondition
    right: GateCondition

    def evaluate(self, switch_states: dict[str, bool]) -> bool:
        return (
            self.left.evaluate(switch_states)
            or self.right.evaluate(switch_states)
        )


def parse_gate_condition(data: Any) -> GateCondition:
    # Une condition de portail est un dictionnaire YAML avec exactement une clef.
    # Exemples valides :
    #   { switch_is_on: "s1" }
    #   { not: [{ switch_is_on: "s1" }] }
    #   { and: [{ switch_is_on: "s1" }, { switch_is_on: "s2" }] }
    if not isinstance(data, dict):
        raise InvalidMapFileException("Une condition de portail doit être un dictionnaire")

    if len(data) != 1:
        raise InvalidMapFileException("Une condition doit avoir exactement une clef")

    key = next(iter(data))
    value = data[key]

    if key == "switch_is_on":
        if not isinstance(value, str):
            raise InvalidMapFileException("switch_is_on doit contenir un id de switch")
        return SwitchIsOn(value)

    if key == "not":
        if not isinstance(value, list) or len(value) != 1:
            raise InvalidMapFileException("not doit contenir une liste de 1 condition")
        return NotCondition(parse_gate_condition(value[0]))

    if key == "and":
        if not isinstance(value, list) or len(value) != 2:
            raise InvalidMapFileException("and doit contenir une liste de 2 conditions")
        return AndCondition(
            parse_gate_condition(value[0]),
            parse_gate_condition(value[1]),
        )

    if key == "or":
        if not isinstance(value, list) or len(value) != 2:
            raise InvalidMapFileException("or doit contenir une liste de 2 conditions")
        return OrCondition(
            parse_gate_condition(value[0]),
            parse_gate_condition(value[1]),
        )

    raise InvalidMapFileException(f"Condition inconnue : {key}")


# ==================================================
# Config des switches et gates
# ==================================================

@dataclass(frozen=True)
class SwitchConfig:
    switch_id: str
    x: int
    y: int
    is_on: bool


@dataclass(frozen=True)
class GateConfig:
    x: int
    y: int
    open_if: GateCondition


def parse_switch_config(data: Any) -> SwitchConfig:
    if not isinstance(data, dict):
        raise InvalidMapFileException("Chaque switch doit être un dictionnaire")

    switch_id = data.get("id")
    x = data.get("x")
    y = data.get("y")
    state = data.get("state", "off")

    if not isinstance(switch_id, str):
        raise InvalidMapFileException("Chaque switch doit avoir un id str")

    if not isinstance(x, int) or not isinstance(y, int):
        raise InvalidMapFileException("Chaque switch doit avoir x et y entiers")

    if state not in {"on", "off"}:
        raise InvalidMapFileException("L'état d'un switch doit être on ou off")

    return SwitchConfig(
        switch_id=switch_id,
        x=x,
        y=y,
        is_on=(state == "on"),
    )


def parse_gate_config(data: Any) -> GateConfig:
    if not isinstance(data, dict):
        raise InvalidMapFileException("Chaque gate doit être un dictionnaire")

    x = data.get("x")
    y = data.get("y")
    open_if = data.get("open_if")

    if not isinstance(x, int) or not isinstance(y, int):
        raise InvalidMapFileException("Chaque gate doit avoir x et y entiers")

    if open_if is None:
        raise InvalidMapFileException("Chaque gate doit avoir open_if")

    return GateConfig(x=x, y=y, open_if=parse_gate_condition(open_if))


def parse_switches(data: Any) -> list[SwitchConfig]:
    if data is None:
        return []
    if not isinstance(data, list):
        raise InvalidMapFileException("switches doit être une liste")
    return [parse_switch_config(item) for item in data]


def parse_gates(data: Any) -> list[GateConfig]:
    if data is None:
        return []
    if not isinstance(data, list):
        raise InvalidMapFileException("gates doit être une liste")
    return [parse_gate_config(item) for item in data]


# ==================================================
# Map
# ==================================================

class Map:
    width: Final[int]
    height: Final[int]
    player_start_x: Final[int]
    player_start_y: Final[int]
    switch_configs: Final[list[SwitchConfig]]
    gate_configs: Final[list[GateConfig]]
    _cells: list[list[GridCell]]

    def __init__(
        self,
        width: int,
        height: int,
        player_start_x: int,
        player_start_y: int,
        switch_configs: list[SwitchConfig],
        gate_configs: list[GateConfig],
    ) -> None:
        self.width = width
        self.height = height
        self.player_start_x = player_start_x
        self.player_start_y = player_start_y
        self.switch_configs = switch_configs
        self.gate_configs = gate_configs

        # Par défaut, toutes les cellules sont de l'herbe.
        # Elles seront remplacées au moment du chargement de la map.
        self._cells = [
            [GridCell.GRASS for _ in range(width)]
            for _ in range(height)
        ]

    def get(self, x: int, y: int) -> GridCell:
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            raise ValueError("Coordonnées hors de la grille")
        return self._cells[y][x]


# ==================================================
# Lecture du fichier
# ==================================================

def map_from_file(path: str) -> Map:
    with open(path, "r") as f:
        text = f.read()
    return map_from_string(text)


def split_map_file(text: str) -> tuple[str, list[str]]:
    # Un fichier de map est divisé en trois parties par "---" :
    #   1. La configuration YAML (width, height, switches, gates...)
    #   2. La grille de caractères
    #   3. (vide, juste pour terminer proprement le fichier)
    parts = text.split("---")

    if len(parts) != 3:
        raise InvalidMapFileException("Le fichier doit contenir deux séparateurs ---")

    config_text = parts[0]
    grid_lines = parts[1].strip("\n").split("\n")

    return config_text, grid_lines


def parse_config(config_text: str) -> dict[str, Any]:
    data = yaml.safe_load(config_text)

    if not isinstance(data, dict):
        raise InvalidMapFileException("La configuration YAML doit être un dictionnaire")

    return data


# Dictionnaire de conversion caractère → cellule.
#
# Avantage par rapport à une chaîne de if/elif :
# pour ajouter un nouveau type de cellule, il suffit d'ajouter
# une ligne ici, sans toucher à la logique de cell_from_char.

_CHAR_TO_CELL: dict[str, GridCell] = {
    " ": GridCell.GRASS,
    "x": GridCell.BUSH,
    "*": GridCell.CRYSTAL,
    "O": GridCell.HOLE,
    "s": GridCell.SPINNER_HORIZONTAL,
    "S": GridCell.SPINNER_VERTICAL,
    "v": GridCell.BAT,
    "m": GridCell.SLIME,
    "^": GridCell.SWITCH,
    "|": GridCell.GATE,
    "P": GridCell.GRASS,
    "A": GridCell.SHIELD,
}


def cell_from_char(char: str, x: int, y: int) -> GridCell:
    if char not in _CHAR_TO_CELL:
        raise InvalidMapFileException(
            f"Caractère inconnu dans la map à ({x}, {y}) : {char}"
        )
    return _CHAR_TO_CELL[char]


def validate_switches_and_gates(
    cells: list[list[GridCell]],
    switch_configs: list[SwitchConfig],
    gate_configs: list[GateConfig],
) -> None:
    # On vérifie que chaque switch déclaré dans le YAML
    # a bien un '^' à sa position dans la grille.
    switch_ids: set[str] = set()

    for switch_config in switch_configs:
        if switch_config.switch_id in switch_ids:
            raise InvalidMapFileException(
                f"Id de switch dupliqué : {switch_config.switch_id}"
            )
        switch_ids.add(switch_config.switch_id)

        if cells[switch_config.y][switch_config.x] != GridCell.SWITCH:
            raise InvalidMapFileException(
                f"Il doit y avoir un ^ à la position du switch {switch_config.switch_id}"
            )

    # Même vérification pour les portails : chaque gate doit avoir un '|'.
    for gate_config in gate_configs:
        if cells[gate_config.y][gate_config.x] != GridCell.GATE:
            raise InvalidMapFileException(
                "Il doit y avoir un | à la position d'un gate"
            )


@dataclass
class _GridParseResult:
    
    #Résultat intermédiaire de la construction de la grille.
    #On sépare la construction de la grille dans sa propre fonction pour que map_from_string reste lisible : 
    # elle orchestre les étapes, _parse_grid s'occupe du détail ligne par ligne.

    cells: list[list[GridCell]]
    player_x: int
    player_y: int


def _parse_grid(grid_lines: list[str], width: int, height: int) -> _GridParseResult:
    
    #Construit la grille de cellules depuis les lignes de texte.
    #Cherche la position de départ du joueur ('P') au passage.
    
    if len(grid_lines) != height:
        raise InvalidMapFileException("La hauteur de la map ne correspond pas")

    player_x = None
    player_y = None
    cells: list[list[GridCell]] = []

    for y in range(height):
        line = grid_lines[y]

        if len(line) != width:
            raise InvalidMapFileException(f"La ligne {y} n'a pas la bonne largeur")

        row: list[GridCell] = []

        for x in range(width):
            char = line[x]

            if char == "P":
                # On mémorise la position de départ du joueur.
                # S'il y en a plusieurs, la map est invalide.
                if player_x is not None:
                    raise InvalidMapFileException(
                        "La map contient plusieurs positions de départ"
                    )
                player_x = x
                player_y = y

            row.append(cell_from_char(char, x, y))

        cells.append(row)

    if player_x is None or player_y is None:
        raise InvalidMapFileException("La map ne contient pas de position de départ")

    return _GridParseResult(cells=cells, player_x=player_x, player_y=player_y)


def map_from_string(text: str) -> Map:
    # Étape 1 : séparer le fichier en config YAML et grille de caractères.
    config_text, grid_lines = split_map_file(text)
    config = parse_config(config_text)

    width = config.get("width")
    height = config.get("height")

    if not isinstance(width, int):
        raise InvalidMapFileException("width doit être un entier")

    if not isinstance(height, int):
        raise InvalidMapFileException("height doit être un entier")

    # Étape 2 : parser les switches et gates depuis la config YAML.
    switch_configs = parse_switches(config.get("switches"))
    gate_configs = parse_gates(config.get("gates"))

    # Étape 3 : construire la grille et trouver la position du joueur.
    grid = _parse_grid(grid_lines, width, height)

    # Étape 4 : valider que les switches et gates sont bien placés dans la grille.
    validate_switches_and_gates(grid.cells, switch_configs, gate_configs)

    # Étape 5 : assembler l'objet Map final.
    game_map = Map(
        width=width,
        height=height,
        player_start_x=grid.player_x,
        player_start_y=grid.player_y,
        switch_configs=switch_configs,
        gate_configs=gate_configs,
    )

    game_map._cells = grid.cells

    return game_map


MAP_DECOUVERTE: Final[Map] = Map(
    width=40,
    height=20,
    player_start_x=2,
    player_start_y=2,
    switch_configs=[],
    gate_configs=[],
)