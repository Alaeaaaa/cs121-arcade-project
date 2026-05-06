import sys
import arcade

from constants import *
from gameview import GameView
from map import map_from_file, InvalidMapFileException


def main() -> None:
    # Crée la fenetre 
    window = arcade.Window(MAX_WINDOW_WIDTH, MAX_WINDOW_HEIGHT, WINDOW_TITLE) 

    #charge la map: Si l’utilisateur a donné un argument après le nom du fichier Python, alors on utilise cet argument comme chemin de map.
    #Sinon, on utilise la map par défaut : maps/map1.txt
    
    try:
        if len(sys.argv) > 1:   #sys.argv ca veut dire ce qu'ecrit l'utilisateur dans le terminal
            path = sys.argv[1]
        else:
            path = "maps/map1.txt"

        game_map = map_from_file(path)

    except InvalidMapFileException as e:
        print(f"Erreur lors du chargement de la map : {e}")
        return

    #creer la fenetre et lancer le jeux 
    game_view = GameView(game_map)
    window.show_view(game_view)
    arcade.run()


if __name__ == "__main__":
    main()