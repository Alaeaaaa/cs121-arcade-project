# Adventure Game

Ce projet est un petit jeu réalisé avec la bibliothèque Arcade dans le cadre du cours CS-121.

Le joueur peut explorer un monde et collecter des cristaux.

## Comment jouer

Utiliser les flèches du clavier :

- ↑ : monter
- ↓ : descendre
- ← : aller à gauche
- → : aller à droite

Lorsque le joueur touche un cristal, celui-ci disparaît et un son est joué.

## Lancer le jeu

Installer les dépendances :

uv sync

Puis lancer le jeu :

uv run python main.py

## Fonctionnalités

- déplacement du joueur
- collisions avec les obstacles
- caméra qui suit le joueur
- animations
- collecte de cristaux
- bruitage lorsque le cristal est collecté