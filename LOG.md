# Log du projet

## Semaine 1

Nous n’avons pas travaillé sur le projet cette semaine.

---

## Semaine 2

Temps de travail : environ 4 heures

Cette semaine nous avons commencé le projet et découvert la bibliothèque Arcade.

Nous avons :

- créé le projet avec les fichiers `main.py`, `gameview.py` et `constants.py`
- installé la bibliothèque Arcade avec `uv`
- ouvert une première fenêtre avec un fond bleu
- ajouté le joueur avec un sprite
- créé le monde avec de l’herbe et des buissons
- ajouté les déplacements du joueur avec le clavier

**Difficultés**

Au début c’était un peu difficile de comprendre comment fonctionnent les `SpriteList` et comment Arcade dessine les objets à l’écran.

---

## Semaine 3

Nous n’avons pas travaillé sur le projet cette semaine.

---

## Semaine 4

Temps de travail : environ 8 heures

Nous avons continué le projet et ajouté plusieurs nouvelles fonctionnalités au jeu.

Nous avons :

- ajouté le moteur physique pour empêcher le joueur de traverser les buissons
- ajouté une caméra qui suit le joueur
- ajouté les animations du joueur
- ajouté les cristaux à collecter
- ajouté un son lorsque le joueur ramasse un cristal

Nous avons aussi implémenté les **spinners** (petits monstres qui se déplacent en ligne droite).

Pour cela nous avons :

- ajouté les cellules `SPINNER_HORIZONTAL` et `SPINNER_VERTICAL` dans la map
- créé un fichier `spinner.py` pour gérer la logique des spinners
- écrit une fonction qui calcule les limites de déplacement d’un spinner en regardant les obstacles dans la map
- créé une classe `Spinner` pour stocker sa position, sa direction et ses limites
- ajouté les sprites des spinners dans `GameView`
- ajouté leur animation
- implémenté leur déplacement automatique entre leurs limites
- ajouté la collision entre le joueur et un spinner (le jeu recommence si le joueur touche un spinner)

Nous avons ensuite ajouté la fonctionnalité principale de cette semaine : **le boomerang**.

Pour cela nous avons :

- créé un fichier `boomerang.py`
- défini un `Enum` `BoomerangState` pour gérer les trois états du boomerang : `INACTIVE`, `LAUNCHING` et `RETURNING`
- créé une classe `Boomerang` qui hérite de `TextureAnimationSprite`
- ajouté l’animation du boomerang dans `textures.py`
- ajouté le boomerang dans `GameView`
- implémenté le lancement du boomerang lorsque le joueur appuie sur la touche `D`
- fait partir le boomerang dans la direction dans laquelle regarde le joueur
- limité la distance de déplacement du boomerang à 8 cellules
- implémenté le retour du boomerang vers le joueur
- ajouté la collision entre le boomerang et les spinners (le boomerang peut les éliminer)
- fait en sorte que le boomerang traverse les obstacles lors du retour

**Difficultés**

Nous avons eu quelques problèmes avec l’import du son `SOUND_COIN` et avec le comportement de la caméra.

Pour les spinners, la partie la plus difficile était de comprendre comment calculer correctement leurs limites de déplacement uniquement à partir de la map.

Pour le boomerang, la partie la plus difficile était de gérer correctement les différents états (`INACTIVE`, `LAUNCHING`, `RETURNING`) et de faire revenir le boomerang vers le joueur même lorsque celui-ci se déplace.

## semaine 5 :

Temps de travail : environ 2h.

Nous avons ajouté une nouvelle fonctionnalité du joueur : **le sword**

Pour cela, nous avond procédé comme suit:

- création du fichier `sword.py`
- définition d'une nouvelle classe  :
`Enum` `SwordState` pour déterminer si l'épée est effectivement l'arme active : `INACTIVE` et `ACTIVE`
- créé une classe `Sword` qui hérite de `TextureAnimationSprite`
- ajouté l'animation de l'épée à `textures.py`

**Difficultés**

Même avec l'existence de la classe Boomerang, nous avons eu quelques difficultés à construire la classe Sword en prenant en compte tous ses attributs.

Par ailleurs, il était assez compliqué de coder les animations de l'épée de façon "élégante" et de les stocker dans une seule structure : un dictionnaire.

## semaine 6 :

Temps de travail : environ 7 heures.

Cette semaine s'est révélée plus fatstidieuse que prévue car nous avons du terminer la construction de la classe Sword et son implémentation dans Gameview + la création des **chauve-souris**, nous avons donc :

- ajouté l'épée à Gameview
- codé la nouvelle touche `R`pour le changement d'ames
- modifié le code de la touche `D` pour inclure le comportment de l'épée
- ajouté un nouvel attribut :`active_weapon`et de l' `Enum` qui la représente : `ActiveWeapon` pour pouvoir passer du boomerang à l'épée plus facilement.
- ajouté la collision entre l'épée et les crystaux
- ajouté la collision entre l'épée et les spinners

nous avons également ajouté la nouvelle classe de monstres : **les chauves-souris**.
Pour cela, nous avons :

- ajouté les cellules `BAT` dans la map
- ajouté l'animation des chauve-souris dans `textures.py`
- créé le fichier `bat.py`
- ajouté une nouvelle classe `BatBounds` pour déterminer les limites de mvt des chauve-souris
- ajouté une nouvelle classe `Bat` pour représenter les chauve-souris, fortement inspiré de la classe `Spinner`
- ajouté une fonction pour calculer leurs limites de déplacement
- ajouté une fonction pour créer les chauves-souris à partir de leur position sur la map
- ajouté leurs sprites dans `gameview.py`
- impléménté leurs déplacements dans des directions "semi-aléatoires" dans les limites de leur zone d'action
- ajouté leur collisions avec le boomerang, l'épée, et le joueur.

**Difficultés**

L'ajout de l'icône des armes est un aspect assez difficile à aborder, en particulier quand on ignore la majorité des commandes de la caméra d'arcade.

L'ajout des commandes de la touche `R` en tenant compte des deux armes a pris du temps, et la modification de la touche `D` pour inclure les commandes de l'épée également.

La délimitation de la zone d'action des chauves-souris ET SURTOUT la mise à jour de leur direction, EN VEILLANT à ne pas dépasser les limites de la zone est ce qui a pris le plus de temps.

---

## Semaine 7

Temps de travail : environ 8 heures.

Cette semaine, nous avons ajouté une nouvelle classe d’ennemis : **les blobs / slimes**.

L’objectif était de créer des ennemis plus intelligents que les spinners et les chauves-souris. Contrairement aux autres monstres, les slimes ne se déplacent pas simplement en ligne droite ou dans une zone fixe : ils peuvent patrouiller, voir le joueur, puis le poursuivre en évitant les obstacles.

Nous avons commencé par modifier la map pour ajouter une nouvelle cellule :

- ajout de la cellule `SLIME` dans `GridCell`
- utilisation du caractère `m` dans les fichiers de map pour représenter un slime
- création d’un fichier `slime.py`
- création d’une classe `Slime` pour stocker :
  - sa position de départ
  - sa position actuelle
  - sa destination
  - ses destinations possibles de patrouille
  - son chemin courant
  - l’indice du point du chemin qu’il suit actuellement

Nous avons ensuite ajouté une logique de patrouille.

Pour cela, nous avons :

- défini un rayon de patrouille autour de la position initiale du slime
- écrit une fonction qui cherche les cases accessibles autour du slime
- empêché les slimes de choisir comme destination les buissons, les trous et les portails
- choisi aléatoirement une destination parmi les cases valides
- fait avancer le slime vers sa destination
- choisi une nouvelle destination quand il atteint la précédente

Ensuite, nous avons ajouté la ligne de vue du slime vers le joueur.

Pour cela, nous avons :

- ajouté une distance maximale de vision
- utilisé `arcade.has_line_of_sight` pour vérifier si un obstacle bloque la vue
- fait en sorte que les buissons et les portails fermés bloquent la vue
- gardé les trous comme obstacles pour le déplacement, mais pas comme obstacles pour la ligne de vue
- fait poursuivre le joueur par le slime uniquement lorsqu’il est visible

Nous avons ensuite ajouté le pathfinding avec un navmesh.

Pour cela, nous avons :

- installé `networkx` avec `uv`
- créé un fichier `navmesh.py`
- représenté les cases accessibles par des nœuds dans un graphe
- ajouté des arêtes entre les cases voisines
- utilisé un poids basé sur la distance euclidienne entre deux cases
- utilisé l’algorithme de plus court chemin de NetworkX pour calculer le chemin du slime
- transformé les positions de grille en positions en pixels
- fait suivre au slime les points du chemin calculé

Nous avons aussi optimisé le comportement du slime.

Pour cela, nous avons :

- évité de recalculer le chemin à chaque frame
- recalculé le chemin seulement lorsque le joueur s’est suffisamment déplacé
- ajouté une poursuite directe lorsque le joueur est très proche du slime
- ajouté une petite tolérance pour considérer que le slime a atteint sa destination

Enfin, nous avons intégré les slimes dans `GameView`.

Nous avons :

- ajouté une liste de slimes dans `GameView`
- créé les sprites des slimes
- ajouté leur dessin à l’écran
- mis à jour leur position à chaque frame
- ajouté la collision entre le joueur et un slime
- ajouté la collision entre les slimes et les armes
- fait recommencer le jeu si le joueur touche un slime

**Difficultés**

La partie la plus difficile était de comprendre comment représenter la map sous forme de graphe. Au début, nous avions seulement des positions en pixels et des cases dans la grille, mais il fallait faire le lien entre les deux.

Le deuxième problème était d’éviter que le slime recalcule son chemin à chaque frame. Cela rendait le comportement moins propre et pouvait ralentir le jeu. Nous avons donc ajouté une condition pour recalculer le chemin seulement quand la destination change vraiment.

Nous avons aussi dû faire attention à la ligne de vue : les trous doivent bloquer le mouvement des slimes, mais ils ne doivent pas bloquer leur vision. À l’inverse, les buissons et les portails fermés bloquent la vision.

---

## Semaine 8

Temps de travail : environ 7 heures.

Cette semaine, nous avons ajouté le système des **interrupteurs et des portails**.

L’objectif était de permettre à la map de contenir des éléments interactifs : le joueur peut activer des interrupteurs avec ses armes, et ces interrupteurs ouvrent ou ferment des portails selon des conditions logiques.

Nous avons commencé par modifier le format des maps.

Avant, la map contenait surtout une grille ASCII. Maintenant, nous avons ajouté une partie de configuration en YAML avant la grille.

Cette configuration permet de définir :

- la largeur de la map
- la hauteur de la map
- la liste des interrupteurs
- la liste des portails
- les conditions d’ouverture des portails

Nous avons ajouté deux nouveaux caractères dans la map :

- `^` pour représenter un interrupteur
- `|` pour représenter un portail

Dans `map.py`, nous avons donc :

- ajouté `SWITCH` dans `GridCell`
- ajouté `GATE` dans `GridCell`
- ajouté la lecture du YAML avec `pyyaml`
- installé `pyyaml` avec `uv`
- créé une classe `SwitchConfig` pour stocker la configuration d’un interrupteur
- créé une classe `GateConfig` pour stocker la configuration d’un portail
- vérifié que chaque interrupteur déclaré dans le YAML correspond bien à un `^` dans la grille
- vérifié que chaque portail déclaré dans le YAML correspond bien à un `|` dans la grille
- vérifié que les identifiants des interrupteurs sont uniques
- ajouté des messages d’erreur plus précis en cas de problème dans la map

Ensuite, nous avons ajouté les conditions logiques des portails.

Nous avons créé plusieurs classes :

- `GateCondition`
- `SwitchIsOn`
- `NotCondition`
- `AndCondition`
- `OrCondition`

Ces classes permettent de représenter des formules logiques récursives.

Par exemple, un portail peut être ouvert si :

```yaml
open_if:
  switch_is_on: first
