from __future__ import annotations
from constants import TILE_SIZE

from dataclasses import dataclass
import math

import networkx as nx

from map import GridCell, Map
from utils import grid_to_pixels


# Un noeud du navmesh est une case de la grille.
Node = tuple[int, int]

# Un point en pixels.
Point = tuple[float, float]

FINESSE=3

@dataclass
class NavMesh:
    # le graphe contient les cases accessibles aux slimes.
    graph: nx.Graph[Node]


def node_position(node: Node) -> Point:
    """avant d'introduire la finesse, on se contentait d'utiliser grid_to_pixels,
    mais là on doit positionner le noeud au centre de la nouvelle sous-case dans
    la nouvelle grille 3 fois plus fine que la map"""
    x, y = node
    #on est contraint d'ajouter le 0.5 pour se positionner au centre de la sous-case
    #càd on rajoute la moitié de "mini_TILE_SIZE" qui est égale à TILE_SIZE/FINESSE
    return (
        (x+0.5)*TILE_SIZE/FINESSE,
        (y+0.5)*TILE_SIZE/FINESSE
    )


def distance_between_points(p1: Point, p2: Point) -> float:
    # Distance euclidienne entre deux points.
    x1, y1 = p1
    x2, y2 = p2
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def is_inside_map(game_map: Map, x: int, y: int) -> bool:
    return 0 <= x < game_map.width and 0 <= y < game_map.height


def is_slime_obstacle(cell: GridCell) -> bool:
    """les slimes ne peuvent pas marcher sur certains obstacles
    c'est ce qu'on vérifie ici: """
    return cell in {
        GridCell.BUSH,
        GridCell.HOLE,
        GridCell.GATE,
    }

def _is_too_close_to_bush(position: Point, map: Map) -> bool:
        """check si on est trop prche d'un buisson de la map en parcourant celle-ci,
        en récupérant la posiion des buissons et en calculant sa distance au point."""
        for y in range(map.height):
            for x in range(map.width):
                if map.get(x, y) == GridCell.BUSH:
                    bush_center = (grid_to_pixels(x), grid_to_pixels(y))

                    if distance_between_points(position, bush_center) < TILE_SIZE:
                        return True
        return False

def can_slime_stand_on(game_map: Map, x: int, y: int) -> bool:
    # Une case devient un noeud du navmesh si le slime peut marcher dessus.
    if not is_inside_map(game_map, x, y):
        #on vérifie si on est à l'intérieur de la map
        return False
        #si on l'est, alors on vérifie si c'est un obstacle
    return not is_slime_obstacle(game_map.get(x, y))


def add_navmesh_nodes(game_map: Map, graph: nx.Graph[Node]) -> None:
    #on ajoute un noeud pour chaque case accessible:
    for y in range(game_map.height):
        for x in range(game_map.width):
            #on regarde ce qu'il y'a dans la case, voir si le slime peut s'y trouver
            if can_slime_stand_on(game_map, x, y):
                #on peut s'y positionner, on doit créer les noeuds
                #comme on est sur une case ou il y'a FINESS**2 noeuds, on procède comme suit :
                for mini_y in range(FINESSE):
                    for mini_x in range(FINESSE):
                        #noeud:
                        node=(mini_x+x*FINESSE,mini_y+y*FINESSE)
                        #la finesse ajoutée oblige à multiplier par FINESSE justement
                        point=node_position(node)
                        #on regarde les coordonnées de ce noeud en pixels, voir s'il est trop proche
                        #d'un obstacle:
                        if not _is_too_close_to_bush(point, game_map):
                            graph.add_node(node)


def neighbor_nodes(node: Node) -> list[Node]:
    """chaque noeud possède au plus 8 voisins, soit en verticale, horizontale ou diagonale
    les coordonnées varient donc de +-1 ou 0, et ce même après l'ajout de la finesse."""
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
    """on ajute les arêtes en tenan compte bien sur des poids de chacune d'elle,
    pour cela on a bien défini notre fonction distance_between_points"""
    for node in graph.nodes:
        for neighbor in neighbor_nodes(node):
            if neighbor in graph:
                weight = distance_between_points(
                    node_position(node),
                    node_position(neighbor),
                )
                graph.add_edge(node, neighbor, weight=weight)


def create_navmesh(game_map: Map) -> NavMesh:
    """on crée le navmesh complet"""
    graph: nx.Graph[Node] = nx.Graph()
    add_navmesh_nodes(game_map, graph)
    add_navmesh_edges(graph)
    return NavMesh(graph=graph)


def nearest_node(navmesh: NavMesh, point: Point) -> Node:
    """cette fonction est essentielle à l'algorithme de dijkstra, car elle
    retourne le noeud du navmesh le plus proche d'un point"""
    return min(
        navmesh.graph.nodes,
        key=lambda node: distance_between_points(point, node_position(node)),
    )


def shortest_path(navmesh: NavMesh, source: Point, target: Point) -> list[Point]:
    """ trouve le chemin le moins couteux en 4 étapes :
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
