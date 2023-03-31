from generalized_buchi import generalized_buchi_classical
from fatalattractors import attractors


def generalized_buchi_inter_safety(g, sets, s):
    """
    Solves a generalized Buchi inter safety game where player 0 has that objective.
    sets contains the sets to be visited infinitely often
    and s is to be avoided.
    :param g: a game graph.
    :param sets: the sets of nodes to be visited infinitely often.
    :param s: the set of nodes to be avoid.
    :return: the winning regions w_0, w_1.
    """

    a, not_a = attractors.attractor(g, s, 1)
    g_reduced = g.subgame(not_a)
    return generalized_buchi_classical(g_reduced, sets)


def inlined_generalized_buchi_inter_safety(g, sets, U):
    nbr_of_sets = len(sets)
    # This is a reapeat until loop which creates a fixpoint
    while True:
        for l in range(nbr_of_sets):
            y, s = attractors.safe_attractor(g, sets[l], U, 0)
            if s != []:
                break  # we've found a dimension in which Pl 1 can win
        d, not_d = attractors.attractor(g, s, 1)
        sets[l] = list(set(sets[l]).intersection(set(g.get_nodes())))
        # TODO check sets operations for removing nodes, check bi sets
        g = g.subgame(not_d)
        if len(d) == 0:
            break
    # TODO return the remaining game and the other winning region
    return g.get_nodes()
