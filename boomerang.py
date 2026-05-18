from enum import Enum, auto

from direction import Direction
from textures import ANIMATION_BOOMERANG
from weapon import Weapon


# Taille visuelle du boomerang dans le jeu.
BOOMERANG_SCALE = 2


class BoomerangState(Enum):
    # Le boomerang n'est pas lancé.
    INACTIVE = auto()

    # Le boomerang part depuis le joueur.
    LAUNCHING = auto()

    # Le boomerang revient vers le joueur.
    RETURNING = auto()


class Boomerang(Weapon):

    def __init__(self):
        # On crée le boomerang comme une arme animée.
        # Son animation est chargée dans textures.py.
        super().__init__(
            animation=ANIMATION_BOOMERANG,
            scale=BOOMERANG_SCALE,
        )

        # Au début, le boomerang n'est pas utilisé.
        self.state = BoomerangState.INACTIVE

        # Distance déjà parcourue pendant la phase LAUNCHING.
        # Quand cette distance devient assez grande, le boomerang commence à revenir.
        self.distance_travelled = 0.0

    def is_active(self) -> bool:
        # Le boomerang est actif s'il est lancé ou s'il revient.
        return self.state != BoomerangState.INACTIVE

    def launch(self, direction: Direction, x: float, y: float) -> None:
        # Lance le boomerang depuis la position donnée.
        self.state = BoomerangState.LAUNCHING

        # Le boomerang part dans la direction actuelle du joueur.
        self.direction = direction

        # On place le boomerang au niveau du joueur.
        self.center_x = x
        self.center_y = y

        # On remet la distance à 0 à chaque nouveau lancer.
        self.distance_travelled = 0.0

    def return_to_player(self) -> None:
        # Le boomerang arrête d'avancer et commence à revenir vers le joueur.
        self.state = BoomerangState.RETURNING

    def deactivate(self) -> None:
        # Désactive le boomerang quand il revient au joueur.
        self.state = BoomerangState.INACTIVE

        # On remet la distance à 0 pour le prochain lancer.
        self.distance_travelled = 0.0