from fatalattractors import attractors
import buchi as buchi
import copy

from graph import Graph


def buchi_inter_safety_player(g, u, s, j):
    """
    Solves a Buchi inter safety game where player j has that objective. U is the set to be visited infinitely often
    and s is to be avoided.
    :param g: a game graph.
    :param u: the set od nodes to be visited infinitely often.
    :param s: the set of nodes to be avoid.
    :param j: the player with the Buchi inter safety objective.
    :return: the winning regions w_0, w_1.
    """

    a, not_a = attractors.attractor(g, s, (j + 1) % 2)
    g_reduced = g.subgame(not_a)
    # TODO check if it is required to return both winning regions
    return buchi.buchi_classical_player(g_reduced, u, j)


def buchi_inter_safety(g, u, s):
    """
    Solves a Buchi inter safety game where player 0 has that objective. U is the set to be visited infinitely often
    and s is to be avoided.
    :param g: a game graph.
    :param u: the set od nodes to be visited infinitely often.
    :param s: the set of nodes to be avoid.
    :return: the winning regions w_0, w_1.
    """

    a, not_a = attractors.attractor(g, s, 1)
    g_reduced = g.subgame(not_a)
    return buchi.buchi_classical(g_reduced, u)


def buchi_inter_safety_transformation(g, u, s):
    """
    Solves a Buchi inter safety game where player 0 has that objective. U is the set to be visited infinitely often
    and s is to be avoided. This is solved by creating a new game arena where every node in s is replaced by a sink and
    predecessors have edges leading to that sink. The classical Buchi algorithm is then applied.
    :param g: a game graph.
    :param u: the set od nodes to be visited infinitely often.
    :param s: the set of nodes to be avoid.
    :return: the winning regions w_0, w_1.
    """

    # Work with a copy which we modify
    g_copy = copy.deepcopy(g)  # type: Graph

    # Create the sink
    g_copy.add_node(-1, (0, 0))
    g_copy.add_successor(-1, -1)
    g_copy.add_predecessor(-1, -1)

    for node in s:
        # TODO should we remove predecessors and successors of these nodes
        g_copy.remove_node(node)
        del g_copy.successors[node]
        # delete bad nodes, remove their successors
        # fix their predecessors by removing them from the successors and replace rc by arc to -1
        for prede in g_copy.get_predecessors(node):
            g_copy.successors[prede] = [-1 if k == node else k for k in g_copy.successors[prede]]

    return buchi.buchi_classical(g_copy, u)
