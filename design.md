# DESIGN.md — Réponses aux questions de design

## 1. Comment définissez-vous le type `Direction`, et pourquoi ?

Nous définissons le type `Direction` comme une énumération (`Enum`) dans un fichier séparé `direction.py`.

```python
from enum import Enum, auto

class Direction(Enum):
    NORTH = auto()
    SOUTH = auto()
    WEST = auto()
    EAST = auto()
```

Nous avons choisi une `Enum` parce qu’une direction ne peut prendre qu’un nombre fini de valeurs possibles. Dans notre jeu, le joueur, l’épée et le boomerang peuvent seulement être orientés vers le nord, le sud, l’ouest ou l’est.

Ce choix est plus propre que d’utiliser des chaînes de caractères comme `"north"` ou `"left"` partout dans le code. Avec des chaînes de caractères, une simple faute de frappe peut créer un bug difficile à repérer, par exemple `"rigth"` au lieu de `"right"`.

Avec une `Enum`, le code devient plus clair :

```python
self.direction = Direction.SOUTH
```

au lieu de :

```python
self.direction = "south"
```

Cela rend le code plus lisible, plus sûr et plus facile à maintenir. Cela aide aussi les outils de typage et l’autocomplétion.

Nous utilisons donc `Direction` pour représenter une information métier précise : l’orientation d’un objet dans le jeu.

---

## 2. Ces méthodes reçoivent-elles n’importe quel `symbol: int`, comme dans `on_key_press`, ou reçoivent-elles un type de données plus spécifique ? Pourquoi ce choix ?

Les méthodes `on_key_press` et `on_key_release` reçoivent bien un `symbol: int`, parce que c’est l’interface imposée par Arcade. Arcade représente les touches du clavier par des constantes entières, par exemple `arcade.key.RIGHT`, `arcade.key.LEFT`, `arcade.key.D`, etc.

Dans `GameView`, on a donc ce type de méthode :

```python
def on_key_press(self, symbol: int, modifiers: int) -> None:
    if symbol == arcade.key.RIGHT:
        self.right_pressed = True
```

Cependant, nous ne faisons pas circuler ces `symbol: int` dans tout le reste du projet. Nous les transformons rapidement en informations plus spécifiques.

Par exemple, pour le joueur, `GameView` garde des booléens :

```python
self.right_pressed
self.left_pressed
self.up_pressed
self.down_pressed
```

Puis il transmet ces booléens au joueur :

```python
self.player.update_movement(
    self.right_pressed,
    self.left_pressed,
    self.up_pressed,
    self.down_pressed,
)
```

Cela veut dire que `Player` ne reçoit pas directement un `symbol: int`. Il reçoit une information plus claire : quelles directions sont actuellement appuyées.

Ce choix est important pour séparer les responsabilités :

- `GameView` gère les événements clavier Arcade.
- `Player` gère le mouvement du joueur.
- `Player` ne dépend pas directement de `arcade.key`.
- Le code devient plus facile à modifier.

Par exemple, si on veut changer les touches du clavier, on modifie seulement `GameView`. On n’a pas besoin de modifier `player.py`.

C’est donc un choix de design volontaire : les événements bas niveau d’Arcade restent dans `GameView`, et les autres classes reçoivent des données plus adaptées à leur rôle.

---

## 3. Avez-vous défini une classe séparée pour gérer le boomerang, et si oui, étend-elle une classe de sprite ? Pourquoi ?

Oui, nous avons défini une classe séparée `Boomerang` dans le fichier `boomerang.py`.

```python
class Boomerang(arcade.TextureAnimationSprite):
    def __init__(self):
        super().__init__(animation=ANIMATION_BOOMERANG, scale=BOOMERANG_SCALE)
        self.state = BoomerangState.INACTIVE
        self.direction = Direction.SOUTH
        self.distance_travelled = 0
```

Cette classe étend `arcade.TextureAnimationSprite`, car le boomerang est un objet graphique animé. Il doit être affiché à l’écran, avoir une position, une animation, une hitbox et participer aux collisions.

En héritant de `TextureAnimationSprite`, le boomerang récupère directement plusieurs fonctionnalités d’Arcade :

- une position en pixels ;
- une texture ou animation ;
- la possibilité d’être dessiné ;
- une hitbox ;
- la compatibilité avec les fonctions de collision ;
- les propriétés comme `center_x`, `center_y`, `position`, etc.

Nous avons choisi une classe séparée parce que le boomerang a une logique propre :

- il peut être inactif ;
- il peut être lancé ;
- il peut revenir vers le joueur ;
- il possède une direction ;
- il garde la distance qu’il a parcourue.

Mettre tous ces attributs directement dans `GameView` rendrait le code moins clair. La classe `Boomerang` permet de regrouper les données propres au boomerang dans un seul endroit.

La logique détaillée du mouvement du boomerang reste dans `GameView`, car elle dépend fortement des collisions avec les murs, les ennemis, les interrupteurs et le joueur. Mais l’objet boomerang lui-même est bien représenté par une classe dédiée.

---

## 4. Comment gérez-vous les 3 états du boomerang ?

Nous gérons les trois états du boomerang avec une énumération `BoomerangState`.

```python
class BoomerangState(Enum):
    INACTIVE = auto()
    LAUNCHING = auto()
    RETURNING = auto()
```

Les trois états sont :

- `INACTIVE` : le boomerang n’est pas utilisé.
- `LAUNCHING` : le boomerang est en train de partir dans la direction du joueur.
- `RETURNING` : le boomerang revient vers le joueur.

Le boomerang stocke son état courant dans un attribut :

```python
self.state = BoomerangState.INACTIVE
```

Dans `GameView`, on utilise cet état pour savoir quelle logique appliquer à chaque frame.

Par exemple :

```python
if self.boomerang.state == BoomerangState.LAUNCHING:
    self._update_boomerang_launching()

elif self.boomerang.state == BoomerangState.RETURNING:
    self._update_boomerang_returning()
```

Quand le joueur utilise le boomerang, on passe de l’état `INACTIVE` à l’état `LAUNCHING`. Le boomerang commence alors à avancer dans la direction du joueur.

Pendant l’état `LAUNCHING`, plusieurs événements peuvent le faire passer à `RETURNING` :

- il atteint sa distance maximale ;
- il touche un mur ;
- il touche un ennemi ;
- il touche un interrupteur.

Pendant l’état `RETURNING`, le boomerang se dirige vers la position actuelle du joueur. Quand il est assez proche du joueur, il repasse à `INACTIVE`.

Cette organisation correspond à une machine à états. Elle est plus claire que d’utiliser plusieurs booléens comme :

```python
is_active
is_launched
is_returning
```

Avec plusieurs booléens, on pourrait créer des états incohérents, par exemple un boomerang à la fois inactif et en train de revenir. Avec une `Enum`, il ne peut être que dans un seul état à la fois.

---

## 5. Comment gérez-vous le fait que vous avez maintenant deux types d’armes, avec des comportements différents ? Pensez-vous que vous pourriez ajouter une troisième arme sans tout refaire ?

Nous avons deux armes :

- le boomerang ;
- l’épée.

Elles ont des comportements différents :

- le boomerang est lancé, se déplace à distance, puis revient vers le joueur ;
- l’épée est une attaque courte autour du joueur, avec une animation directionnelle.

Pour gérer quelle arme est active, nous avons ajouté une `Enum` dans `GameView`.

```python
class ActiveWeapon(Enum):
    BOOMERANG = 1
    SWORD = 2
```

`GameView` stocke ensuite l’arme actuellement sélectionnée :

```python
self.active_weapon = ActiveWeapon.BOOMERANG
```

La touche `R` sert à changer d’arme. La touche `D` sert à utiliser l’arme active.

La logique est donc du type :

```python
if self.active_weapon == ActiveWeapon.BOOMERANG:
    self._launch_boomerang()

elif self.active_weapon == ActiveWeapon.SWORD:
    self._start_sword_attack()
```

Cette solution est simple et fonctionne bien pour deux armes. Elle permet déjà de séparer les classes `Boomerang` et `Sword`, chacune avec ses propres attributs.

Ajouter une troisième arme serait possible sans tout refaire, mais il faudrait encore modifier plusieurs endroits dans `GameView` :

- ajouter une nouvelle valeur dans `ActiveWeapon` ;
- créer une nouvelle classe d’arme ;
- initialiser cette arme ;
- gérer son comportement lorsque le joueur appuie sur `D` ;
- mettre à jour son mouvement ou son animation ;
- la dessiner ;
- gérer ses collisions avec les ennemis, cristaux, interrupteurs, etc.

Donc notre design est extensible, mais pas encore totalement polymorphique.

Une amélioration possible serait de créer une classe de base abstraite `Weapon`, avec des méthodes communes comme :

```python
start_attack()
update()
draw()
hits_enemy()
hits_switch()
```

Ensuite, `Sword`, `Boomerang` et une troisième arme pourraient hériter de cette classe ou implémenter la même interface. `GameView` pourrait alors manipuler les armes de manière plus générale, sans connaître tous les détails de chaque arme.

Notre choix actuel est donc adapté pour le stade actuel du projet, mais une abstraction supplémentaire serait utile si le nombre d’armes augmente.

---

## 6. Comment gérez-vous le fait que vous avez maintenant deux types de monstres, avec des comportements différents ? Pensez-vous que vous pourriez ajouter un troisième monstre sans tout refaire ?

Nous avons actuellement plusieurs types de monstres :

- les spinners ;
- les chauves-souris ;
- les slimes.

Chaque type de monstre a son propre fichier :

- `spinner.py` ;
- `bat.py` ;
- `slime.py`.

Chaque monstre possède un comportement différent :

- le spinner fait des allers-retours sur une ligne horizontale ou verticale ;
- la chauve-souris se déplace dans une zone rectangulaire avec une direction semi-aléatoire ;
- le slime patrouille ou poursuit le joueur avec une ligne de vue et un navmesh.

Dans `GameView`, nous gardons des listes séparées :

```python
self.spinners
self.bats
self.slimes
```

Nous gardons aussi des listes de sprites correspondantes, car Arcade dessine et teste les collisions sur des sprites.

Cette organisation permet déjà d’ajouter un nouveau monstre sans refaire tout le projet. Pour ajouter un nouveau monstre, on pourrait :

- ajouter une nouvelle valeur dans `GridCell` ;
- ajouter un nouveau caractère dans `map.py` ;
- créer un nouveau fichier, par exemple `ghost.py` ;
- créer une classe ou `dataclass` pour ce monstre ;
- créer une fonction qui lit ses positions dans la map ;
- ajouter ses sprites dans `GameView` ;
- ajouter sa logique de mouvement ;
- ajouter ses collisions avec le joueur et les armes.

Cependant, comme pour les armes, `GameView` connaît encore explicitement chaque type de monstre. Ce n’est donc pas un design totalement polymorphique.

Une amélioration possible serait de créer une classe de base ou interface `Enemy`, avec des méthodes communes comme :

```python
update()
draw()
touches_player()
is_hit_by_weapon()
```

Ensuite, `Spinner`, `Bat`, `Slime` et un futur ennemi pourraient avoir une interface commune. `GameView` pourrait alors avoir une seule liste :

```python
self.enemies: list[Enemy]
```

et appeler les mêmes méthodes pour tous les monstres.

Notre solution actuelle est donc modulaire et compréhensible, mais elle pourrait être améliorée pour devenir plus extensible si le jeu grandit.

---

## 7. Qu’avez-vous choisi comme type de nœud `TypeNoeud` ? Pourquoi ?

Dans notre navmesh, nous avons choisi de représenter un nœud par un tuple de deux entiers :

```python
Node = tuple[int, int]
```

Un nœud représente une position dans la grille de la map.

Par exemple :

```python
(4, 7)
```

représente la cellule située à la colonne 4 et à la ligne 7.

Nous avons choisi ce type pour plusieurs raisons.

D’abord, c’est simple. Un nœud de navigation correspond directement à une cellule de la carte.

Ensuite, un tuple est immuable. Cela veut dire qu’une fois créé, il ne peut pas être modifié. C’est important parce que les nœuds sont utilisés dans le graphe NetworkX. Les nœuds doivent pouvoir être utilisés comme clés, et les tuples sont adaptés pour cela.

Ce choix permet aussi de convertir facilement une position de grille en position en pixels :

```python
def node_position(node: Node) -> Point:
    x, y = node
    return (grid_to_pixels(x), grid_to_pixels(y))
```

Nous avons également défini un type pour les positions en pixels :

```python
Point = tuple[float, float]
```

La distinction est importante :

- `Node` représente une position dans la grille ;
- `Point` représente une position en pixels dans le monde Arcade.

Cette séparation évite de mélanger les coordonnées de grille et les coordonnées d’affichage.

---

## 8. À quel niveau traitez-vous la construction du navmesh, et où le stockez-vous ? Pourquoi ces choix ?

La construction du navmesh est faite dans le fichier `navmesh.py`.

Nous avons choisi de ne pas mettre cette logique dans `Map`, parce que `Map` doit seulement représenter la carte : sa largeur, sa hauteur, ses cellules et la position de départ du joueur. Construire un graphe de navigation est une autre responsabilité.

Nous avons aussi choisi de ne pas mettre la construction du navmesh directement dans `slime.py`. Même si actuellement les slimes sont les seuls à utiliser le navmesh, le navmesh est une structure générale qui pourrait servir à d’autres ennemis plus tard.

Dans `GameView`, après avoir chargé la map, nous construisons le navmesh une seule fois :

```python
self.navmesh = create_navmesh(self.map)
```

Puis nous le stockons dans `GameView`.

Ce choix est logique parce que `GameView` orchestre le jeu. Il connaît la map, les ennemis, les sprites, les murs et le joueur. Il peut donc créer le navmesh au bon moment et le transmettre aux slimes quand ils en ont besoin.

Les slimes utilisent ensuite le navmesh dans leur mise à jour :

```python
update_slime_movement(
    slime,
    self.navmesh,
    self.random,
    self.player.position,
    self.walls,
)
```

Ce choix a plusieurs avantages :

- `Map` reste simple ;
- `navmesh.py` contient la logique de graphe ;
- `slime.py` utilise le navmesh sans gérer sa construction ;
- le navmesh n’est construit qu’une seule fois ;
- le code est plus facile à tester.

Comme notre map ne change pas beaucoup pendant une partie, il n’est pas nécessaire de reconstruire le navmesh à chaque frame.

---

## 9. Pouvez-vous tester la construction du navmesh, voire la recherche de chemin, sans dépendre de Arcade ?

Oui. La construction du navmesh et la recherche de chemin peuvent être testées sans dépendre de la fenêtre Arcade ou des sprites.

Le fichier `navmesh.py` dépend principalement de :

- `Map` ;
- `GridCell` ;
- `NetworkX` ;
- `TILE_SIZE`.

Il ne dépend pas du rendu graphique, de la caméra, du moteur physique ou des événements clavier.

On peut donc tester le navmesh avec une petite map en texte. Par exemple, on peut créer une map avec `map_from_string`, puis appeler `create_navmesh`.

Exemple :

```python
text = '''
width: 5
height: 3
---
P   x
 xx x
    x
---
'''

game_map = map_from_string(text)
navmesh = create_navmesh(game_map)
```

Ensuite, on peut vérifier que :

- les cases libres deviennent bien des nœuds ;
- les buissons ne deviennent pas des nœuds ;
- les trous ne deviennent pas des nœuds ;
- les portails sont traités comme obstacles pour les slimes ;
- un chemin existe entre deux points accessibles ;
- aucun chemin n’existe si la carte est bloquée.

On peut aussi tester la recherche de chemin :

```python
path = shortest_path(navmesh, (16, 16), (80, 80))
assert len(path) > 0
```

Ce test ne nécessite pas d’ouvrir une fenêtre de jeu. Il teste seulement la logique de la carte et du graphe.

Cela montre que notre design sépare correctement la logique de navigation de l’affichage Arcade.

---

## 10. Si vous avez `n × n` nœuds par cellule, et une carte de taille `m × m`, quelle est la complexité de vos différents algorithmes ?

Supposons que la carte a une taille `m × m`. Elle contient donc :

```text
m² cellules
```

Si chaque cellule contient `n × n` nœuds, alors chaque cellule contient :

```text
n² nœuds
```

Le nombre total de nœuds du navmesh est donc :

```text
V = m² n²
```

Si chaque nœud est connecté à un nombre constant de voisins, par exemple 4 ou 8 voisins, alors le nombre d’arêtes est proportionnel au nombre de nœuds :

```text
E = O(V)
```

Donc :

```text
E = O(m² n²)
```

### Construction des nœuds

Pour construire les nœuds, on parcourt toutes les cellules et tous les sous-nœuds dans chaque cellule.

Complexité :

```text
O(m² n²)
```

### Construction des arêtes

Pour chaque nœud, on regarde un nombre constant de voisins.

Complexité :

```text
O(V)
```

Donc :

```text
O(m² n²)
```

### Recherche de plus court chemin

Avec Dijkstra, la complexité classique est :

```text
O((V + E) log V)
```

Comme `E = O(V)`, cela devient :

```text
O(V log V)
```

En remplaçant `V` par `m² n²`, on obtient :

```text
O(m² n² log(m² n²))
```

### Mémoire

Le graphe doit stocker les nœuds et les arêtes.

Complexité mémoire :

```text
O(V + E)
```

Comme `E = O(V)`, cela donne :

```text
O(V) = O(m² n²)
```

### Dans notre implémentation actuelle

Dans notre version actuelle, nous avons surtout un nœud par cellule. Cela correspond au cas :

```text
n = 1
```

Donc le nombre total de nœuds est environ :

```text
V = m²
```

La construction du navmesh est donc :

```text
O(m²)
```

La recherche de chemin avec Dijkstra est :

```text
O(m² log(m²))
```

Si on améliore le navmesh avec `3 × 3` nœuds par cellule, alors `n = 3`, donc chaque cellule contient 9 nœuds. Le déplacement devient plus précis, mais le graphe devient aussi plus grand.

---

## 11. Quelle structure de données utilisez-vous pour représenter les conditions d’ouverture des portails ? Pourquoi ?

Nous représentons les conditions d’ouverture des portails avec une structure récursive de classes.

Nous avons une classe de base :

```python
class GateCondition:
    def evaluate(self, switch_states: dict[str, bool]) -> bool:
        raise NotImplementedError
```

Puis nous avons plusieurs classes concrètes :

```python
@dataclass(frozen=True)
class SwitchIsOn(GateCondition):
    switch_id: str

@dataclass(frozen=True)
class NotCondition(GateCondition):
    condition: GateCondition

@dataclass(frozen=True)
class AndCondition(GateCondition):
    left: GateCondition
    right: GateCondition

@dataclass(frozen=True)
class OrCondition(GateCondition):
    left: GateCondition
    right: GateCondition
```

Cette structure forme un arbre logique.

Par exemple, la condition YAML suivante :

```yaml
open_if:
  and:
    - switch_is_on: first
    - not:
        - switch_is_on: second
```

peut être représentée comme :

```python
AndCondition(
    SwitchIsOn("first"),
    NotCondition(SwitchIsOn("second"))
)
```

Nous avons choisi cette structure parce que les conditions logiques sont naturellement récursives. Une condition peut contenir d’autres conditions.

Par exemple :

- un `not` contient une condition ;
- un `and` contient deux conditions ;
- un `or` contient deux conditions ;
- un `switch_is_on` est une condition de base.

Chaque classe sait comment s’évaluer avec la méthode `evaluate`.

Par exemple :

```python
gate.open_if.evaluate(states)
```

Ici, `GameView` ou `Gate` n’a pas besoin de savoir si la condition est un `and`, un `or`, un `not` ou un simple `switch_is_on`. Il appelle simplement `evaluate`.

C’est un bon exemple de polymorphisme : plusieurs classes différentes partagent la même méthode, mais chacune l’implémente à sa manière.

---

## 12. Pouvez-vous tester l’évaluation des formules logiques sans dépendre de Arcade ?

Oui. L’évaluation des formules logiques peut être testée sans Arcade.

Les classes `SwitchIsOn`, `NotCondition`, `AndCondition` et `OrCondition` ne dépendent pas de l’affichage, des sprites, de la caméra ou du moteur physique. Elles ont seulement besoin d’un dictionnaire qui donne l’état des interrupteurs.

Par exemple :

```python
states = {
    "first": True,
    "second": False,
}
```

On peut tester une condition simple :

```python
condition = SwitchIsOn("first")
assert condition.evaluate(states) is True
```

On peut aussi tester une condition composée :

```python
condition = AndCondition(
    SwitchIsOn("first"),
    NotCondition(SwitchIsOn("second")),
)

assert condition.evaluate(states) is True
```

On peut aussi tester une condition `or` :

```python
condition = OrCondition(
    SwitchIsOn("first"),
    SwitchIsOn("second"),
)

assert condition.evaluate(states) is True
```

Ces tests ne nécessitent pas de lancer le jeu. Ils testent seulement la logique des formules.

C’est un avantage de notre design : la logique des portails est séparée de la logique graphique. On peut donc tester cette partie facilement avec des tests unitaires.

---

## 13. S’il y a `n` interrupteurs et `m` portails, et en supposant que chaque condition de portail n’est qu’un unique `switch_is_on`, quelle est la complexité de traitement des portails à chaque frame ?

Supposons :

- `n` interrupteurs ;
- `m` portails ;
- chaque portail a une condition simple de type `switch_is_on`.

Dans notre code, pour mettre à jour les portails, nous construisons d’abord un dictionnaire contenant l’état de tous les interrupteurs :

```python
states = switch_states(switches)
```

Cette fonction parcourt tous les interrupteurs.

Complexité :

```text
O(n)
```

Ensuite, nous parcourons tous les portails :

```python
for gate in gates:
    gate.is_open = gate.open_if.evaluate(states)
```

Pour chaque portail, la condition est un simple `switch_is_on`. Elle fait donc une recherche dans le dictionnaire :

```python
switch_states[self.switch_id]
```

Une recherche dans un dictionnaire Python est en moyenne en temps constant :

```text
O(1)
```

Donc évaluer les `m` portails coûte :

```text
O(m)
```

La complexité totale est donc :

```text
O(n + m)
```

Cependant, dans notre jeu, nous n’avons pas besoin de recalculer les portails à chaque frame si aucun interrupteur n’a changé. Les portails changent seulement lorsqu’un interrupteur est activé.

Donc, dans notre design, il est préférable d’appeler `update_gates` seulement quand un switch change d’état. Dans ce cas, le coût `O(n + m)` est payé seulement au moment d’une interaction, pas 60 fois par seconde.

C’est plus efficace et plus logique.

---

# Résumé final

Dans notre projet, nous avons essayé de séparer les responsabilités entre plusieurs modules.

Les choix principaux sont :

- `Direction` est une `Enum`, car une direction est une valeur parmi un ensemble fini.
- Les événements clavier Arcade restent dans `GameView`, puis sont transformés en données plus spécifiques.
- Le boomerang a une classe séparée et hérite de `arcade.TextureAnimationSprite`.
- Les états du boomerang sont représentés par une `Enum`.
- Les armes sont séparées, mais pourraient être encore améliorées avec une classe abstraite `Weapon`.
- Les monstres sont séparés par fichiers, mais pourraient être encore améliorés avec une interface commune `Enemy`.
- Le navmesh est séparé dans `navmesh.py` et stocké dans `GameView`.
- Les nœuds du navmesh sont représentés par des tuples `(x, y)`.
- La logique du navmesh peut être testée sans Arcade.
- Les conditions des portails sont représentées par un arbre de classes récursives.
- Les formules logiques peuvent être testées sans Arcade.
- La mise à jour des portails coûte `O(n + m)` dans le cas de conditions simples.

Les principales pistes d’amélioration seraient :

- alléger `GameView`, qui contient encore beaucoup de logique ;
- rendre les armes plus polymorphiques ;
- rendre les ennemis plus polymorphiques ;
- affiner le navmesh avec plusieurs nœuds par cellule ;
- ajouter davantage de tests unitaires.