from __future__ import annotations

from dataclasses import dataclass
import math

import networkx as nx

from map import GridCell, Map
from utils import grid_to_pixels


# Un noeud du navmesh est une case de la grille.
# Exemple : (4, 7)
#
# On choisit tuple[int, int] parce que :
# - c'est simple
# - c'est hashable
# - NetworkX peut l'utiliser comme noeud
Node = tuple[int, int]

# Un point en pixels.
# Exemple : (144.0, 240.0)
Point = tuple[float, float]


@dataclass
class NavMesh:
    # Le graphe contient les cases accessibles aux slimes.
    graph: nx.Graph[Node]


def node_position(node: Node) -> Point:
    # Donne la position en pixels du centre d'un noeud.
    x, y = node
    return (grid_to_pixels(x), grid_to_pixels(y))


def distance_between_points(p1: Point, p2: Point) -> float:
    # Distance euclidienne entre deux points.
    x1, y1 = p1
    x2, y2 = p2
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def is_inside_map(game_map: Map, x: int, y: int) -> bool:
    return 0 <= x < game_map.width and 0 <= y < game_map.height


def is_slime_obstacle(cell: GridCell) -> bool:
    # Les slimes ne peuvent pas marcher sur :
    # - les buissons
    # - les trous
    #
    # Les trous ne bloqueront pas la vue plus tard,
    # mais ils restent des obstacles pour le déplacement.
    return cell in {
        GridCell.BUSH,
        GridCell.HOLE,
        GridCell.GATE,
    }


def can_slime_stand_on(game_map: Map, x: int, y: int) -> bool:
    # Une case devient un noeud du navmesh si le slime peut marcher dessus.
    if not is_inside_map(game_map, x, y):
        return False
    return not is_slime_obstacle(game_map.get(x, y))


def add_navmesh_nodes(game_map: Map, graph: nx.Graph[Node]) -> None:
    # On ajoute un noeud pour chaque case accessible.
    for y in range(game_map.height):
        for x in range(game_map.width):
            if can_slime_stand_on(game_map, x, y):
                graph.add_node((x, y))


def neighbor_nodes(node: Node) -> list[Node]:
    # On connecte chaque noeud avec ses voisins :
    # - horizontaux
    # - verticaux
    # - diagonaux
    #
    # Donc au maximum 8 voisins.
    x, y = node
    return [
        (x - 1, y - 1),
        (x, y - 1),
        (x + 1, y - 1),
        (x - 1, y),
        (x + 1, y),
        (x - 1, y + 1),
        (x, y + 1),
        (x + 1, y + 1),
    ]


def add_navmesh_edges(graph: nx.Graph[Node]) -> None:
    # On ajoute les arêtes entre les noeuds voisins.
    #
    # Le poids est la vraie distance :
    # - horizontal / vertical : TILE_SIZE
    # - diagonale : sqrt(2) * TILE_SIZE
    #
    # C'est important pour que Dijkstra choisisse un vrai plus court chemin.
    for node in graph.nodes:
        for neighbor in neighbor_nodes(node):
            if neighbor in graph:
                weight = distance_between_points(
                    node_position(node),
                    node_position(neighbor),
                )
                graph.add_edge(node, neighbor, weight=weight)


def create_navmesh(game_map: Map) -> NavMesh:
    # Crée le graphe complet du navmesh.
    graph: nx.Graph[Node] = nx.Graph()
    add_navmesh_nodes(game_map, graph)
    add_navmesh_edges(graph)
    return NavMesh(graph=graph)


def nearest_node(navmesh: NavMesh, point: Point) -> Node:
    # Trouve le noeud du navmesh le plus proche d'un point quelconque.
    #
    # Le slime et sa destination sont en pixels.
    # Mais Dijkstra travaille sur des noeuds.
    # Donc on rapproche chaque point du noeud le plus proche.
    return min(
        navmesh.graph.nodes,
        key=lambda node: distance_between_points(point, node_position(node)),
    )


def shortest_path(navmesh: NavMesh, source: Point, target: Point) -> list[Point]:
    # Calcule un chemin entre deux points en pixels.
    #
    # Étapes :
    # 1. source -> noeud le plus proche
    # 2. target -> noeud le plus proche
    # 3. Dijkstra entre ces deux noeuds
    # 4. conversion des noeuds en points pixels

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