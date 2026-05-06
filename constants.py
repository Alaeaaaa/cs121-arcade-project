WINDOW_TITLE = "Adventure"
"""Title of the main window."""

SCALE = 2.0
"""The global scale for all textures."""

TILE_SIZE = 32
"""After scaling, the size of a tile."""

MAX_WINDOW_WIDTH = 14 * TILE_SIZE
MAX_WINDOW_HEIGHT = 14 * TILE_SIZE

PLAYER_MOVEMENT_SPEED = 4
"""Speed of the player, in pixels per frame."""
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
