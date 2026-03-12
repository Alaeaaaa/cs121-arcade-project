from typing import Final
import arcade

from constants import *
from textures import *

def grid_to_pixels(i:int) -> int:
    return i* TILE_SIZE + (TILE_SIZE // 2)


class GameView(arcade.View):
    """Main in-game view."""

    world_width: Final[int]
    world_height: Final[int]
    player: Final[arcade.Sprite]
    grounds: Final[arcade.Sprite]
    walls: Final[arcade.Sprite]

    def __init__(self) -> None:
        # Magical incantion: initialize the Arcade view
        super().__init__()

        # Choose a nice comfy background color
        self.background_color = arcade.csscolor.CORNFLOWER_BLUE

        # Setup our game
        self.world_width = 40 * TILE_SIZE
        self.world_height = 20 * TILE_SIZE

        #setup our player
        self.player = arcade.TextureAnimationSprite(
            animation=ANIMATION_PLAYER_IDLE_DOWN,
            scale=SCALE,
            center_x=grid_to_pixels(2),
            center_y=grid_to_pixels(2),
        )
        
        #setup the grounds and walls
        self.grounds = arcade.SpriteList(use_spatial_hash=True)
        for x in range(0,40):
            for y in range(0,20):
                sprite = arcade.Sprite(
                    TEXTURE_GRASS,
                    scale=SCALE, center_x=grid_to_pixels(x), center_y=grid_to_pixels(y) 
                )
                self.grounds.append(sprite)

        #setup the walls
        self.walls = arcade.SpriteList(use_spatial_hash=True)
        sprite1 = arcade.Sprite(
            TEXTURE_BUSH,
            scale=SCALE, center_x=grid_to_pixels(3), center_y=grid_to_pixels(6) 
        )
        sprite2 = arcade.Sprite(
            TEXTURE_BUSH,
            scale=SCALE, center_x=grid_to_pixels(7), center_y=grid_to_pixels(2) 
        )
        sprite3 = arcade.Sprite(
            TEXTURE_BUSH,
            scale=SCALE, center_x=grid_to_pixels(2), center_y=grid_to_pixels(10) 
        )
        sprite4= arcade.Sprite(
            TEXTURE_BUSH,
            scale=SCALE, center_x=grid_to_pixels(3), center_y=grid_to_pixels(8) 
        )
        self.walls.append(sprite1)
        self.walls.append(sprite2)
        self.walls.append(sprite3)
        self.walls.append(sprite4)

    def on_show_view(self) -> None:
        """Called automatically by 'window.show_view(game_view)' in main.py."""
        # When we show the view, adjust the window's size to our world size.
        # If the world size is smaller than the maximum window size, we should
        # limit the size of the window.
        self.window.width = min(MAX_WINDOW_WIDTH, self.world_width)
        self.window.height = min(MAX_WINDOW_HEIGHT, self.world_height)

    def on_draw(self) -> None:
        """Render the screen."""
        self.clear() # always start with self.clear()
        self.grounds.draw()
        self.walls.draw()
        arcade.draw_sprite(self.player)
