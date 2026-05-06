from typing import Final
import arcade

from direction import Direction


# Taille d'une image dans la plupart des spritesheets.
ORIG_TILE_SIZE: Final[tuple[int, int]] = (16, 16)

# Chemins de base pour éviter de répéter les longs chemins.
ASSET_ROOT: Final[str] = "assets/Top_Down_Adventure_Pack_v.1.0"
CHAR_SPRITES: Final[str] = f"{ASSET_ROOT}/Char_Sprites"
ENEMY_SPRITES: Final[str] = f"{ASSET_ROOT}/Enemies_Sprites"
ITEM_SPRITES: Final[str] = f"{ASSET_ROOT}/Props_Items_(animated)"


def _load_grid(
    file: str,
    columns: int,
    rows: int,
    tile_size: tuple[int, int] = ORIG_TILE_SIZE,
) -> list[arcade.Texture]:
    # Charge une grande image puis la découpe en petites textures.
    spritesheet = arcade.load_spritesheet(file)
    return spritesheet.get_texture_grid(tile_size, columns, columns * rows)


def _load_animation_strip(
    file: str,
    frame_count: int,
    frame_duration: int = 100,
    tile_size: tuple[int, int] = ORIG_TILE_SIZE,
) -> arcade.TextureAnimation:
    # Une animation strip est une ligne de frames.
    grid = _load_grid(file, columns=frame_count, rows=1, tile_size=tile_size)

    # Une keyframe = une image + sa durée d'affichage.
    keyframes = [
        arcade.TextureKeyframe(frame, frame_duration)
        for frame in grid
    ]

    return arcade.TextureAnimation(keyframes)


def _load_player_animation(action: str, direction: str) -> arcade.TextureAnimation:
    # Exemple : char_run_down_anim_strip_6.png
    return _load_animation_strip(
        f"{CHAR_SPRITES}/char_{action}_{direction}_anim_strip_6.png",
        frame_count=6,
    )


def _load_sword_animation(direction: str) -> arcade.TextureAnimation:
    # L'attaque utilise des frames 48x48 car elles incluent joueur + épée.
    return _load_animation_strip(
        f"{CHAR_SPRITES}/char_attack48_{direction}_anim_strip_6.png",
        frame_count=6,
        frame_duration=50,
        tile_size=(48, 48),
    )


# ---------------------------------------------------------
# Textures fixes
# ---------------------------------------------------------

_overworld_grid = _load_grid(
    f"{ASSET_ROOT}/Overworld_Tileset.png",
    columns=18,
    rows=13,
)

# index = y * columns + x, ici columns = 18.
TEXTURE_GRASS: Final[arcade.Texture] = _overworld_grid[18 * 1 + 6]
TEXTURE_BUSH: Final[arcade.Texture] = _overworld_grid[18 * 3 + 5]
TEXTURE_HOLE: Final[arcade.Texture] = _overworld_grid[18 * 4 + 8]


# ---------------------------------------------------------
# Directions
# ---------------------------------------------------------

# Relie notre Direction au mot utilisé dans les noms des fichiers.
DIRECTION_NAMES: Final[dict[Direction, str]] = {
    Direction.SOUTH: "down",
    Direction.NORTH: "up",
    Direction.WEST: "left",
    Direction.EAST: "right",
}


# ---------------------------------------------------------
# Joueur
# ---------------------------------------------------------

# Factorisation : on génère les animations avec une boucle sur les directions.
PLAYER_IDLE_ANIMATIONS: Final[dict[Direction, arcade.TextureAnimation]] = {
    direction: _load_player_animation("idle", file_direction)
    for direction, file_direction in DIRECTION_NAMES.items()
}

PLAYER_RUN_ANIMATIONS: Final[dict[Direction, arcade.TextureAnimation]] = {
    direction: _load_player_animation("run", file_direction)
    for direction, file_direction in DIRECTION_NAMES.items()
}

# Anciens noms gardés pour ne pas casser le reste du code.
ANIMATION_PLAYER_IDLE_DOWN: Final[arcade.TextureAnimation] = PLAYER_IDLE_ANIMATIONS[Direction.SOUTH]
ANIMATION_PLAYER_IDLE_UP: Final[arcade.TextureAnimation] = PLAYER_IDLE_ANIMATIONS[Direction.NORTH]
ANIMATION_PLAYER_IDLE_LEFT: Final[arcade.TextureAnimation] = PLAYER_IDLE_ANIMATIONS[Direction.WEST]
ANIMATION_PLAYER_IDLE_RIGHT: Final[arcade.TextureAnimation] = PLAYER_IDLE_ANIMATIONS[Direction.EAST]

ANIMATION_PLAYER_RUN_DOWN: Final[arcade.TextureAnimation] = PLAYER_RUN_ANIMATIONS[Direction.SOUTH]
ANIMATION_PLAYER_RUN_UP: Final[arcade.TextureAnimation] = PLAYER_RUN_ANIMATIONS[Direction.NORTH]
ANIMATION_PLAYER_RUN_LEFT: Final[arcade.TextureAnimation] = PLAYER_RUN_ANIMATIONS[Direction.WEST]
ANIMATION_PLAYER_RUN_RIGHT: Final[arcade.TextureAnimation] = PLAYER_RUN_ANIMATIONS[Direction.EAST]


# ---------------------------------------------------------
# Objets et ennemis
# ---------------------------------------------------------

ANIMATION_CRYSTAL: Final[arcade.TextureAnimation] = _load_animation_strip(
    f"{ITEM_SPRITES}/crystal_item_anim_strip_6.png",
    frame_count=6,
)

ANIMATION_SPINNER: Final[arcade.TextureAnimation] = _load_animation_strip(
    f"{ENEMY_SPRITES}/Spinner_Sprites/spinner_run_attack_anim_all_dir_strip_8.png",
    frame_count=3,
)

ANIMATION_BAT: Final[arcade.TextureAnimation] = _load_animation_strip(
    f"{ENEMY_SPRITES}/Pinkbat_Sprites/pinkbat_idle_left_anim_strip_5.png",
    frame_count=5,
)


# ---------------------------------------------------------
# Boomerang
# ---------------------------------------------------------

ANIMATION_BOOMERANG: Final[arcade.TextureAnimation] = _load_animation_strip(
    "assets/provided/boomerang-sheet.png",
    frame_count=8,
    frame_duration=25,  # Animation plus rapide.
)


# ---------------------------------------------------------
# Épée
# ---------------------------------------------------------

ANIMATION_SWORD: Final[dict[Direction, arcade.TextureAnimation]] = {
    direction: _load_sword_animation(file_direction)
    for direction, file_direction in DIRECTION_NAMES.items()
}


# ---------------------------------------------------------
# Son
# ---------------------------------------------------------

SOUND_COIN: Final[arcade.Sound] = arcade.load_sound(":resources:sounds/coin5.wav")