"""
Tests pytest pour le projet CS-121 DevLog.
Couvre : map, switch/gate, player, boomerang, sword, slime, navmesh, spinner, bat, utils.
"""

import sys
import math
import random
import pytest
from unittest.mock import MagicMock, patch

# ==================================================
# Mock arcade AVANT tout import qui en dépend
# ==================================================
# Player, Spinner, Bat, Slime héritent tous de classes arcade.
# On mocke arcade une seule fois ici pour que tous les imports fonctionnent.

_arcade_mock = MagicMock()
_arcade_mock.TextureAnimationSprite = object  # classe de base neutre
_arcade_mock.Sprite = object

patch.dict(sys.modules, {"arcade": _arcade_mock}).start()

# Maintenant on peut importer sans crash
from map import (
    Map,
    GridCell,
    InvalidMapFileException,
    map_from_string,
    cell_from_char,
    SwitchIsOn,
    AndCondition,
    OrCondition,
    NotCondition,
)
from switch import (
    Switch,
    Gate,
    create_switches,
    create_gates,
    toggle_switch,
    update_gates,
    switch_states,
)
from direction import Direction
from utils import grid_to_pixels, find_cells
from constants import TILE_SIZE, PLAYER_MAX_HEALTH, PLAYER_INVINCIBILITY_DURATION, SHIELD_DURATION
from spinner import Spinner, _is_blocking_cell, _scan_until_blocked, create_spinners
from bat import Bat, _clamp, _compute_bat_bounds


# ==================================================
# Helpers
# ==================================================

def make_map(grid: str, width: int, height: int) -> Map:
    text = f"width: {width}\nheight: {height}\n---\n{grid}\n---\n"
    return map_from_string(text)


def make_player():
    """Instancie un Player en bypassant arcade proprement."""
    import player as player_module
    # On patche les dicts d'animations pour éviter le chargement des assets
    with patch.object(player_module, "PLAYER_IDLE_ANIMATIONS", {d: MagicMock() for d in Direction}), \
         patch.object(player_module, "PLAYER_RUN_ANIMATIONS", {d: MagicMock() for d in Direction}):
        p = player_module.Player.__new__(player_module.Player)
        p.direction = Direction.SOUTH
        p.max_health = PLAYER_MAX_HEALTH
        p.health = PLAYER_MAX_HEALTH
        p.invincibility_time = 0.0
        p.shield_time = 0.0
        p.change_x = 0
        p.change_y = 0
        p.animation = MagicMock()
        p.alpha = 255
        return p


def make_spinner(
    x=5, y=5,
    horizontal=True,
    min_x=3, max_x=7,
    min_y=5, max_y=5,
) -> Spinner:
    """Crée un Spinner sans passer par arcade."""
    s = Spinner.__new__(Spinner)
    s.logic_x = float(grid_to_pixels(x))
    s.logic_y = float(grid_to_pixels(y))
    s.horizontal = horizontal
    s.direction = 1
    s.min_x = float(grid_to_pixels(min_x))
    s.max_x = float(grid_to_pixels(max_x))
    s.min_y = float(grid_to_pixels(min_y))
    s.max_y = float(grid_to_pixels(max_y))
    return s


def make_bat(
    start_x=100.0, start_y=100.0,
    dx=2.0, dy=2.0,
    min_x=50, max_x=200,
    min_y=50, max_y=200,
) -> Bat:
    b = Bat.__new__(Bat)
    b.logic_x = start_x
    b.logic_y = start_y
    b.dx = dx
    b.dy = dy
    b.min_x = min_x
    b.max_x = max_x
    b.min_y = min_y
    b.max_y = max_y
    return b


# ==================================================
# Tests : cell_from_char
# ==================================================

class TestCellFromChar:

    def test_space_gives_grass(self):
        assert cell_from_char(" ", 0, 0) == GridCell.GRASS

    def test_x_gives_bush(self):
        assert cell_from_char("x", 0, 0) == GridCell.BUSH

    def test_crystal(self):
        assert cell_from_char("*", 0, 0) == GridCell.CRYSTAL

    def test_hole(self):
        assert cell_from_char("O", 0, 0) == GridCell.HOLE

    def test_spinner_horizontal(self):
        assert cell_from_char("s", 0, 0) == GridCell.SPINNER_HORIZONTAL

    def test_spinner_vertical(self):
        assert cell_from_char("S", 0, 0) == GridCell.SPINNER_VERTICAL

    def test_bat(self):
        assert cell_from_char("v", 0, 0) == GridCell.BAT

    def test_slime(self):
        assert cell_from_char("m", 0, 0) == GridCell.SLIME

    def test_player_gives_grass(self):
        assert cell_from_char("P", 0, 0) == GridCell.GRASS

    def test_shield(self):
        assert cell_from_char("A", 0, 0) == GridCell.SHIELD

    def test_switch_char(self):
        assert cell_from_char("^", 0, 0) == GridCell.SWITCH

    def test_gate_char(self):
        assert cell_from_char("|", 0, 0) == GridCell.GATE

    def test_unknown_char_raises(self):
        with pytest.raises(InvalidMapFileException):
            cell_from_char("Z", 0, 0)


# ==================================================
# Tests : map_from_string
# ==================================================

class TestMapFromString:

    def test_basic_map_loads(self):
        game_map = make_map("P  ", 3, 1)
        assert game_map.width == 3
        assert game_map.height == 1

    def test_player_start_position(self):
        game_map = make_map(" P ", 3, 1)
        assert game_map.player_start_x == 1
        assert game_map.player_start_y == 0

    def test_player_start_bottom_left(self):
        game_map = make_map("P  \n   \n   ", 3, 3)
        assert game_map.player_start_x == 0
        assert game_map.player_start_y == 0

    def test_missing_player_raises(self):
        with pytest.raises(InvalidMapFileException):
            make_map("   ", 3, 1)

    def test_duplicate_player_raises(self):
        with pytest.raises(InvalidMapFileException):
            make_map("PPP", 3, 1)

    def test_wrong_width_raises(self):
        with pytest.raises(InvalidMapFileException):
            make_map("P  ", 5, 1)

    def test_wrong_height_raises(self):
        with pytest.raises(InvalidMapFileException):
            make_map("P  ", 3, 3)

    def test_missing_separator_raises(self):
        with pytest.raises(InvalidMapFileException):
            map_from_string("width: 3\nheight: 1\nP  ")

    def test_cell_types_are_correct(self):
        game_map = make_map("P x*", 4, 1)
        assert game_map.get(0, 0) == GridCell.GRASS
        assert game_map.get(1, 0) == GridCell.GRASS
        assert game_map.get(2, 0) == GridCell.BUSH
        assert game_map.get(3, 0) == GridCell.CRYSTAL

    def test_map_get_out_of_bounds_raises(self):
        game_map = make_map("P  ", 3, 1)
        with pytest.raises(ValueError):
            game_map.get(-1, 0)
        with pytest.raises(ValueError):
            game_map.get(3, 0)

    def test_map_get_negative_y_raises(self):
        game_map = make_map("P  ", 3, 1)
        with pytest.raises(ValueError):
            game_map.get(0, -1)


# ==================================================
# Tests : GateConditions
# ==================================================

class TestGateConditions:

    def test_switch_is_on_true(self):
        assert SwitchIsOn("s1").evaluate({"s1": True}) is True

    def test_switch_is_on_false(self):
        assert SwitchIsOn("s1").evaluate({"s1": False}) is False

    def test_switch_is_on_unknown_raises(self):
        with pytest.raises(InvalidMapFileException):
            SwitchIsOn("unknown").evaluate({"s1": True})

    def test_not_true_gives_false(self):
        assert NotCondition(SwitchIsOn("s1")).evaluate({"s1": True}) is False

    def test_not_false_gives_true(self):
        assert NotCondition(SwitchIsOn("s1")).evaluate({"s1": False}) is True

    def test_and_both_true(self):
        cond = AndCondition(SwitchIsOn("s1"), SwitchIsOn("s2"))
        assert cond.evaluate({"s1": True, "s2": True}) is True

    def test_and_one_false(self):
        cond = AndCondition(SwitchIsOn("s1"), SwitchIsOn("s2"))
        assert cond.evaluate({"s1": True, "s2": False}) is False

    def test_or_one_true(self):
        cond = OrCondition(SwitchIsOn("s1"), SwitchIsOn("s2"))
        assert cond.evaluate({"s1": False, "s2": True}) is True

    def test_or_both_false(self):
        cond = OrCondition(SwitchIsOn("s1"), SwitchIsOn("s2"))
        assert cond.evaluate({"s1": False, "s2": False}) is False

    def test_nested_conditions(self):
        # (s1 AND s2) OR (NOT s3)
        cond = OrCondition(
            AndCondition(SwitchIsOn("s1"), SwitchIsOn("s2")),
            NotCondition(SwitchIsOn("s3")),
        )
        assert cond.evaluate({"s1": True,  "s2": True,  "s3": True})  is True
        assert cond.evaluate({"s1": False, "s2": True,  "s3": True})  is False
        assert cond.evaluate({"s1": False, "s2": False, "s3": False}) is True


# ==================================================
# Tests : Switch et Gate
# ==================================================

class TestSwitch:

    def _sw(self, is_on=False) -> Switch:
        return Switch("s1", 0, 0, is_on=is_on, is_being_hit=False)

    def test_toggle_off_to_on(self):
        s = self._sw(is_on=False)
        toggle_switch(s)
        assert s.is_on is True

    def test_toggle_on_to_off(self):
        s = self._sw(is_on=True)
        toggle_switch(s)
        assert s.is_on is False

    def test_toggle_twice_returns_to_original(self):
        s = self._sw(is_on=True)
        toggle_switch(s)
        toggle_switch(s)
        assert s.is_on is True

    def test_switch_states_reflects_all(self):
        switches = [
            Switch("s1", 0, 0, is_on=True,  is_being_hit=False),
            Switch("s2", 1, 0, is_on=False, is_being_hit=False),
        ]
        assert switch_states(switches) == {"s1": True, "s2": False}

    def test_switch_states_empty_list(self):
        assert switch_states([]) == {}


class TestGate:

    def _gate(self, is_open: bool) -> Gate:
        return Gate(x=0, y=0, open_if=SwitchIsOn("s1"), is_open=is_open)

    def test_gate_opens_when_switch_on(self):
        switches = [Switch("s1", 0, 0, is_on=True, is_being_hit=False)]
        gates = [self._gate(is_open=False)]
        update_gates(switches, gates)
        assert gates[0].is_open is True

    def test_gate_closes_when_switch_off(self):
        switches = [Switch("s1", 0, 0, is_on=False, is_being_hit=False)]
        gates = [self._gate(is_open=True)]
        update_gates(switches, gates)
        assert gates[0].is_open is False

    def test_toggle_then_update_opens_gate(self):
        """Scénario complet : on touche le switch, la gate s'ouvre."""
        switch = Switch("s1", 0, 0, is_on=False, is_being_hit=False)
        gate = self._gate(is_open=False)
        toggle_switch(switch)
        update_gates([switch], [gate])
        assert gate.is_open is True

    def test_multiple_gates_updated_independently(self):
        s1 = Switch("s1", 0, 0, is_on=True,  is_being_hit=False)
        s2 = Switch("s2", 1, 0, is_on=False, is_being_hit=False)
        g1 = Gate(x=0, y=1, open_if=SwitchIsOn("s1"), is_open=False)
        g2 = Gate(x=1, y=1, open_if=SwitchIsOn("s2"), is_open=True)
        update_gates([s1, s2], [g1, g2])
        assert g1.is_open is True
        assert g2.is_open is False


# ==================================================
# Tests : Player
# ==================================================

class TestPlayer:
    """
    Teste la logique pure de Player (take_damage, shield, invincibilité).
    On instancie Player.__new__ pour court-circuiter arcade.TextureAnimationSprite.
    """

    def test_take_damage_reduces_health_by_one(self):
        p = make_player()
        initial = p.health
        result = p.take_damage()
        assert result is True
        assert p.health == initial - 1

    def test_take_damage_returns_false_when_invincible(self):
        p = make_player()
        p.invincibility_time = 1.0
        result = p.take_damage()
        assert result is False
        assert p.health == PLAYER_MAX_HEALTH  # aucune vie perdue

    def test_shield_absorbs_damage_no_health_lost(self):
        p = make_player()
        p.shield_time = SHIELD_DURATION
        result = p.take_damage()
        assert result is False
        assert p.health == PLAYER_MAX_HEALTH

    def test_shield_consumed_after_hit(self):
        p = make_player()
        p.shield_time = SHIELD_DURATION
        p.take_damage()
        assert p.shield_time == 0.0

    def test_shield_grants_invincibility_after_absorb(self):
        p = make_player()
        p.shield_time = SHIELD_DURATION
        p.take_damage()
        assert p.invincibility_time == PLAYER_INVINCIBILITY_DURATION

    def test_damage_sets_invincibility(self):
        p = make_player()
        p.take_damage()
        assert p.invincibility_time == PLAYER_INVINCIBILITY_DURATION

    def test_health_cannot_go_below_zero(self):
        p = make_player()
        p.health = 1
        p.take_damage()
        # on court-circuite l'invincibilité pour tester le plancher
        p.invincibility_time = 0.0
        p.take_damage()
        assert p.health == 0

    def test_activate_shield_sets_shield_time(self):
        p = make_player()
        p.activate_shield()
        assert p.shield_time == SHIELD_DURATION
        assert p.has_active_shield() is True

    def test_is_invincible_false_at_start(self):
        p = make_player()
        assert p.is_invincible() is False

    def test_update_invincibility_decreases_over_time(self):
        p = make_player()
        p.invincibility_time = 1.0
        p.update_invincibility(0.3)
        assert abs(p.invincibility_time - 0.7) < 1e-9

    def test_update_invincibility_does_not_go_negative(self):
        p = make_player()
        p.invincibility_time = 0.1
        p.update_invincibility(999.0)
        assert p.invincibility_time == 0.0

    def test_update_shield_decreases_over_time(self):
        p = make_player()
        p.shield_time = 3.0
        p.update_shield(1.0)
        assert abs(p.shield_time - 2.0) < 1e-9

    def test_update_shield_does_not_go_negative(self):
        p = make_player()
        p.shield_time = 0.5
        p.update_shield(999.0)
        assert p.shield_time == 0.0

    def test_movement_right(self):
        p = make_player()
        p.update_movement(right=True, left=False, up=False, down=False)
        assert p.change_x > 0
        assert p.change_y == 0

    def test_movement_opposite_keys_cancel(self):
        p = make_player()
        p.update_movement(right=True, left=True, up=False, down=False)
        assert p.change_x == 0

    def test_direction_updates_on_movement(self):
        p = make_player()
        p.update_movement(right=False, left=False, up=True, down=False)
        assert p.direction == Direction.NORTH


# ==================================================
# Tests : Navmesh
# ==================================================

class TestNavmesh:

    def _map3x3(self) -> Map:
        return make_map("   \n P \n   ", 3, 3)

    def test_navmesh_creates_nodes_for_all_grass(self):
        from navmesh import create_navmesh
        navmesh = create_navmesh(self._map3x3())
        assert len(navmesh.graph.nodes) == 9

    def test_navmesh_bush_excluded(self):
        from navmesh import create_navmesh
        game_map = make_map("PxP", 3, 1)
        navmesh = create_navmesh(game_map)
        assert (1, 0) not in navmesh.graph.nodes

    def test_navmesh_hole_excluded(self):
        from navmesh import create_navmesh
        game_map = make_map("POP", 3, 1)
        navmesh = create_navmesh(game_map)
        assert (1, 0) not in navmesh.graph.nodes

    def test_shortest_path_finds_route(self):
        from navmesh import create_navmesh, shortest_path
        navmesh = create_navmesh(self._map3x3())
        path = shortest_path(navmesh, (grid_to_pixels(0), grid_to_pixels(0)),
                                      (grid_to_pixels(2), grid_to_pixels(2)))
        assert len(path) > 0

    def test_shortest_path_same_source_and_target(self):
        from navmesh import create_navmesh, shortest_path
        navmesh = create_navmesh(self._map3x3())
        pt = (grid_to_pixels(1), grid_to_pixels(1))
        path = shortest_path(navmesh, pt, pt)
        assert len(path) >= 1

    def test_shortest_path_empty_graph_returns_target(self):
        from navmesh import NavMesh, shortest_path
        import networkx as nx
        navmesh = NavMesh(graph=nx.Graph())
        target = (100.0, 100.0)
        path = shortest_path(navmesh, (0.0, 0.0), target)
        assert path == [target]

    def test_navmesh_edges_connect_neighbours(self):
        from navmesh import create_navmesh
        navmesh = create_navmesh(self._map3x3())
        # (0,0) et (1,0) doivent être connectés
        assert navmesh.graph.has_edge((0, 0), (1, 0))

    def test_diagonal_edges_exist(self):
        from navmesh import create_navmesh
        navmesh = create_navmesh(self._map3x3())
        assert navmesh.graph.has_edge((0, 0), (1, 1))


# ==================================================
# Tests : utils
# ==================================================

class TestUtils:

    def test_grid_to_pixels_zero_is_half_tile(self):
        assert grid_to_pixels(0) == TILE_SIZE // 2

    def test_grid_to_pixels_is_strictly_increasing(self):
        assert grid_to_pixels(1) > grid_to_pixels(0)
        assert grid_to_pixels(2) > grid_to_pixels(1)

    def test_grid_to_pixels_step_is_tile_size(self):
        assert grid_to_pixels(1) - grid_to_pixels(0) == TILE_SIZE

    def test_grid_to_pixels_negative_index(self):
        assert grid_to_pixels(-1) < grid_to_pixels(0)

    def test_find_cells_returns_correct_position(self):
        game_map = make_map("P*x", 3, 1)
        crystals = find_cells(game_map, GridCell.CRYSTAL)
        assert (1, 0) in crystals

    def test_find_cells_returns_only_matching_type(self):
        game_map = make_map("P*x", 3, 1)
        crystals = find_cells(game_map, GridCell.CRYSTAL)
        assert len(crystals) == 1

    def test_find_cells_empty_when_none_present(self):
        game_map = make_map("P  ", 3, 1)
        assert find_cells(game_map, GridCell.CRYSTAL) == []

    def test_find_cells_multiple_occurrences(self):
        game_map = make_map("P***", 4, 1)
        crystals = find_cells(game_map, GridCell.CRYSTAL)
        assert len(crystals) == 3
        assert (1, 0) in crystals and (2, 0) in crystals and (3, 0) in crystals

    def test_find_cells_multiple_rows(self):
        game_map = make_map("P  \n * \n   ", 3, 3)
        crystals = find_cells(game_map, GridCell.CRYSTAL)
        assert (1, 1) in crystals and len(crystals) == 1


# ==================================================
# Tests : Spinner
# ==================================================

class TestSpinner:

    def test_moves_right_when_direction_positive(self):
        s = make_spinner(x=5, horizontal=True, min_x=3, max_x=7)
        initial_x = s.logic_x
        s.update_logic()
        assert s.logic_x > initial_x

    def test_reverses_at_max_x(self):
        s = make_spinner(horizontal=True, min_x=3, max_x=5)
        s.logic_x = s.max_x  # déjà au bord
        s.update_logic()
        assert s.direction == -1

    def test_reverses_at_min_x(self):
        s = make_spinner(horizontal=True, min_x=5, max_x=7)
        s.logic_x = s.min_x
        s.direction = -1
        s.update_logic()
        assert s.direction == 1

    def test_vertical_moves_up_when_direction_positive(self):
        s = make_spinner(x=5, y=5, horizontal=False, min_x=5, max_x=5, min_y=3, max_y=7)
        initial_y = s.logic_y
        s.update_logic()
        assert s.logic_y > initial_y

    def test_stays_within_bounds_after_overshoot(self):
        s = make_spinner(horizontal=True, min_x=3, max_x=5)
        s.logic_x = s.max_x + 1  # dépasse volontairement
        s.update_logic()
        assert s.logic_x <= s.max_x

    def test_is_blocking_cell_bush(self):
        assert _is_blocking_cell(GridCell.BUSH) is True

    def test_is_blocking_cell_grass_not_blocking(self):
        assert _is_blocking_cell(GridCell.GRASS) is False

    def test_scan_until_blocked_stops_at_wall(self):
        game_map = make_map("PxS", 3, 1)
        # scan vers la droite depuis (0,0) : s'arrête avant x=1 (bush)
        result_x, result_y = _scan_until_blocked(game_map, 0, 0, dx=1, dy=0)
        assert result_x == 0  # ne passe pas le buisson

    def test_create_spinners_horizontal_finds_bounds(self):
        game_map = make_map("Ps ", 3, 1)
        spinners = create_spinners(game_map)
        assert len(spinners) == 1
        assert spinners[0].horizontal is True


# ==================================================
# Tests : Bat
# ==================================================

class TestBat:

    def test_bat_moves_each_frame(self):
        b = make_bat(start_x=100.0, start_y=100.0, dx=2.0, dy=3.0)
        b.update_logic()
        assert b.logic_x == 102.0
        assert b.logic_y == 103.0

    def test_bat_bounces_at_max_x(self):
        b = make_bat(start_x=198.0, dx=5.0, max_x=200)
        b.update_logic()
        assert b.dx < 0  # direction inversée

    def test_bat_bounces_at_min_x(self):
        b = make_bat(start_x=52.0, dx=-5.0, min_x=50)
        b.update_logic()
        assert b.dx > 0

    def test_bat_bounces_at_max_y(self):
        b = make_bat(start_y=198.0, dy=5.0, max_y=200)
        b.update_logic()
        assert b.dy < 0

    def test_bat_clamped_within_bounds_after_bounce(self):
        b = make_bat(start_x=199.0, dx=5.0, min_x=50, max_x=200)
        b.update_logic()
        assert b.logic_x <= b.max_x

    def test_clamp_below_min(self):
        assert _clamp(3, 5, 10) == 5

    def test_clamp_above_max(self):
        assert _clamp(15, 5, 10) == 10

    def test_clamp_within_range(self):
        assert _clamp(7, 5, 10) == 7

    def test_compute_bat_bounds_within_map(self):
        game_map = make_map("P" + " " * 9, 10, 1)
        min_x, max_x, min_y, max_y = _compute_bat_bounds(game_map, 5, 0)
        assert min_x < max_x


# ==================================================
# Tests : Slime
# ==================================================

from slime import (
    Slime,
    _is_slime_obstacle,
    _can_stand_on,
    _patrol_destinations,
)
from constants import SLIME_SPEED, DESTINATION_EPSILON, MAX_VIEW_DISTANCE


def make_slime(lx=100.0, ly=100.0, dest_x=200.0, dest_y=100.0) -> Slime:
    """Crée un Slime sans passer par arcade."""
    s = Slime.__new__(Slime)
    s.start_x = 0
    s.start_y = 0
    s.logic_x = lx
    s.logic_y = ly
    s.destination_x = dest_x
    s.destination_y = dest_y
    s.possible_destinations = [(0, 0), (1, 0), (0, 1)]
    s.current_path = []
    s.current_path_index = 0
    return s


class TestSlime:

    # --- _is_slime_obstacle ---

    def test_bush_is_obstacle(self):
        assert _is_slime_obstacle(GridCell.BUSH) is True

    def test_hole_is_obstacle(self):
        assert _is_slime_obstacle(GridCell.HOLE) is True

    def test_grass_is_not_obstacle(self):
        assert _is_slime_obstacle(GridCell.GRASS) is False

    def test_crystal_is_not_obstacle(self):
        assert _is_slime_obstacle(GridCell.CRYSTAL) is False

    # --- _can_stand_on ---

    def test_can_stand_on_grass(self):
        game_map = make_map("P  ", 3, 1)
        assert _can_stand_on(game_map, 1, 0) is True

    def test_cannot_stand_on_bush(self):
        game_map = make_map("Px ", 3, 1)
        assert _can_stand_on(game_map, 1, 0) is False

    def test_cannot_stand_outside_map(self):
        game_map = make_map("P  ", 3, 1)
        assert _can_stand_on(game_map, -1, 0) is False
        assert _can_stand_on(game_map, 3, 0) is False

    # --- _patrol_destinations ---

    def test_patrol_destinations_excludes_walls(self):
        # Map 3x3, slime au centre (1,1), buisson en (0,0)
        game_map = make_map("x  \n P \n   ", 3, 3)
        dests = _patrol_destinations(game_map, 1, 1)
        assert (0, 0) not in dests

    def test_patrol_destinations_excludes_out_of_bounds(self):
        # Slime dans un coin : les destinations hors map ne doivent pas apparaître
        game_map = make_map("P  \n   \n   ", 3, 3)
        dests = _patrol_destinations(game_map, 0, 0)
        assert all(0 <= x < 3 and 0 <= y < 3 for x, y in dests)

    def test_patrol_destinations_includes_start(self):
        game_map = make_map("P  \n   \n   ", 3, 3)
        dests = _patrol_destinations(game_map, 1, 1)
        assert (1, 1) in dests

    # --- _move_directly_to ---

    def test_move_directly_advances_toward_target(self):
        s = make_slime(lx=0.0, ly=0.0)
        target = (100.0, 0.0)
        s._move_directly_to(target)
        assert s.logic_x > 0.0
        assert s.logic_y == 0.0

    def test_move_directly_does_not_overshoot(self):
        """Un slime à epsilon du but ne doit pas bouger."""
        s = make_slime(lx=0.0, ly=0.0)
        target = (DESTINATION_EPSILON / 2, 0.0)
        s._move_directly_to(target)
        assert s.logic_x == 0.0  # trop proche → ne bouge pas

    def test_move_directly_diagonal(self):
        s = make_slime(lx=0.0, ly=0.0)
        target = (100.0, 100.0)
        s._move_directly_to(target)
        # Les deux composantes doivent avancer
        assert s.logic_x > 0.0
        assert s.logic_y > 0.0

    # --- _has_reached_destination ---

    def test_has_reached_destination_true(self):
        s = make_slime(lx=100.0, ly=100.0, dest_x=100.0, dest_y=100.0)
        assert s._has_reached_destination() is True

    def test_has_reached_destination_false(self):
        s = make_slime(lx=0.0, ly=0.0, dest_x=500.0, dest_y=0.0)
        assert s._has_reached_destination() is False

    # --- _can_see_player ---

    def test_cannot_see_player_too_far(self):
        s = make_slime(lx=0.0, ly=0.0)
        far_player = (MAX_VIEW_DISTANCE + 999.0, 0.0)
        walls = MagicMock()
        assert s._can_see_player(far_player, walls) is False

    def test_can_see_player_when_close_and_los(self):
        s = make_slime(lx=0.0, ly=0.0)
        close_player = (50.0, 0.0)
        walls = MagicMock()
        _arcade_mock.has_line_of_sight.return_value = True
        assert s._can_see_player(close_player, walls) is True

    # --- _follow_current_path ---

    def test_follow_path_advances_toward_first_waypoint(self):
        s = make_slime(lx=0.0, ly=0.0)
        s.current_path = [(200.0, 0.0)]
        s.current_path_index = 0
        s._follow_current_path()
        assert s.logic_x > 0.0

    def test_follow_path_advances_index_when_waypoint_reached(self):
        s = make_slime(lx=0.0, ly=0.0)
        # Premier waypoint au même endroit → doit passer au suivant
        s.current_path = [(0.0, 0.0), (200.0, 0.0)]
        s.current_path_index = 0
        s._follow_current_path()
        assert s.current_path_index == 1

    def test_follow_empty_path_does_nothing(self):
        s = make_slime(lx=50.0, ly=50.0)
        s.current_path = []
        s._follow_current_path()
        assert s.logic_x == 50.0
        assert s.logic_y == 50.0


# ==================================================
# Tests : Boomerang
# ==================================================

from boomerang import Boomerang, BoomerangState


def make_boomerang() -> Boomerang:
    b = Boomerang.__new__(Boomerang)
    b.state = BoomerangState.INACTIVE
    b.distance_travelled = 0.0
    b.direction = Direction.EAST
    b.center_x = 0.0
    b.center_y = 0.0
    return b


class TestBoomerang:

    def test_initial_state_is_inactive(self):
        b = make_boomerang()
        assert b.state == BoomerangState.INACTIVE
        assert b.is_active() is False

    def test_launch_sets_launching_state(self):
        b = make_boomerang()
        b.launch(Direction.EAST, 100.0, 200.0)
        assert b.state == BoomerangState.LAUNCHING
        assert b.is_active() is True

    def test_launch_sets_position(self):
        b = make_boomerang()
        b.launch(Direction.NORTH, 50.0, 75.0)
        assert b.center_x == 50.0
        assert b.center_y == 75.0

    def test_launch_resets_distance(self):
        b = make_boomerang()
        b.distance_travelled = 999.0
        b.launch(Direction.WEST, 0.0, 0.0)
        assert b.distance_travelled == 0.0

    def test_return_to_player_sets_returning_state(self):
        b = make_boomerang()
        b.launch(Direction.EAST, 0.0, 0.0)
        b.return_to_player()
        assert b.state == BoomerangState.RETURNING
        assert b.is_active() is True

    def test_deactivate_sets_inactive(self):
        b = make_boomerang()
        b.launch(Direction.EAST, 0.0, 0.0)
        b.deactivate()
        assert b.state == BoomerangState.INACTIVE
        assert b.is_active() is False

    def test_deactivate_resets_distance(self):
        b = make_boomerang()
        b.distance_travelled = 500.0
        b.deactivate()
        assert b.distance_travelled == 0.0

    def test_full_lifecycle(self):
        """INACTIVE → LAUNCHING → RETURNING → INACTIVE."""
        b = make_boomerang()
        assert b.state == BoomerangState.INACTIVE
        b.launch(Direction.SOUTH, 0.0, 0.0)
        assert b.state == BoomerangState.LAUNCHING
        b.return_to_player()
        assert b.state == BoomerangState.RETURNING
        b.deactivate()
        assert b.state == BoomerangState.INACTIVE


# ==================================================
# Tests : Sword
# ==================================================

from sword import Sword, SwordState


def make_sword() -> Sword:
    s = Sword.__new__(Sword)
    s.state = SwordState.INACTIVE
    s.time = 0.0
    s.direction = Direction.SOUTH
    s.animation = MagicMock()
    return s


class TestSword:

    def test_initial_state_is_inactive(self):
        s = make_sword()
        assert s.state == SwordState.INACTIVE
        assert s.is_active() is False

    def test_activate_sets_active_state(self):
        s = make_sword()
        s.activate(Direction.NORTH)
        assert s.state == SwordState.ACTIVE
        assert s.is_active() is True

    def test_activate_sets_direction(self):
        s = make_sword()
        s.activate(Direction.WEST)
        assert s.direction == Direction.WEST

    def test_activate_resets_time(self):
        s = make_sword()
        s.time = 9.9
        s.activate(Direction.EAST)
        assert s.time == 0.0

    def test_deactivate_sets_inactive(self):
        s = make_sword()
        s.activate(Direction.SOUTH)
        s.deactivate()
        assert s.state == SwordState.INACTIVE
        assert s.is_active() is False

    def test_deactivate_resets_time(self):
        s = make_sword()
        s.time = 0.2
        s.deactivate()
        assert s.time == 0.0

    def test_activate_each_direction(self):
        """L'épée peut être activée dans chacune des 4 directions."""
        for direction in Direction:
            s = make_sword()
            s.activate(direction)
            assert s.direction == direction
            assert s.is_active() is True

    def test_full_lifecycle(self):
        """INACTIVE → ACTIVE → INACTIVE."""
        s = make_sword()
        assert not s.is_active()
        s.activate(Direction.EAST)
        assert s.is_active()
        s.deactivate()
        assert not s.is_active()