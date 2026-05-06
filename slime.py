from dataclasses import dataclass

@dataclass
class Slime:
    start_x: int
    start_y: int
    destination_x: float
    destination_y: float
    x: float
    y: float
    possible_destinations: list[tuple[int, int]]

def find_slimes(game_map: Map) -> list[tuple[int, int]]: