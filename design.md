# DESIGN.md

## Vue générale

Notre projet est un jeu d’aventure 2D développé en Python avec la bibliothèque Arcade. Le joueur se déplace sur une carte chargée depuis un fichier texte, collecte des cristaux, évite des dangers, combat des ennemis avec plusieurs armes et interagit avec des interrupteurs qui ouvrent ou ferment des portails.

Nous avons refactorisé le projet pour éviter que toute la logique soit concentrée dans `GameView`. La classe `GameView` reste le point d’entrée principal du jeu, mais elle délègue plusieurs responsabilités à des modules spécialisés :

- `Map` représente la carte de manière abstraite.
- `Player` gère le joueur, ses déplacements, ses vies et son bouclier.
- `WeaponSystem` gère les armes.
- `EnemySystem` relie les ennemis logiques à leurs sprites.
- `CollisionHandler` centralise les collisions.
- `WorldRenderer` centralise l’affichage.
- `navmesh.py` gère le graphe utilisé par les slimes.
- `switch.py` gère les interrupteurs et les portails.

Ce découpage rend le projet plus lisible, plus testable et plus facile à faire évoluer.

---

## Carte et chargement

La carte est représentée par la classe `Map`. Elle contient la largeur, la hauteur, la position de départ du joueur, les cellules de la grille, ainsi que les configurations des switches et des gates.

Les cellules sont représentées par l’énumération `GridCell`. Le fichier de map utilise des caractères comme `x`, `*`, `O`, `s`, `S`, `v`, `m`, `^`, `|`, mais ces caractères sont convertis une seule fois vers des valeurs de `GridCell`.

Cela permet au reste du programme de ne pas dépendre directement du format textuel de la map. Par exemple, `GameView` ne teste pas si un caractère vaut `"x"` : elle utilise `GridCell.BUSH`.

Le chargement est fait par `map_from_string` et `map_from_file`. En cas d’erreur de format, une exception `InvalidMapFileException` est levée. Dans `main.py`, cette exception est attrapée pour afficher un message clair à l’utilisateur au lieu d’une traceback.

---

## Conditions logiques des portails

Les portails peuvent être ouverts ou fermés selon des conditions logiques.

Nous représentons ces conditions par plusieurs classes :

- `SwitchIsOn`
- `NotCondition`
- `AndCondition`
- `OrCondition`

Toutes ces classes possèdent une méthode `evaluate`, qui reçoit l’état des switches et renvoie un booléen.

Ce choix permet de représenter naturellement des formules récursives comme :

```yaml
open_if:
  and:
    - switch_is_on: first
    - not:
      - switch_is_on: second