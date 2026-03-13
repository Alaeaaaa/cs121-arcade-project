# Design du projet

## Description générale

Notre projet est un petit jeu 2D réalisé avec la bibliothèque Arcade.

Le joueur peut se déplacer dans un monde composé d’herbe et d’obstacles.
Il peut aussi collecter des cristaux qui disparaissent lorsqu’il les touche.

Le programme est séparé en plusieurs fichiers pour organiser le code.

---

## main.py

Ce fichier sert simplement à lancer le jeu.

Il crée la fenêtre du jeu et crée un objet GameView.
Ensuite il démarre le jeu avec arcade.run().

---

## gameview.py

Ce fichier contient la classe principale du jeu : GameView.

Cette classe est responsable de presque tout ce qui se passe dans le jeu :

- créer le monde
- créer le joueur
- gérer les déplacements
- gérer les collisions
- mettre à jour le jeu
- dessiner les objets à l’écran

Dans cette classe on crée plusieurs listes de sprites :

- player_list : contient le joueur
- grounds : contient l’herbe
- walls : contient les buissons
- crystals : contient les cristaux

On utilise aussi un PhysicsEngineSimple pour gérer les collisions entre le joueur et les murs.

La caméra permet d’afficher seulement une partie du monde et de suivre le joueur.

---

## textures.py

Ce fichier sert à charger toutes les textures et animations.

On charge les images une seule fois pour pouvoir les utiliser ensuite dans le jeu.

On y trouve par exemple :

- la texture de l’herbe
- la texture des buissons
- l’animation du joueur
- l’animation des cristaux

---

## constants.py

Ce fichier contient des constantes utilisées dans le jeu.

Par exemple :

- la taille des tiles
- l’échelle des textures
- la taille maximale de la fenêtre
- la vitesse du joueur

Cela permet d’éviter de répéter les mêmes valeurs dans le code.