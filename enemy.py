from dataclasses import dataclass
from abc import abstractmethod
from abc import abstractmethod

import arcade
from navmesh import NavMesh, Point
import random
@dataclas
class EnemyContext:
    """cette classe est vraiment juste utile pour la fonction update,
    ça nous permet de garder update comme méthode abstraite sans passer par **kwargs
    qui rend le checker pas content quand on override la méthode pour le slime.
    de cette façon, on garde la même structure, on définit EnemyContext dans gameview
    avant de le passer à update, chaque type de monstre utilise les données dont il a besoin."""
    navmesh: NavMesh
    rng: random.Random
    player_position: Point
    walls: arcade.SpriteList


class Enemy(arcade.TextureAnimationSprite):
    """classe commune à tous nos ennemis. On hérite de textureanimationsprite
    car tous les ennemis ont une position, animation, échelle...
    les ennemis ont également tous une logique qu'il faut mettre à jour : update_logic()
    et il faut lier l'aspect logique au visuel : sync_sprite() """


class Enemy(arcade.TextureAnimationSprite):


    def __init__(self, animation: arcade.TextureAnimation, scale: float) -> None:
        super().__init__(animation=animation, scale=scale)

    @abstractmethod

    def update_logic(self, context:EnemyContext) -> None:
        """après je ne sais pas combien de refactoring, on souffle enfin.
        on s'est débarassé des **kwargs en introduisant la nouvelle classe EnemyContext.
        chaque ennemi utilise alors les données dont il a besoin."""
        ...
    @abstractmethod
    def sync_sprite(self) -> None:
        """synchronise simplement la position du sprite en accord avec la logique"""
        ...

    def update_logic(self, **kwargs) -> None:
        ...

    def sync_sprite(self) -> None:
        ...

