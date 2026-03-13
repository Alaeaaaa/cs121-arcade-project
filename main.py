import sys
import arcade

from constants import *
from gameview import GameView
from map import map_from_file, InvalidMapFileException


def main() -> None:
    # Create the (unique) Window, setup our GameView, and launch
    window = arcade.Window(MAX_WINDOW_WIDTH, MAX_WINDOW_HEIGHT, WINDOW_TITLE)

    try:
        if len(sys.argv) > 1:
            path = sys.argv[1]
        else:
            path = "maps/map1.txt"

        game_map = map_from_file(path)

    except InvalidMapFileException as e:
        print(f"Erreur lors du chargement de la map : {e}")
        return

    game_view = GameView(game_map)
    window.show_view(game_view)
    arcade.run()


if __name__ == "__main__":
    main()