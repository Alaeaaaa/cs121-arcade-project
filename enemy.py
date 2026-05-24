from abc import ABC, abstractmethod

import arcade


class Enemy(arcade.Sprite, ABC):

    @abstractmethod
    def update_logic(self, **kwargs) -> None:
        pass

    def sync_sprite(self) -> None:
        pass