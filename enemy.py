from abc import abstractmethod
import arcade


class Enemy(arcade.TextureAnimationSprite):
    """classe commune à tous nos ennemis. On hérite de textureanimationsprite
    car tous les ennemis ont une position, animation, échelle...
    les ennemis ont également tous une logique qu'il faut mettre à jour : update_logic()
    et il faut lier l'aspect logique au visuel : sync_sprite() """

    def __init__(self, animation: arcade.TextureAnimation, scale: float) -> None:
        super().__init__(animation=animation, scale=scale)

    @abstractmethod
    def update_logic(self, **kwargs) -> None:
        """c'est la meilleure façon à laquelle on a pensé sans définir de nouvelle classe.
        sans les **kwargs, on aurait défini une nouvelle classe avec les attributs nécessaires
        au fonctionnement de chaque ennemi, parfois trop, parfois rien."""
        ...
    @abstractmethod
    def sync_sprite(self) -> None:
        """synchronise simplement la position du sprite en accord avec la logique"""
        ...
