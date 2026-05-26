from __future__ import annotations

from typing import Final

import arcade

from direction import Direction


# ==================================================
# Chemins vers les assets
# ==================================================

ORIG_TILE_SIZE: Final[tuple[int, int]] = (16, 16)

"""après refactorisation, il est bcp plus simple de réécrire les racines communes des assets."""
ASSET_ROOT: Final[str] = "assets/Top_Down_Adventure_Pack_v.1.0"
CHAR_SPRITES: Final[str] = f"{ASSET_ROOT}/Char_Sprites"
ENEMY_SPRITES: Final[str] = f"{ASSET_ROOT}/Enemies_Sprites"
ITEM_SPRITES: Final[str] = f"{ASSET_ROOT}/Props_Items_(animated)"


# ==================================================
# Fonctions utilitaires de chargement
# ==================================================

def _load_grid(
    file: str,
    columns: int,
    rows: int,
    tile_size: tuple[int, int] = ORIG_TILE_SIZE,
) -> list[arcade.Texture]:
    spritesheet = arcade.load_spritesheet(file)

    return spritesheet.get_texture_grid(
        tile_size,
        columns,
        columns * rows,
    )


def _load_animation_strip(
    file: str,
    frame_count: int,
    frame_duration: int = 100,
    tile_size: tuple[int, int] = ORIG_TILE_SIZE,
) -> arcade.TextureAnimation:
    grid = _load_grid(
        file,
        columns=frame_count,
        rows=1,
        tile_size=tile_size,
    )

    keyframes = [
        arcade.TextureKeyframe(frame, frame_duration)
        for frame in grid
    ]

    return arcade.TextureAnimation(keyframes)


def _load_player_animation(
    action: str,
    direction: str,
) -> arcade.TextureAnimation:
    """spécifique au joueur"""
    return _load_animation_strip(
        f"{CHAR_SPRITES}/char_{action}_{direction}_anim_strip_6.png",
        frame_count=6,
    )


def _load_sword_animation(direction: str) -> arcade.TextureAnimation:
    """spécifique à l'épée, car ayant des animations en fct de la direction"""
    return _load_animation_strip(
        f"{CHAR_SPRITES}/char_attack48_{direction}_anim_strip_6.png",
        frame_count=6,
        frame_duration=50,
        tile_size=(48, 48),
    )


# ==================================================
# Tilesets
# ==================================================

_overworld_grid = _load_grid(
    f"{ASSET_ROOT}/Overworld_Tileset.png",
    columns=18,
    rows=13,
)

_dungeon_grid = _load_grid(
    f"{ASSET_ROOT}/Dungeon_Tileset.png",
    columns=13,
    rows=12,
)


# ==================================================
# Textures de terrain
# ==================================================

TEXTURE_GRASS: Final[arcade.Texture] = _overworld_grid[18 * 1 + 6]
TEXTURE_BUSH: Final[arcade.Texture] = _overworld_grid[18 * 3 + 5]
TEXTURE_HOLE: Final[arcade.Texture] = _overworld_grid[18 * 4 + 8]

# ==================================================
# Texture du bouclier
# ==================================================

TEXTURE_SHIELD: Final[arcade.Texture] = arcade.load_texture(
    ":resources:/images/items/star.png"
)


# ==================================================
# Textures des interrupteurs
# ==================================================

TEXTURE_SWITCH_OFF: Final[arcade.Texture] = arcade.load_texture(
    ":resources:/images/tiles/leverLeft.png"
)

TEXTURE_SWITCH_ON: Final[arcade.Texture] = arcade.load_texture(
    ":resources:/images/tiles/leverRight.png"
)


# ==================================================
# Textures des portails
# ==================================================

TEXTURE_GATE_OPEN: Final[arcade.Texture] = _dungeon_grid[13 * 8 + 4]
TEXTURE_GATE_CLOSED: Final[arcade.Texture] = _dungeon_grid[13 * 8 + 7]


# ==================================================
# Directions
# ==================================================

DIRECTION_NAMES: Final[dict[Direction, str]] = {
    Direction.SOUTH: "down",
    Direction.NORTH: "up",
    Direction.WEST: "left",
    Direction.EAST: "right",
}


# ==================================================
# Animations du joueur
# ==================================================

PLAYER_IDLE_ANIMATIONS: Final[dict[Direction, arcade.TextureAnimation]] = {
    direction: _load_player_animation("idle", file_direction)
    for direction, file_direction in DIRECTION_NAMES.items()
}

PLAYER_RUN_ANIMATIONS: Final[dict[Direction, arcade.TextureAnimation]] = {
    direction: _load_player_animation("run", file_direction)
    for direction, file_direction in DIRECTION_NAMES.items()
}
"""programmation dynamique: il est mieux de stocker une seule fois les animations
que de les recaculer à chaque fois."""

#refactoring
ANIMATION_PLAYER_IDLE_DOWN: Final[arcade.TextureAnimation] = PLAYER_IDLE_ANIMATIONS[
    Direction.SOUTH
]
ANIMATION_PLAYER_IDLE_UP: Final[arcade.TextureAnimation] = PLAYER_IDLE_ANIMATIONS[
    Direction.NORTH
]
ANIMATION_PLAYER_IDLE_LEFT: Final[arcade.TextureAnimation] = PLAYER_IDLE_ANIMATIONS[
    Direction.WEST
]
ANIMATION_PLAYER_IDLE_RIGHT: Final[arcade.TextureAnimation] = PLAYER_IDLE_ANIMATIONS[
    Direction.EAST
]

ANIMATION_PLAYER_RUN_DOWN: Final[arcade.TextureAnimation] = PLAYER_RUN_ANIMATIONS[
    Direction.SOUTH
]
ANIMATION_PLAYER_RUN_UP: Final[arcade.TextureAnimation] = PLAYER_RUN_ANIMATIONS[
    Direction.NORTH
]
ANIMATION_PLAYER_RUN_LEFT: Final[arcade.TextureAnimation] = PLAYER_RUN_ANIMATIONS[
    Direction.WEST
]
ANIMATION_PLAYER_RUN_RIGHT: Final[arcade.TextureAnimation] = PLAYER_RUN_ANIMATIONS[
    Direction.EAST
]


# ==================================================
# Animations des objets et monstres
# ==================================================

ANIMATION_CRYSTAL: Final[arcade.TextureAnimation] = _load_animation_strip(
    f"{ITEM_SPRITES}/crystal_item_anim_strip_6.png",
    frame_count=6,
)

ANIMATION_SPINNER: Final[arcade.TextureAnimation] = _load_animation_strip(
    f"{ENEMY_SPRITES}/Spinner_Sprites/spinner_run_attack_anim_all_dir_strip_8.png",
    frame_count=8,
)

ANIMATION_BAT: Final[arcade.TextureAnimation] = _load_animation_strip(
    f"{ENEMY_SPRITES}/Pinkbat_Sprites/pinkbat_idle_left_anim_strip_5.png",
    frame_count=5,
)

ANIMATION_BOOMERANG: Final[arcade.TextureAnimation] = _load_animation_strip(
    "assets/provided/boomerang-sheet.png",
    frame_count=8,
    frame_duration=25,
)

ANIMATION_SLIME: Final[arcade.TextureAnimation] = _load_animation_strip(
    f"{ENEMY_SPRITES}/Pinkslime_Sprites/pinkslime_idle_anim_all_dir_strip_6.png",
    frame_count=6,
)

# ==================================================
# Animations de l'épée
# ==================================================

ANIMATION_SWORD: Final[dict[Direction, arcade.TextureAnimation]] = {
    direction: _load_sword_animation(file_direction)
    for direction, file_direction in DIRECTION_NAMES.items()
}


# ==================================================
# Sons
# ==================================================

SOUND_COIN: Final[arcade.Sound] = arcade.load_sound(
    ":resources:sounds/coin5.wav"
)
