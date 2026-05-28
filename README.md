# Adventure Game

Ce projet est un petit jeu d’aventure réalisé en Python avec la bibliothèque Arcade, dans le cadre du cours CS-121 à l’EPFL.

Au début, le jeu était assez simple : on pouvait juste déplacer le joueur dans une map et ramasser des cristaux. Ensuite, on a ajouté petit à petit plusieurs éléments comme les ennemis, les armes, les interrupteurs, les portails, les trous, les vies et le bouclier.

Le projet nous a aussi beaucoup servi à faire du refactoring, parce que le code devenait vite trop grand si tout restait dans `GameView`.

## Fonctionnalités

Le jeu contient notamment :

- un joueur avec des animations ;
- une caméra qui suit le joueur ;
- des cristaux à ramasser ;
- un système de score ;
- des trous qui peuvent faire perdre une vie ;
- un système de vies ;
- un bouclier temporaire ;
- deux armes : l’épée et le boomerang ;
- plusieurs ennemis : chauves-souris, spinners et slimes ;
- des interrupteurs et des portails ;
- un système de map chargé depuis un fichier ;
- un système de collisions ;
- un navmesh pour le déplacement des slimes.

## Comment jouer

Les contrôles sont :

- flèches du clavier : déplacer le joueur ;
- `D` : utiliser l’arme active ;
- `R` : changer d’arme ;
- `ESC` : recommencer la partie.

## Lancer le jeu

Pour installer les dépendances :

uv sync

Pour lancer le jeu :

uv run python main.py

## Organisation du projet

On a essayé de séparer le code en plusieurs fichiers pour éviter que `GameView` devienne trop long.

Les fichiers principaux sont :

- `game_view.py` : lance le jeu et relie les grands systèmes ;
- `player.py` : gère le joueur ;
- `weapon_system.py` : gère l’épée et le boomerang ;
- `enemy_system.py` : gère les ennemis ;
- `collision_handler.py` : gère les collisions ;
- `world_renderer.py` : s’occupe de l’affichage ;
- `map.py` : charge et vérifie la map ;
- `navmesh.py` : sert pour les chemins des slimes ;
- `textures.py` : charge les images et animations.

## Maps

Les maps sont écrites avec une partie configuration et une grille de caractères.

Quelques symboles utilisés :

- `P` : joueur ;
- `x` : buisson / obstacle ;
- `*` : cristal ;
- `O` : trou ;
- `A` : bouclier ;
- `m` : slime ;
- `v` : chauve-souris ;
- `s` ou `S` : spinner ;
- `^` : interrupteur ;
- `|` : portail.

## Ce qu’on a ajouté

On a ajouté deux extensions principales :

1. un système de vies ;
2. un système de bouclier.

Le joueur peut perdre des vies quand il touche un ennemi ou tombe dans un trou. Après un dégât, il devient invincible pendant un petit moment pour éviter de perdre toutes ses vies directement.

Le bouclier protège le joueur pendant un certain temps. Si le joueur prend un dégât avec le bouclier actif, le bouclier absorbe le dégât.

## À propos des ennemis

Les ennemis ne fonctionnent pas tous pareil.

Les chauves-souris bougent dans une zone et changent un peu de direction.
Les spinners se déplacent en ligne droite et font demi-tour.
Les slimes sont plus compliqués, car ils utilisent un navmesh pour trouver un chemin vers le joueur quand ils le voient.

Cette partie était une des plus difficiles du projet, surtout pour faire fonctionner le pathfinding sans trop ralentir le jeu.

## Refactoring

Au début, beaucoup de choses étaient dans `GameView`. Après, on s’est rendu compte que ça devenait trop dur à comprendre et à modifier.

On a donc séparé le code en plusieurs systèmes :

- un système pour les armes ;
- un système pour les ennemis ;
- une classe pour les collisions ;
- une classe pour l’affichage.

Ce n’est pas parfait, mais ça rend le projet beaucoup plus lisible qu’au début.

## Remarques

Le projet n’est pas forcément parfait. Certaines parties pourraient encore être améliorées, surtout l’organisation de quelques fichiers et l’équilibrage du jeu.

Mais le jeu est jouable, les principales fonctionnalités marchent, et on a surtout essayé de montrer qu’on comprenait comment structurer un projet plus grand avec des classes, des sprites, des collisions et plusieurs systèmes qui interagissent.