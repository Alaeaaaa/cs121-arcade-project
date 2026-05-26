# DESIGN.md

## Vue générale

Notre projet, comme vous le savez sans doute, est un jeu d’aventure 2D développé en Python avec la bibliothèque Arcade. Le joueur se déplace sur une carte chargée depuis un fichier texte, collecte des cristaux, combat des ennemis avec plusieurs armes et interagit avec des interrupteurs qui ouvrent ou ferment des portails.

Nous avons refactorisé le projet (PLUSIEURES fois si je puis dire) pour éviter que toute la logique soit concentrée dans `GameView`. La classe `GameView` reste le point d’entrée principal du jeu, mais elle délègue plusieurs responsabilités à des modules spécialisés :

- `Map` représente la carte de manière abstraite.
- `Player` gère le joueur, ses déplacements, ses vies et son bouclier.
- `WeaponSystem` gère les armes.
- `EnemySystem` relie les ennemis logiques à leurs sprites, et donc centralise la mise à jour des ennemis.
- `CollisionHandler` centralise les collisions.
- `WorldRenderer` centralise l’affichage.
- `navmesh.py` gère le graphe utilisé par les slimes.
- `switch.py` gère les interrupteurs et les portails.

Ce découpage rend le projet plus lisible, plus testable et plus facile à faire évoluer.

---
## Définition du type direction :

Comme `Direction` est supposé représenter les 4 directions cardunales, on a choisi de le représenter par un `Enum`. Cela aide également si jamais on a besoin d'ajouter d'autres directions, on n'aura qu'à les ajouter également dans `Direction` et implémenter leurs commandes associées sans changement de structure globale.

## Définition du joueur :

On a choisi de définir la classe `Player` comme sous-classe de `arcade.TextureAnimationSprite`, simplement parce que c'est un sprite avec une animation, une échelle et une position. Biensur, on ajoute à cela nos attributs définis en particulier pour implémenter nos extensions (vies et bouclier).
Cette classe encapsule donc les données et méthodes propres au joueur, dont sa direction, son déplacement, ses vies, son bouclier... et leur mise à jour par les méthodes correspondantes. On évite de cette façon d'avoir à tout définir dans `GameView`, et le détail d'impplémentation des méthodes reste interne à la classe `Player`, même si on appelle des fonctions de mise à jour dans `GameView`. Par exemple, la question de design qui nous avait été posée à la conception concernait la lecture des touches du clavier, et bienque `GameView` en reste responsable, la logique du mouvemet est déléguée à `Player` avec `update_movement()` en lui passant des booléens selon la direction du mouvement. Cette implémenation permet en plus de mieux structurer nos tests (indépendamment de arcade), de gérer des cas comme "deux touches opposées en même temps"; pour plus de détails, voir le corps de la méthode.

## Gestion des armes :

Au début, nous avions conçu une classe `Boomerang` héritant directement de `arcade.TextureAnimationSprite`, de même pour l'épée, on avait similairement défini une classe `Sword`. Ce n'est que bien plus tard, après plusieurs refactorisations qu'on on en est arrivé au format actuel : `Weapon` et `WeaponSystem`.
`Weapon` est une classe abstraite commune aux deux armes, elle hérite de `arcade.TextureAnimationSprite`, donnant donc aux armes une animation, position, et échelle, en plus de l'attribut supplémentaire `direction`, responsable comme son nom l'indique, de la direction des armes. La classe définit donc une interface commune avec des méthodes abstraites: `is_active` et `deactivate`, garantissant ainsi la bonne coordination entres les armes en fonction de leurs états respectifs, et ce malgré leur différences de comportements. Viennent ensuite les classes `Boomerang` et `Sword` héritant toutes deux de `Weapon` mais implémentant leur propre logique. En discutant tous deux, on s'est dit qu'on aurait pu mieux concevoir ces deux classes pour mieux implémenter la logique des deux armes, mais faute de temps, on laisse `WeaponSystem` gérer tout ça (nous parlons des méthodes comme `_update_sword`...). Avant de passer à `WeaponSystem`, on regarde d'abord comment on a représenté les états des armes, `BoomerangState` est un Enum pour les 3 états, et dans le même esprit `SwordState` représente les deux états du sword. On aurait pu utiliser un booléen à la place, mais `SwordState` en tant que tel donne une meilleure compréhension.
Enfin, la classe `WeaponSystem` centralise toute la gestion des armes, elle sert d'intermédiaire entre `GameView` et les armes, de cette façon, `GameView` n'a pas besoin de connaître les détails internes de l'épée et du boomerang, elle appelle simplement les méthodes appropriées pour décider quelle arme utiliser, met à jour son animation, gère ses collisions et synchronise sa position avec le joueur.

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

Ce choix permet de représenter les conditions sous forme d'arbre logique, et l'évaluation se fat donc par recursivité : chaque condition demande l'évaluation de ses sous-conditions avant d'appliquer son propre opérateur logique (not, and, or).
Ce choix nous a paru très censé (esprit du cours : ADT), sans oublier qu'on peut tester les conditions de cette manière indépendamment d'arcade, car ne dépendant que de dict[str,bool].
