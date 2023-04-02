import buchi_inter_safety as buchi_inter_safety
from fatalattractors import attractors


def buchi_inter_cobuchi(g, u, s):
    """
    Solves a Buchi inter co-Buchi game. The set u is to be visited infinitely often and s is to be visited finitely.
    Assumes player 0 has the Buchi inter co-Buchi objective.
    :param g: a game graph.
    :param u: the set of nodes to be visited infinitely often.
    :param s: the set of nodes to be visited finitely often.
    :return: w_0, w_1 the winning regions.
    """

    # TODO check if we need both winning regions

    # We iterate over several subgames
    current_game = g

    i = 1
    res = []

    while True:
        # Winning regions for player 1 in the buchi inter safety game in current_game.
        w = buchi_inter_safety.buchi_inter_safety(current_game, u, s)

        if not w:
            break

        res.extend(w)
        a, not_a = attractors.attractor(g, w, 0)

        current_game = g.subgame(not_a)
        i = i + 1
    return res

def buchi_inter_cobuchi_player(g, u, s, j):
    """
    Solves a Buchi inter co-Buchi game. The set u is to be visited infinitely often and s is to be visited finitely.
    Assumes player 0 has the Buchi inter co-Buchi objective.
    :param g: a game graph.
    :param u: the set of nodes to be visited infinitely often.
    :param s: the set of nodes to be visited finitely often.
    :param j: the player with the Buchi inter co-Buchi objective.
    :return: w_0, w_1 the winning regions.
    """

    # TODO check if we need both winning regions

    # We iterate over several subgames
    current_game = g

    i = 1
    res = []

    while True:
        # Winning regions for player 1 in the buchi inter safety game in current_game.
        w = buchi_inter_safety.buchi_inter_safety_player(current_game, u, s, j)

        if not w:
            break

        res.extend(w)
        a, not_a = attractors.attractor(g, w, j)

        current_game = g.subgame(not_a)
        i = i + 1

    return res