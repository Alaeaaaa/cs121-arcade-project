from enum import Enum, auto

from direction import Direction
from textures import ANIMATION_SWORD
from weapon import Weapon


class SwordState(Enum):
    # L'épée existe dans le jeu, mais elle n'est pas en train d'attaquer.
    INACTIVE = auto()

    # L'épée est utilisée par le joueur : elle peut toucher les ennemis.
    ACTIVE = auto()


class Sword(Weapon):

    def __init__(self):
        # On crée l'épée comme une arme animée.
        # On met une animation par défaut vers le bas.
        super().__init__(
            animation=ANIMATION_SWORD[Direction.SOUTH],
            scale=1,
        )

        # Au début, le joueur n'attaque pas.
        self.state = SwordState.INACTIVE

        # Compteur utilisé pour savoir depuis combien de temps l'attaque est active.
        self.time = 0.0

    def is_active(self) -> bool:
        # L'épée est active seulement pendant l'attaque.
        return self.state == SwordState.ACTIVE

    def activate(self, direction: Direction) -> None:
        # Active l'épée dans la direction donnée.
        self.state = SwordState.ACTIVE
        self.direction = direction

        # On remet le temps à 0 au début de chaque attaque.
        self.time = 0.0

        # On met à jour l'animation selon la direction du joueur.
        self.update_direction_animation()

    def deactivate(self) -> None:
        # Désactive l'épée après l'attaque.
        self.state = SwordState.INACTIVE

        # On remet le compteur à 0 pour la prochaine attaque.
        self.time = 0.0

    def update_direction_animation(self) -> None:
        # ANIMATION_SWORD est un dictionnaire :
        # chaque direction correspond à une animation d'attaque.
        #
        # Exemple :
        # si self.direction vaut Direction.NORTH,
        # alors ANIMATION_SWORD[self.direction] donne l'animation d'attaque vers le haut.
        self.animation = ANIMATION_SWORD[self.direction]