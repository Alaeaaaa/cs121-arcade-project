from constants import PLAYER_INVINCIBILITY_DURATION, SHIELD_DURATION
import pytest
from map import (
    Map, GridCell, InvalidMapFileException,
    map_from_string, cell_from_char,
    SwitchIsOn, AndCondition, OrCondition, NotCondition,
)
from switch import Switch, Gate, toggle_switch, update_gates, switch_states
from player import Player
from boomerang import Boomerang, BoomerangState
from direction import Direction


# des petites maps qu'on utilise pour les tests

# map simple avec herbe, buisson et cristal
MAP_CELLULES = map_from_string(
    "width: 4\nheight: 1\n---\nP x*\n---\n"
)

# map sans obstacles, comme ca le navmesh est plus simple a tester
MAP_OUVERTE = map_from_string(
    "width: 3\nheight: 3\n---\n   \n P \n   \n---\n"
)

# map avec un buisson au milieu pour voir si il est bien bloquant
MAP_BUISSON = map_from_string(
    "width: 3\nheight: 1\n---\nPx \n---\n"
)


# petite fonction pour créer un switch sans réecrire toute la ligne a chaque fois
def creer_switch(sid:str="s1", is_on:bool=False) -> Switch:
    return Switch(sid, 0, 0, is_on=is_on, is_being_hit=False)


""" ici on fait des classes plus simples pour tester juste la logique
 comme ca on a pas besoin de charger arcade ni les images du jeu. Toutefoid, en
 empruntant les méthodes de chacune des classes en les nommant, on avait des checkers
 pas contents, on est donc obligé d'hériter des classes respectives pour tester
 les bonnes méthodes et fonctions. On le fait indépendamment d'arcade car on définit
 un nouvel init sans faire appel à super. Notre première approche fonctionnait, mais
 les erreurs de type obligent à reconsidérer"""

class PlayerTest(Player):
    def __init__(self) -> None:
        self.health = 3
        self.max_health = 3
        self.invincibility_time = 0.0
        self.shield_time = 0.0
        self.direction = Direction.SOUTH



class BoomerangTest(Boomerang):
    def __init__(self) -> None:
        self.state = BoomerangState.INACTIVE
        self.distance_travelled = 0.0
        self._position = (0.0, 0.0)
        self.direction = Direction.SOUTH


class TestCellFromChar:

    def test_chars_connus(self)->None:
        # P donne la position du joueur mais la case reste quand meme de l'herbe
        assert cell_from_char(" ", 0, 0) == GridCell.GRASS
        assert cell_from_char("x", 0, 0) == GridCell.BUSH
        assert cell_from_char("P", 0, 0) == GridCell.GRASS

    def test_char_inconnu_leve_exception(self)->None:
        pytest.raises(InvalidMapFileException, cell_from_char, "Z", 0, 0)


class TestMap:
    """il y'a trop de cas à tester pour la map, on en enone quelaues uns c'est tout"""

    def test_dimensions_et_cellules(self)->None:
        assert MAP_CELLULES.width == 4 and MAP_CELLULES.height == 1
        assert MAP_CELLULES.get(2, 0) == GridCell.BUSH
        assert MAP_CELLULES.get(3, 0) == GridCell.CRYSTAL

    def test_map_sans_joueur_leve_exception(self)->None:
        pytest.raises(InvalidMapFileException, map_from_string,
                      "width: 3\nheight: 1\n---\n   \n---\n")

    def test_acces_hors_bornes_leve_exception(self)->None:
        pytest.raises(ValueError, MAP_CELLULES.get, 99, 0)

    def test_largeur_incorrecte_leve_exception(self) -> None:
    #width doit être un entier valide, "trois" est un string !
        with pytest.raises(InvalidMapFileException):
            map_from_string(
                "width: trois\nheight: 1\n---\nP  \n---\n"
            )
    def test_map_avec_plusieurs_joueurs_leve_exception(self) -> None:
    #une map ne peut contenir qu'un seul joueur
        with pytest.raises(InvalidMapFileException):
            map_from_string(
                "width: 3\nheight: 1\n---\nPP \n---\n"
            )



class TestGateConditions:
    """encore une fois, trooop de cas.. On se contente de quelques uns !"""

    def test_operateurs_and_or_not(self)->None:
        s = {"s1": True, "s2": False}
        assert AndCondition(SwitchIsOn("s1"), SwitchIsOn("s2")).evaluate(s) is False
        assert OrCondition(SwitchIsOn("s1"), SwitchIsOn("s2")).evaluate(s) is True
        assert NotCondition(SwitchIsOn("s1")).evaluate(s) is False

    def test_switch_inconnu_leve_exception(self)->None:
        pytest.raises(InvalidMapFileException, SwitchIsOn("inconnu").evaluate, {"s1": True})
    def test_switch_state_invalide_leve_exception(self) -> None:
    # l'état initial d'un switch doit être on ou off, pas autre chose
        from map import parse_switch_config
        with pytest.raises(InvalidMapFileException):
            parse_switch_config({
                "id": "s1",
                "x": 0,
                "y": 0,
                "state": "maybe",
            })



class TestSwitchGate:

    def test_toggle_change_etat_et_states_reflète(self)->None:
        s = creer_switch(is_on=False)
        toggle_switch(s)
        assert s.is_on is True
        assert switch_states([s]) == {"s1": True}

    def test_gate_ouvre_et_ferme_selon_switch(self)->None:
        gate = Gate(x=0, y=0, open_if=SwitchIsOn("s1"), is_open=False)
        update_gates([creer_switch(is_on=True)], [gate])
        assert gate.is_open is True
        update_gates([creer_switch(is_on=False)], [gate])
        assert gate.is_open is False

    def test_gate_complexe_and_not(self) -> None:
    #vérifie qu'une combinaison and ou not est correctement évaluée, c'est un cas parmi tant d'autres
        condition = AndCondition(
            SwitchIsOn("s1"),
            NotCondition(SwitchIsOn("s2")),
        )
        gate = Gate(x=0, y=0, open_if=condition, is_open=False)

        update_gates(
            [creer_switch("s1", is_on=True), creer_switch("s2", is_on=False)],
            [gate])

        assert gate.is_open is True


class TestNavmesh:

    def test_noeuds_accessibles_et_obstacles_exclus(self)->None:
        from navmesh import create_navmesh
        # chaque case est divisée en 9 petits noeuds, donc 3x3 cases donne 81 noeuds
        assert len(create_navmesh(MAP_OUVERTE).graph.nodes) == 81
        navmesh = create_navmesh(MAP_BUISSON)
        # le buisson est la case du milieu, donc ses mini-noeuds ne doivent pas exister
        assert all(
            (x, y) not in navmesh.graph.nodes
            for x in range(3, 6)
            for y in range(0, 3)
        )

    def test_chemin_trouve_et_graphe_vide_retourne_cible(self)->None:
        from navmesh import create_navmesh, shortest_path, NavMesh
        import networkx as nx
        assert len(shortest_path(create_navmesh(MAP_OUVERTE), (24.0, 24.0), (120.0, 24.0))) > 0
        # si il y a aucun noeud, on renvoie juste la cible directement
        assert shortest_path(NavMesh(graph=nx.Graph()), (0.0, 0.0), (100.0, 100.0)) == [(100.0, 100.0)]

    def test_can_slime_stand_on_refuse_obstacles_et_hors_map(self) -> None:
        # un slime ne peut pas se trouver sur un obstacle ou hors de la map
        from navmesh import can_slime_stand_on

        game_map = map_from_string(
            "width: 4\nheight: 1\n---\nPxOm\n---\n"
        )

        assert can_slime_stand_on(game_map, 0, 0) is True
        assert can_slime_stand_on(game_map, 1, 0) is False
        assert can_slime_stand_on(game_map, 2, 0) is False
        assert can_slime_stand_on(game_map, -1, 0) is False



class TestPlayer:
    """on aurait aimé tester le mouvement du joueur et sa mise à jour en fonction
    des booléens de la méthode update_movement, mais hélàs cela nécessite l'initialisation
    de change_x et y, et on a des problèmes qui en résultent. On pourrait pour ça refactoriser
    la classe Player à l'instar de Enemy pour avoir logi_x et logic_y, mais faute de temps..."""

    def test_degat_reduit_pv(self)->None:
        # si le joueur est pas invincible, il perd un point de vie
        p = PlayerTest()
        p.take_damage(1)
        assert p.health == 2

    def test_invincible_absorbe_degat(self)->None:
        # quand il est invincible, les pv ne changent pas
        p = PlayerTest()
        p.invincibility_time = 1.0
        p.take_damage(1)
        assert p.health == 3

    def test_take_damage_retourne_true_si_vie_perdue(self) -> None:
        # le joueur doit perdre une vie, et le booléen doit l'indiquer.
        p = PlayerTest()
        result = p.take_damage(1)

        assert result is True
        assert p.health == 2
        assert p.invincibility_time == PLAYER_INVINCIBILITY_DURATION

    def test_bouclier_absorbe_degat_et_disparait(self) -> None:
        # le jueur ne prend pas de dégats, d'où le False
        p = PlayerTest()
        p.shield_time = 2.0

        result = p.take_damage(1)

        assert result is False
        assert p.health == 3
        assert p.shield_time == 0.0
        assert p.invincibility_time == PLAYER_INVINCIBILITY_DURATION

    def test_health_ne_devient_pas_negative(self) -> None:
        #on en est sur de toute façon, la health du joueur
        #retourne max entre 0 et pv restants
        p = PlayerTest()
        p.take_damage(10)

        assert p.health == 0

    def test_activate_shield_met_le_timer(self) -> None:
        #initialisation du compteur à l'activation du shield
        p = PlayerTest()
        p.activate_shield()

        assert p.shield_time == SHIELD_DURATION

    def test_update_shield_diminue_le_timer(self) -> None:
        #et enfin, le compteur du bouclier aussi doit diminuer avec le temps
        p = PlayerTest()
        p.shield_time = 1.0

        p.update_shield(0.25)

        assert p.shield_time == 0.75

class TestBoomerang:
    """on évite tous les tests qui font appel à des attributs de sprite d'arcade"""
    def test_is_active_true_quand_lance(self) -> None:
        # un boomerang en état launching doit etre actif
        b = BoomerangTest()
        b.state = BoomerangState.LAUNCHING
        assert b.is_active() is True

    def test_return_to_player_passe_en_retour(self) -> None:
        #return_to_player doit mettre le boomerang en état returning
        b = BoomerangTest()
        b.state = BoomerangState.LAUNCHING

        b.return_to_player()

        assert b.state == BoomerangState.RETURNING

    def test_deactivate_remet_inactif_et_distance_a_zero(self) -> None:
        b = BoomerangTest()
        b.state = BoomerangState.RETURNING
        b.distance_travelled = 50.0
        b.deactivate()
        assert b.state == BoomerangState.INACTIVE
        assert b.distance_travelled == 0.0


"""on reprenait juste les methodes du slime qui n'ont pas besoin d'arcade
 et on testait surtout le déplacement et si il arrive a sa destination, on hérite de slime
 car la première approche de 'emprunter' les méthodes du slime ne satisfaisait pas le type checker"""

from slime import Slime

class SlimeTest(Slime):
    def __init__(self) -> None:
        self.logic_x = 0.0
        self.logic_y = 0.0
        self.destination_x = 0.0
        self.destination_y = 0.0
        self.current_path = []
        self.current_path_index = 0

class TestSlime:

    def test_destination_atteinte_quand_position_egale(self)->None:
        # le slime est deja sur le point ou il doit aller
        s = SlimeTest()
        s.logic_x, s.logic_y = 100.0, 100.0
        s.destination_x, s.destination_y = 100.0, 100.0
        assert s._has_reached_destination() is True

    def test_destination_non_atteinte_quand_loin(self)->None:
        # la il est encore trop loin de sa destination
        s = SlimeTest()
        s.logic_x, s.logic_y = 0.0, 0.0
        s.destination_x, s.destination_y = 500.0, 500.0
        assert s._has_reached_destination() is False

    def test_move_directly_to_rapproche_du_point(self)->None:
        # apres le déplacement il doit etre plus proche du point choisi
        s = SlimeTest()
        s.logic_x, s.logic_y = 0.0, 0.0
        import math
        avant = math.dist((s.logic_x, s.logic_y), (100.0, 0.0))
        s._move_directly_to((100.0, 0.0))
        apres = math.dist((s.logic_x, s.logic_y), (100.0, 0.0))
        assert apres < avant


# map avec un cristal et un slime pour tester find_cells
MAP_FIND_CELLS = map_from_string(
    "width: 3\nheight: 1\n---\nP*m\n---\n"
)


class TestUtils:

    def test_grid_to_pixels_augmente(self)->None:
        from utils import grid_to_pixels
        # quand on avance dans la grille, la position en pixels augmente aussi
        assert grid_to_pixels(1) > grid_to_pixels(0)
        assert grid_to_pixels(2) > grid_to_pixels(1)

    def test_find_cells_trouve_la_bonne_case(self)->None:
        from utils import find_cells
        assert (1, 0) in find_cells(MAP_FIND_CELLS, GridCell.CRYSTAL)
        assert (2, 0) in find_cells(MAP_FIND_CELLS, GridCell.SLIME)

    def test_find_cells_vide_si_absent(self)->None:
        from utils import find_cells
        assert find_cells(MAP_FIND_CELLS, GridCell.HOLE) == []


class TestPatrolDestinations:

    def test_destinations_dans_le_rayon(self)->None:
        # les destinations doivent rester sur de l'herbe ou le slime peut aller
        from slime import _patrol_destinations
        destinations = _patrol_destinations(MAP_OUVERTE, 1, 1)
        assert len(destinations) > 0
        assert all(MAP_OUVERTE.get(x, y) == GridCell.GRASS for x, y in destinations)


from map import SwitchConfig, GateConfig
from switch import create_switch, create_gate, create_switches, create_gates

# config d'un switch allumé pour les tests
CONFIG_SWITCH_ON  = SwitchConfig(switch_id="s1", x=0, y=0, is_on=True)

# config d'un switch eteint pour comparer
CONFIG_SWITCH_OFF = SwitchConfig(switch_id="s1", x=0, y=0, is_on=False)

# config d'une gate qui depend du switch s1
CONFIG_GATE = GateConfig(x=1, y=0, open_if=SwitchIsOn("s1"))


class TestCreateSwitchGate:

    def test_create_switch_respecte_config(self)->None:
        # le switch créé doit reprendre les infos de la config
        s = create_switch(CONFIG_SWITCH_ON)
        assert s.switch_id == "s1" and s.is_on is True and s.is_being_hit is False

    def test_create_gate_etat_initial_selon_switch(self)->None:
        # si le switch est on la gate s'ouvre, sinon elle reste fermée
        assert create_gate(CONFIG_GATE, {"s1": True}).is_open  is True
        assert create_gate(CONFIG_GATE, {"s1": False}).is_open is False
