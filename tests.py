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
    "width: 3\nheight: 1\n---\nPxP\n---\n"
)


# petite fonction pour créer un switch sans réecrire toute la ligne a chaque fois
def creer_switch(sid="s1", is_on=False) -> Switch:
    return Switch(sid, 0, 0, is_on=is_on, is_being_hit=False)


# ici on fait des classes plus simples pour tester juste la logique
# comme ca on a pas besoin de charger arcade ni les images du jeu

class PlayerTest:
    health            = 3
    invincibility_time = 0.0
    shield_time       = 0.0

    is_invincible     = Player.is_invincible
    has_active_shield = Player.has_active_shield
    take_damage       = Player.take_damage


class BoomerangTest:
    state              = BoomerangState.INACTIVE
    distance_travelled = 0.0
    center_x           = 0.0
    center_y           = 0.0
    direction          = None

    is_active        = Boomerang.is_active
    launch           = Boomerang.launch
    return_to_player = Boomerang.return_to_player
    deactivate       = Boomerang.deactivate


class TestCellFromChar:

    def test_chars_connus(self):
        # P donne la position du joueur mais la case reste quand meme de l'herbe
        assert cell_from_char(" ", 0, 0) == GridCell.GRASS
        assert cell_from_char("x", 0, 0) == GridCell.BUSH
        assert cell_from_char("P", 0, 0) == GridCell.GRASS

    def test_char_inconnu_leve_exception(self):
        pytest.raises(InvalidMapFileException, cell_from_char, "Z", 0, 0)


class TestMap:

    def test_dimensions_et_cellules(self):
        assert MAP_CELLULES.width == 4 and MAP_CELLULES.height == 1
        assert MAP_CELLULES.get(2, 0) == GridCell.BUSH
        assert MAP_CELLULES.get(3, 0) == GridCell.CRYSTAL

    def test_map_sans_joueur_leve_exception(self):
        pytest.raises(InvalidMapFileException, map_from_string,
                      "width: 3\nheight: 1\n---\n   \n---\n")

    def test_acces_hors_bornes_leve_exception(self):
        pytest.raises(ValueError, MAP_CELLULES.get, 99, 0)


class TestGateConditions:

    def test_operateurs_and_or_not(self):
        s = {"s1": True, "s2": False}
        assert AndCondition(SwitchIsOn("s1"), SwitchIsOn("s2")).evaluate(s) is False
        assert OrCondition(SwitchIsOn("s1"), SwitchIsOn("s2")).evaluate(s) is True
        assert NotCondition(SwitchIsOn("s1")).evaluate(s) is False

    def test_switch_inconnu_leve_exception(self):
        pytest.raises(InvalidMapFileException, SwitchIsOn("inconnu").evaluate, {"s1": True})


class TestSwitchGate:

    def test_toggle_change_etat_et_states_reflète(self):
        s = creer_switch(is_on=False)
        toggle_switch(s)
        assert s.is_on is True
        assert switch_states([s]) == {"s1": True}

    def test_gate_ouvre_et_ferme_selon_switch(self):
        gate = Gate(x=0, y=0, open_if=SwitchIsOn("s1"), is_open=False)
        update_gates([creer_switch(is_on=True)], [gate])
        assert gate.is_open is True
        update_gates([creer_switch(is_on=False)], [gate])
        assert gate.is_open is False


class TestNavmesh:

    def test_noeuds_accessibles_et_obstacles_exclus(self):
        from navmesh import create_navmesh
        # il y a 9 cases d'herbe donc normalement 9 noeuds
        assert len(create_navmesh(MAP_OUVERTE).graph.nodes) == 9
        # le buisson est un obstacle donc il doit pas etre dans le graphe
        assert (1, 0) not in create_navmesh(MAP_BUISSON).graph.nodes

    def test_chemin_trouve_et_graphe_vide_retourne_cible(self):
        from navmesh import create_navmesh, shortest_path, NavMesh
        import networkx as nx
        assert len(shortest_path(create_navmesh(MAP_OUVERTE), (24.0, 24.0), (120.0, 24.0))) > 0
        # si il y a aucun noeud, on renvoie juste la cible directement
        assert shortest_path(NavMesh(graph=nx.Graph()), (0.0, 0.0), (100.0, 100.0)) == [(100.0, 100.0)]


class TestPlayer:

    def test_degat_reduit_pv(self):
        # si le joueur est pas invincible, il perd un point de vie
        p = PlayerTest()
        p.take_damage(1)
        assert p.health == 2

    def test_invincible_absorbe_degat(self):
        # quand il est invincible, les pv ne changent pas
        p = PlayerTest()
        p.invincibility_time = 1.0
        p.take_damage(1)
        assert p.health == 3


class TestBoomerang:

    def test_launch_passe_en_etat_actif(self):
        b = BoomerangTest()
        b.launch(Direction.NORTH, 10.0, 20.0)
        assert b.is_active() is True
        assert b.state == BoomerangState.LAUNCHING

    def test_return_puis_deactivate_remet_inactif(self):
        b = BoomerangTest()
        b.launch(Direction.NORTH, 0.0, 0.0)
        b.return_to_player()
        assert b.state == BoomerangState.RETURNING
        b.deactivate()
        assert b.is_active() is False


# on reprend juste les methodes du slime qui n'ont pas besoin d'arcade
# ici on teste surtout le déplacement et si il arrive a sa destination
from slime import Slime

class SlimeTest:
    logic_x            = 0.0
    logic_y            = 0.0
    destination_x      = 0.0
    destination_y      = 0.0
    current_path       = []
    current_path_index = 0

    _has_reached_destination = Slime._has_reached_destination
    _move_directly_to        = Slime._move_directly_to


class TestSlime:

    def test_destination_atteinte_quand_position_egale(self):
        # le slime est deja sur le point ou il doit aller
        s = SlimeTest()
        s.logic_x, s.logic_y = 100.0, 100.0
        s.destination_x, s.destination_y = 100.0, 100.0
        assert s._has_reached_destination() is True

    def test_destination_non_atteinte_quand_loin(self):
        # la il est encore trop loin de sa destination
        s = SlimeTest()
        s.logic_x, s.logic_y = 0.0, 0.0
        s.destination_x, s.destination_y = 500.0, 500.0
        assert s._has_reached_destination() is False

    def test_move_directly_to_rapproche_du_point(self):
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

    def test_grid_to_pixels_augmente(self):
        from utils import grid_to_pixels
        # quand on avance dans la grille, la position en pixels augmente aussi
        assert grid_to_pixels(1) > grid_to_pixels(0)
        assert grid_to_pixels(2) > grid_to_pixels(1)

    def test_find_cells_trouve_la_bonne_case(self):
        from utils import find_cells
        assert (1, 0) in find_cells(MAP_FIND_CELLS, GridCell.CRYSTAL)
        assert (2, 0) in find_cells(MAP_FIND_CELLS, GridCell.SLIME)

    def test_find_cells_vide_si_absent(self):
        from utils import find_cells
        assert find_cells(MAP_FIND_CELLS, GridCell.HOLE) == []


class TestPatrolDestinations:

    def test_destinations_dans_le_rayon(self):
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

    def test_create_switch_respecte_config(self):
        # le switch créé doit reprendre les infos de la config
        s = create_switch(CONFIG_SWITCH_ON)
        assert s.switch_id == "s1" and s.is_on is True and s.is_being_hit is False

    def test_create_gate_etat_initial_selon_switch(self):
        # si le switch est on la gate s'ouvre, sinon elle reste fermée
        assert create_gate(CONFIG_GATE, {"s1": True}).is_open  is True
        assert create_gate(CONFIG_GATE, {"s1": False}).is_open is False

