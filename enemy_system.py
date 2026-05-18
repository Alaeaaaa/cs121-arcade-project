from __future__ import annotations

from typing import Generic, TypeVar

import arcade

TLogic = TypeVar("TLogic")
TSprite = TypeVar("TSprite", bound=arcade.Sprite)


class EnemySystem(Generic[TLogic, TSprite]):
    """
    Associe une liste de données logiques à une SpriteList parallèle.

    Invariant : logic[i] correspond toujours à sprites[i].
    """

    def __init__(
        self,
        logic: list[TLogic],
        sprites: arcade.SpriteList,
    ) -> None:
        self.logic = logic
        self.sprites = sprites

    def remove_sprite(self, target: arcade.Sprite) -> None:
        """Supprime un sprite et son objet logique associé."""
        for i, sprite in enumerate(self.sprites):
            if sprite is target:
                sprite.remove_from_sprite_lists()
                self.logic.pop(i)
                return

    def weapon_hits(self, weapon: arcade.Sprite) -> bool:
        """
        Vérifie les collisions entre l'arme et les sprites ennemis.
        Supprime les ennemis touchés. Retourne True si au moins un ennemi touché.
        """
        hit = arcade.check_for_collision_with_list(weapon, self.sprites)

        for sprite in hit:
            self.remove_sprite(sprite)

        return len(hit) > 0

    def update_animations(self) -> None:
        for sprite in self.sprites:
            sprite.update_animation()

    def __len__(self) -> int:
        return len(self.logic)