from typing import Final
import arcade

ORIG_TILE_SIZE = (16, 16)


def _load_grid(
    file: str,
    columns: int,
    rows: int,
    tile_size: tuple[int, int] = ORIG_TILE_SIZE,
) -> list[arcade.Texture]:
    """
    Loads a texture grid from a spritesheet.
    """
    spritesheet = arcade.load_spritesheet(file)
    return spritesheet.get_texture_grid(tile_size, columns, columns * rows)


def _load_animation_strip(
    file: str,
    frame_count: int,
    frame_duration: int = 100,
    tile_size: tuple[int, int] = ORIG_TILE_SIZE,
) -> arcade.TextureAnimation:
    """
    Loads an animation strip from a line-oriented spritesheet.
    """
    grid = _load_grid(file, columns=frame_count, rows=1, tile_size=tile_size)
    keyframes = [arcade.TextureKeyframe(frame, frame_duration) for frame in grid]
    return arcade.TextureAnimation(keyframes)


_overworld_grid = _load_grid(
    "assets/Top_Down_Adventure_Pack_v.1.0/Overworld_Tileset.png",
    18,
    13,
)

TEXTURE_GRASS: Final[arcade.Texture] = _overworld_grid[18 * 1 + 6]
TEXTURE_BUSH: Final[arcade.Texture] = _overworld_grid[18 * 3 + 5]

ANIMATION_PLAYER_IDLE_DOWN: Final[arcade.TextureAnimation] = _load_animation_strip(
    "assets/Top_Down_Adventure_Pack_v.1.0/Char_Sprites/char_idle_down_anim_strip_6.png",
    6,
)