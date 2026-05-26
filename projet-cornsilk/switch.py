from __future__ import annotations

from dataclasses import dataclass

from map import GateCondition, GateConfig, Map, SwitchConfig


@dataclass
class Switch:
    switch_id: str
    x: int
    y: int
    is_on: bool

    """sert à éviter qu'une arme toggle le switch trop de fois par seconde.
    mis à true dès que l'arme touche le switch, remis à false quand elle s'éloigne."""
    is_being_hit: bool


@dataclass
class Gate:
    x: int
    y: int
    open_if: GateCondition
    is_open: bool


def create_switch(config: SwitchConfig) -> Switch:
    return Switch(
        switch_id=config.switch_id,
        x=config.x,
        y=config.y,
        is_on=config.is_on,
        is_being_hit=False,
    )


def create_gate(
    config: GateConfig,
    switch_states: dict[str, bool],
) -> Gate:
    """création du portail, et evalutation pour voir s'il doit etre ouvert"""
    return Gate(
        x=config.x,
        y=config.y,
        open_if=config.open_if,
        is_open=config.open_if.evaluate(switch_states),
    )


def switch_states(switches: list[Switch]) -> dict[str, bool]:
    """on convertit la liste des switch en dictionnaire avec leur nom(id) et état"""
    return {
        switch.switch_id: switch.is_on
        for switch in switches
    }


def create_switches(game_map: Map) -> list[Switch]:
    return [
        create_switch(config)
        for config in game_map.switch_configs
    ]


def create_gates(
    game_map: Map,
    switches: list[Switch],
) -> list[Gate]:
    states = switch_states(switches)

    return [
        create_gate(config, states)
        for config in game_map.gate_configs
    ]


def toggle_switch(switch: Switch) -> None:
    """actualisation de l'état de l'interrupteur"""
    switch.is_on = not switch.is_on


def update_gates(
    switches: list[Switch],
    gates: list[Gate],
) -> None:
    """determine l'état des portails en fonction des switch"""
    states = switch_states(switches)

    for gate in gates:
        gate.is_open = gate.open_if.evaluate(states)
