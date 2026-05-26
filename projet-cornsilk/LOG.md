
### `LOG.md`

```md
# LOG.md

## Semaine 2 : Découverte d’Arcade

Nous avons commencé par créer la structure de base du projet avec `main.py`, `gameview.py` et `constants.py`.

Nous avons installé Arcade avec `uv`, puis créé une fenêtre de jeu. Ensuite, nous avons ajouté les premiers sprites : le joueur, l’herbe et les buissons.

Nous avons appris à utiliser les `SpriteList`, car elles permettent de dessiner plusieurs sprites plus efficacement qu’en appelant `draw_sprite` à chaque fois.

Nous avons aussi ajouté le déplacement du joueur au clavier, puis un moteur physique simple avec `arcade.PhysicsEngineSimple` pour empêcher le joueur de traverser les buissons.

Nous avons ensuite ajouté une caméra qui suit le joueur, des animations pour le joueur et des cristaux collectables.

Difficultés rencontrées :
- comprendre le système de coordonnées Arcade ;
- comprendre la différence entre une texture, un sprite et une SpriteList ;
- comprendre pourquoi il fallait utiliser une caméra ;
- gérer les collisions correctement.

## Semaine 3 : Maps et spinners

Nous avons remplacé la map codée directement dans `GameView` par une vraie structure `Map`.

Nous avons créé une énumération `GridCell` pour représenter les différents types de cellules : herbe, buisson, cristal, spinner, trou, etc.

Nous avons ensuite implémenté le chargement d’une map depuis un fichier texte. La fonction `map_from_string` lit la configuration, vérifie la taille de la map, cherche la position du joueur et transforme les caractères de la grille en `GridCell`.

Nous avons aussi créé une exception personnalisée `InvalidMapFileException` pour gérer les erreurs de format de manière propre.

Ensuite, nous avons ajouté les spinners. Un spinner horizontal ou vertical est créé depuis la map. Ses limites de déplacement sont calculées une seule fois au lancement du jeu.

Difficultés rencontrées :
- gérer les coordonnées dans la grille ;
- vérifier qu’il y a exactement un joueur ;
- produire des messages d’erreur clairs ;
- calculer les limites des spinners sans dépendre d’Arcade.

## Semaine 4 : Trous, joueur et boomerang

Nous avons créé une classe `Player` séparée. Avant cela, beaucoup de logique du joueur était directement dans `GameView`.

La classe `Player` gère maintenant la direction du joueur, son mouvement et ses animations.

Nous avons ajouté l’énumération `Direction`, qui permet de représenter les quatre directions cardinales. Elle est utilisée par le joueur, l’épée et le boomerang.

Nous avons ajouté les trous avec le caractère `O`. Le joueur tombe s’il est trop proche du centre d’un trou.

Nous avons ensuite ajouté le score et une interface fixe à l’écran grâce à une deuxième caméra.

Enfin, nous avons ajouté le boomerang. Il possède trois états :
- inactif ;
- lancement ;
- retour.

Le boomerang part dans la direction du joueur, revient après une certaine distance ou lorsqu’il touche un obstacle, et peut tuer des ennemis.

Difficultés rencontrées :
- gérer les états du boomerang ;
- faire revenir le boomerang vers le joueur ;
- éviter que la logique du boomerang rende `GameView` trop grande ;
- gérer proprement les collisions avec les ennemis.

## Semaine 5 : Épée et chauves-souris

Nous avons ajouté une deuxième arme : l’épée.

Le joueur peut changer d’arme avec la touche `R`, puis utiliser l’arme active avec la touche `D`.

L’épée possède une animation dépendant de la direction du joueur. Elle reste active pendant une courte durée, peut tuer des ennemis et peut aussi collecter des cristaux.

Nous avons ensuite ajouté les chauves-souris. Elles sont placées dans la map avec le caractère `v`.

Chaque chauve-souris possède une zone de mouvement autour de sa position de départ. Elle se déplace avec une vitesse de norme constante, puis rebondit lorsqu’elle atteint les limites de sa zone.

Difficultés rencontrées :
- gérer deux armes sans dupliquer trop de code ;
- éviter que le joueur puisse lancer plusieurs attaques en même temps ;
- synchroniser l’animation de l’épée avec sa durée d’activité ;
- créer un mouvement aléatoire mais contrôlé pour les chauves-souris.

## Semaine 6 : Refactoring

On n'a pas eu le temps de faire de refactoring significatif durant cette semaine.

## Semaine 7 : slimes, navmesh

Nous avons ajouté les slimes, qui sont des ennemis plus intelligents.

Contrairement aux spinners et aux chauves-souris, les slimes utilisent un navmesh pour trouver un chemin vers leur destination.

Nous avons représenté le navmesh avec NetworkX. Les nœuds sont des tuples `(x, y)` correspondant aux cellules accessibles de la map. Les buissons, trous et portails sont des obstacles pour les slimes.

Nous avons connecté les nœuds voisins avec des arêtes pondérées par la distance euclidienne. Cela permet d’utiliser Dijkstra pour calculer un plus court chemin.

Les slimes patrouillent dans une zone autour de leur position de départ. S’ils voient le joueur, ils changent leur destination vers sa position.

## semaine 8 :switches et gates

Nous avons ajouté les switches et gates.

Les switches peuvent être activés par une arme. Les gates s’ouvrent ou se ferment selon des conditions logiques écrites dans la configuration YAML de la map.

Nous avons représenté ces conditions avec des classes récursives :
- `SwitchIsOn`
- `NotCondition`
- `AndCondition`
- `OrCondition`

Difficultés rencontrées :
- comprendre comment utiliser NetworkX ;
- relier les positions en pixels aux nœuds du graphe ;
- éviter de recalculer le chemin du slime à chaque frame ;
- parser les conditions YAML des portails ;
- éviter qu’un switch soit activé plusieurs fois par seconde pendant une collision.

## semaine 9 : Refactoring du navmesh

Nous avons raffiné le navmesh pour tenir compte de la finesse en modifiant toutes les fonctions responsables de la création des noeuds et du navmesh en général.
Pleins de difficultés ont été recontrées, mais elles sont déja detaillees dans le fichier du design

## semaine 10
nous n'avons pas eu le temps de bosser sur le projet cette semaine.

## semaine 11 et 12 : refactoring de presque tout
Nous avons refactorisé le projet pour mieux séparer les responsabilités.

Nous avons introduit `WeaponSystem` pour gérer les armes. Cela permet de ne plus mettre toute la logique du boomerang et de l’épée dans `GameView`.

Nous avons aussi créé `EnemySystem`, qui relie les objets logiques des ennemis à leurs sprites. Cela permet de supprimer un ennemi logique et son sprite en même temps.

Nous avons créé `CollisionHandler` pour centraliser les collisions du joueur et des armes.

Nous avons créé `WorldRenderer` pour regrouper l’affichage du monde et de l’interface.

Ce refactoring était absolument nécessaire pour améliorer l'architecture générale de notre projet.

Difficultés rencontrées :
- décider quelles responsabilités sortir de `GameView` ;
- garder la synchronisation entre objets logiques et sprites ;
- éviter les imports circulaires;
- garder le projet compréhensible malgré plus de fichiers

## semaine 13 :

Nous avons ajouté deux extensions personnelles : un système de vies et un système de bouclier.

Pour le système de vies, le joueur possède plusieurs cœurs. Lorsqu’il prend un dégât, il perd une vie et revient au début de la map. Après un dégât, il devient invincible pendant un court moment.

Pour le système de bouclier, nous avons ajouté un nouvel objet dans la map avec le caractère `A`. Quand le joueur le ramasse, il obtient un bouclier temporaire. Si le joueur prend un dégât pendant que le bouclier est actif, le bouclier absorbe le coup.

Nous avons aussi ajouté l’affichage des vies et du bouclier dans l’interface, et on a encore plus tout refactorisé.

Difficultés rencontrées :
- intégrer les extensions sans casser les collisions existantes ;
- éviter que le joueur perde toutes ses vies instantanément ;
- afficher clairement les informations dans l’interface ;
- garder une architecture propre malgré l’ajout de nouvelles fonctionnalités.

## État actuel du projet:

À l'état actuel du projet (actuel), notre jeu contient :

- un joueur animé ;
- une map chargée depuis un fichier ;
- des cristaux ;
- des trous ;
- un score ;
- deux armes ;
- plusieurs types d’ennemis ;
- des switches ;
- des gates ;
- des slimes avec navmesh ;
- un système de vies ;
- un système de bouclier ;
- une interface utilisateur ;
- des tests pytest pour une partie importante de la logique.

Le projet pourrait encore être amélioré avec plus de tests, une meilleure factorisation de certaines fonctions utilitaires et une classe abstraite plus complète pour les ennemis, mais on l'a dèjà mentionné dans le fichier design
