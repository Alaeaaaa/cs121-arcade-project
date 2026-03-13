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