from abc import ABC, abstractmethod

import arcade


class Enemy(arcade.TextureAnimationSprite, ABC):

    def __init__(self, animation: arcade.TextureAnimation, scale: float) -> None:
        super().__init__(animation=animation, scale=scale)

    @abstractmethod
    def update_logic(self, **kwargs) -> None:
        pass

    def sync_sprite(self) -> None:
        pass