from __future__ import annotations
from constants import TILE_SIZE

from dataclasses import dataclass
import math

import networkx as nx

from map import GridCell, Map
from utils import grid_to_pixels

Node = tuple[int, int]
Point = tuple[float, float]
# on a fait la distinction entre un point en pixels et un noeud du graphe.

# FINESSE : nombre de noeuds par côté de cellule (doit être un entier impair).
# 1 → 1 noeud/cellule (ancien comportement)
# 3 → 9 noeuds/cellule (nouveau comportement)
FINESSE = 3


@dataclass
class NavMesh:
    graph: nx.Graph[Node]


def node_position(node: Node) -> Point:
    """positionne le noeud au centre de sa sous-case dans la grille FINESSE fois plus fine.
    La formule générale pour n×n noeuds par cellule est (2i+1)*s/(2n),
    ce qui donne, pour FINESSE=3 : s/6, 3s/6 (=centre), 5s/6."""
    x, y = node
    # (2*x + 1) * TILE_SIZE / (2 * FINESSE)  — formule générale
    return (
        (2 * x + 1) * TILE_SIZE / (2 * FINESSE),
        (2 * y + 1) * TILE_SIZE / (2 * FINESSE),
    )


def distance_between_points(p1: Point, p2: Point) -> float:
    x1, y1 = p1
    x2, y2 = p2
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def is_inside_map(game_map: Map, x: int, y: int) -> bool:
    return 0 <= x < game_map.width and 0 <= y < game_map.height


def is_slime_obstacle(cell: GridCell) -> bool:
    """les slimes ne peuvent pas marcher sur les trous et buissons."""
    return cell in {
        GridCell.BUSH,
        GridCell.HOLE,
    }


def _is_too_close_to_bush(position: Point, game_map: Map) -> bool:
    """vérifie si le point est à moins d'une TILE_SIZE d'un buisson.
    On exclut les noeuds trop proches des buissons pour éviter que les slimes
    rasent les obstacles en diagonale."""
    for y in range(game_map.height):
        for x in range(game_map.width):
            if game_map.get(x, y) == GridCell.BUSH:
                bush_center = (grid_to_pixels(x), grid_to_pixels(y))
                if distance_between_points(position, bush_center) < TILE_SIZE:
                    return True
    return False


def can_slime_stand_on(game_map: Map, x: int, y: int) -> bool:
    """renvoie True si la cellule (x, y) est accessible pour un slime."""
    if not is_inside_map(game_map, x, y):
        return False
    return not is_slime_obstacle(game_map.get(x, y))


def add_navmesh_nodes(game_map: Map, graph: nx.Graph[Node]) -> None:
    """crée FINESSE×FINESSE noeuds par cellule accessible.
    Pour chaque sous-noeud, on vérifie en plus qu'il n'est pas trop près
    d'un buisson (les trous sont autorisés, on peut longer les bords)."""
    for y in range(game_map.height):
        for x in range(game_map.width):
            if can_slime_stand_on(game_map, x, y):
                for mini_y in range(FINESSE):
                    for mini_x in range(FINESSE):
                        node: Node = (x * FINESSE + mini_x, y * FINESSE + mini_y)
                        point = node_position(node)
                        if not _is_too_close_to_bush(point, game_map):
                            graph.add_node(node)


def neighbor_nodes(node: Node) -> list[Node]:
    """chaque noeud possède au plus 8 voisins (4-connexité + diagonales).
    Les coordonnées varient de ±1 ou 0 — identique avant et après l'ajout de la finesse."""
    x, y = node
    return [
        (x - 1, y - 1),
        (x,     y - 1),
        (x + 1, y - 1),
        (x - 1, y    ),
        (x + 1, y    ),
        (x - 1, y + 1),
        (x,     y + 1),
        (x + 1, y + 1),
    ]


def add_navmesh_edges(graph: nx.Graph[Node]) -> None:
    """ajoute les arêtes pondérées par la distance euclidienne réelle en pixels."""
    for node in graph.nodes:
        for neighbor in neighbor_nodes(node):
            if neighbor in graph:
                weight = distance_between_points(
                    node_position(node),
                    node_position(neighbor),
                )
                graph.add_edge(node, neighbor, weight=weight)


def create_navmesh(game_map: Map) -> NavMesh:
    graph: nx.Graph[Node] = nx.Graph()
    add_navmesh_nodes(game_map, graph)
    add_navmesh_edges(graph)
    return NavMesh(graph=graph)


def nearest_node(navmesh: NavMesh, point: Point) -> Node:
    """retourne le noeud du navmesh le plus proche d'un point en pixels."""
    return min(
        navmesh.graph.nodes,
        key=lambda node: distance_between_points(point, node_position(node)),
    )


def shortest_path(navmesh: NavMesh, source: Point, target: Point) -> list[Point]:
    """trouve le chemin le moins coûteux en 4 étapes :
    1. depuis la source, on trouve le noeud le plus proche
    2. on trouve le noeud le plus proche de la destination
    3. Dijkstra entre ces deux noeuds
    4. conversion des noeuds en points pixels"""

    if len(navmesh.graph.nodes) == 0:
        return [target]

    source_node = nearest_node(navmesh, source)
    target_node = nearest_node(navmesh, target)

    try:
        path_nodes = nx.shortest_path(
            navmesh.graph,
            source=source_node,
            target=target_node,
            weight="weight",
        )
    except nx.NetworkXNoPath:
        return [target]

    path_points = [node_position(node) for node in path_nodes]

    # On ajoute la vraie destination à la fin.
    # Comme ça, le slime arrive exactement là où il voulait aller.
    path_points.append(target)

    return path_points