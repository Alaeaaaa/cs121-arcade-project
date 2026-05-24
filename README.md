# Adventure Game

Petit jeu d'aventure 2D réalisé en Python avec la bibliothèque [Arcade](https://api.arcade.academy/) dans le cadre du cours CS-121 à l'EPFL.

Le joueur explore un monde, collecte des cristaux, évite des ennemis et utilise des armes pour se défendre.

---

## Lancer le jeu

Installer les dépendances :

```bash
uv sync
```

Lancer le jeu avec la map par défaut :

```bash
uv run python main.py
```

Lancer le jeu avec une map personnalisée :

```bash
uv run python main.py maps/map1.txt
```

Lancer les tests :

```bash
uv run pytest
```

---

## Commandes

| Touche | Action |
|---|---|
| ↑ ↓ ← → | Déplacer le joueur |
| D | Utiliser l'arme active |
| R | Changer d'arme (boomerang / épée) |
| ESCAPE | Recommencer la partie |

---

## Fonctionnalités

### Semaine 1 — Bases
- Déplacement du joueur avec animations directionnelles
- Caméra qui suit le joueur
- Collisions avec les obstacles (buissons)
- Collecte de cristaux avec bruitage
- Score affiché en temps réel

### Semaine 2 — Maps et monstres
- Chargement de maps depuis des fichiers texte
- Validation du format avec gestion d'erreurs
- Spinners horizontaux et verticaux

### Semaine 3 — Trous et boomerang
- Orientation du joueur selon la direction de déplacement
- Trous mortels
- Boomerang avec trois états : inactif, lancé, retour

### Semaine 4 — Épée et chauves-souris
- Épée avec animation directionnelle
- Changement d'arme à la volée
- Chauves-souris avec déplacement pseudo-aléatoire dans une zone

### Semaine 5 — Refactoring
- Extraction de `WeaponSystem`, `EnemySystem`, `CollisionHandler`, `WorldRenderer`
- Classe abstraite `Weapon` avec polymorphisme sur `is_active()` et `deactivate()`
- Suppression des doublons (`grid_to_pixels`, `find_cells` dans `utils.py`)

### Semaine 6 — Slimes et interrupteurs
- Slimes avec ligne de vue, navigation mesh (NetworkX + Dijkstra)
- Interrupteurs et portails
- Conditions logiques `and`, `or`, `not`, `switch_is_on` lues depuis YAML

---

## Extensions personnelles

### 1. Système de vies

Le joueur commence avec plusieurs vies affichées sous forme de cœurs (♥).

Quand il touche un ennemi ou tombe dans un trou, il perd une vie et revient à sa position de départ. Après un dégât, il devient temporairement invincible (effet de clignotement). Si toutes les vies sont perdues, la partie recommence.

**Fichiers concernés :** `player.py`, `game_view.py`, `collision_handler.py`, `constants.py`

### 2. Système de bouclier

Des boucliers sont placés sur la carte (caractère `A` dans le fichier de map).

Quand le joueur en ramasse un, il est protégé temporairement contre la prochaine attaque ou le prochain danger — sans perdre de vie. Le temps restant est affiché dans l'interface. Une fois le coup absorbé, le bouclier disparaît.

**Fichiers concernés :** `player.py`, `game_view.py`, `collision_handler.py`, `map.py`, `textures.py`

---

## Format des maps

Les maps sont des fichiers texte avec deux sections séparées par `---`.

La première section est une configuration YAML :

```yaml
width: 20
height: 10
switches:
  - id: s1
    x: 5
    y: 3
    state: off
gates:
  - x: 8
    y: 3
    open_if:
      switch_is_on: s1
```

La deuxième section est la grille de caractères :

| Caractère | Élément |
|---|---|
| ` ` (espace) | Herbe |
| `P` | Position de départ du joueur |
| `x` | Buisson (mur) |
| `*` | Cristal |
| `O` | Trou |
| `s` | Spinner horizontal |
| `S` | Spinner vertical |
| `v` | Chauve-souris |
| `m` | Slime |
| `^` | Interrupteur |
| `\|` | Portail |
| `A` | Bouclier |

---

## Structure du projet

```
.
├── main.py               # Point d'entrée
├── game_view.py          # Vue principale (coordination)
├── player.py             # Joueur (vies, bouclier, invincibilité)
├── map.py                # Chargement et validation des maps
├── weapon_system.py      # Boomerang + épée
├── weapon.py             # Classe abstraite Weapon
├── boomerang.py          # Boomerang
├── sword.py              # Épée
├── enemy_system.py       # Système générique d'ennemis
├── spinner.py            # Spinners
├── bat.py                # Chauves-souris
├── slime.py              # Slimes (IA + navmesh)
├── navmesh.py            # Navigation mesh (Dijkstra)
├── switch.py             # Interrupteurs et portails
├── collision_handler.py  # Toutes les collisions
├── world_renderer.py     # Dessin du monde et de l'UI
├── direction.py          # Enum Direction
├── constants.py          # Constantes globales
├── textures.py           # Chargement des assets
├── utils.py              # Fonctions utilitaires partagées
├── maps/                 # Fichiers de maps
├── assets/               # Sprites et sons
└── tests/                # Tests pytest
```