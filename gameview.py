from typing import Final
import arcade

from constants import *
from textures import *


def grid_to_pixels(i: int) -> int:
    return i * TILE_SIZE + (TILE_SIZE // 2)


class GameView(arcade.View):
    """Main in-game view."""

    world_width: Final[int]
    world_height: Final[int]

    player: Final[arcade.TextureAnimationSprite]
    player_list: Final[arcade.SpriteList[arcade.TextureAnimationSprite]]

    grounds: Final[arcade.SpriteList[arcade.Sprite]]
    walls: Final[arcade.SpriteList[arcade.Sprite]]

    def __init__(self) -> None:
        super().__init__()

        self.background_color = arcade.csscolor.CORNFLOWER_BLUE

        self.world_width = 40 * TILE_SIZE
        self.world_height = 20 * TILE_SIZE

        # Player (animated)
        self.player = arcade.TextureAnimationSprite(
            animation=ANIMATION_PLAYER_IDLE_DOWN,
            scale=SCALE,
            center_x=grid_to_pixels(2),
            center_y=grid_to_pixels(2),
        )

        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player)

        # Ground and walls
        self.grounds = arcade.SpriteList(use_spatial_hash=True)
        self.walls = arcade.SpriteList(use_spatial_hash=True)

        # Grass everywhere
        for x in range(40):
            for y in range(20):
                self.grounds.append(
                    arcade.Sprite(
                        TEXTURE_GRASS,
                        scale=SCALE,
                        center_x=grid_to_pixels(x),
                        center_y=grid_to_pixels(y),
                    )
                )

        # Bushes (walls)
        bush_positions = [(3, 6), (7, 2), (2, 10), (3, 8)]
        for x, y in bush_positions:
            self.walls.append(
                arcade.Sprite(
                    TEXTURE_BUSH,
                    scale=SCALE,
                    center_x=grid_to_pixels(x),
                    center_y=grid_to_pixels(y),
                )
            )

    def on_show_view(self) -> None:
        self.window.width = min(MAX_WINDOW_WIDTH, self.world_width)
        self.window.height = min(MAX_WINDOW_HEIGHT, self.world_height)

    def on_draw(self) -> None:
        self.clear()
        self.grounds.draw()
        self.walls.draw()
        self.player_list.draw()

    def on_update(self, delta_time: float) -> None:
        # Update animation each frame
        self.player.update_animation()