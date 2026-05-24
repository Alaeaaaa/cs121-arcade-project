WINDOW_TITLE = "Adventure"
#Title of the main window.

SCALE = 2.0
#The global scale for all textures.

TILE_SIZE = 32
#After scaling, the size of a tile.

MAX_WINDOW_WIDTH = 14 * TILE_SIZE
MAX_WINDOW_HEIGHT = 14 * TILE_SIZE

PLAYER_MOVEMENT_SPEED = 4
#Speed of the player, in pixels per frame.
#pour affiner la camera
LEFT_MARGIN = 200
RIGHT_MARGIN = 200
BOTTOM_MARGIN = 150
TOP_MARGIN = 150

SPINNER_MOVEMENT_SPEED = 3

# =========================
# Extension : vies du joueur
# =========================

# Nombre maximal de vies du joueur.
# Au début de la partie, le joueur aura ce nombre de cœurs.
PLAYER_MAX_HEALTH = 3

# Durée d'invincibilité après un dégât, en secondes.
# Cela évite que le joueur perde plusieurs vies instantanément
# s'il reste en contact avec un ennemi ou un trou.
PLAYER_INVINCIBILITY_DURATION = 1.0

# =========================
# Extension : bouclier
# =========================

# Durée pendant laquelle le bouclier protège le joueur.
SHIELD_DURATION = 5.0

# Taille visuelle du bonus bouclier dans le monde.
SHIELD_SCALE = 0.5


# =========================
# Armes
# =========================

# Vitesse du boomerang en pixels par frame.
BOOMERANG_SPEED = 8

# Distance maximale du boomerang, en nombre de cases.
BOOMERANG_MAX_DISTANCE_IN_TILES = 8

# Distance à partir de laquelle le boomerang est récupéré par le joueur.
BOOMERANG_CATCH_DISTANCE = 8

# Durée de l'attaque à l'épée, en secondes.
SWORD_ATTACK_DURATION = 0.3

BOOMERANG_SCALE = 2


# =========================
# Collisions dangereuses
# =========================

# Distance à partir de laquelle le joueur tombe dans un trou.
HOLE_DEATH_DISTANCE = 16


# =========================
# Switches
# =========================

# Les textures Arcade des switches sont grandes, donc on les réduit.
SWITCH_SCALE = 0.25

# ==================================================
# Constantes des slimes
# ==================================================
SLIME_SPEED = 1.0
PATROL_RADIUS = 3
DESTINATION_EPSILON = 4.0
MAX_VIEW_DISTANCE = 12 * TILE_SIZE
DIRECT_CHASE_DISTANCE = 2 * TILE_SIZE
RECOMPUTE_PATH_DISTANCE = TILE_SIZE // 2

# ==================================================
# Constantes des chauves-souris
# ==================================================

BAT_SPEED = 2.0
BAT_WIDTH = 6
BAT_HEIGHT = 4