import fatalattractors.attractors as attractors
import copy

DEBUG_PRINT = False


def buchi_classical(g, b):
    """
    Classical algorithm in O(n.m) to solve Buchi games. Assumes player 1 has the Buchi objective.
    :param g: a game graph.
    :param b: a set of nodes in g.
    :return: w_0, w_1 the solution of the Buchi game.
    """

    # We don't want g to be modified # TODO check if this is required as subgames don't modify the object
    g = copy.deepcopy(g)
    res = []

    # This is a reapeat until loop which creates a fixpoint
    while True:

        if DEBUG_PRINT:
            print("--------------------------------------------------------------")
            print("B is " + str(b))
            print("V is " + str(g.get_nodes()))

        # TODO check if I really need to compute the intersection here or I can just ignore it and handle it in
        # the attractor directly.
        b_inter_v = list(set(b).intersection(set(g.get_nodes())))
        # TODO b inter v is recomputed all the time without modifying b should we not modify b
        # and remove the nodes suppoosed to be removed

        if DEBUG_PRINT: print("B inter V " + str(b_inter_v))

        w, v = avoid_set_classical(g, b_inter_v)

        if DEBUG_PRINT: print("AVOID SET " + str(w) + " " + str(v))

        g = g.subgame(v)

        if DEBUG_PRINT:
            print("SUBGAME")
            print(g)

        res.extend(w)

        if DEBUG_PRINT: print("RES " + str(res))

        if len(w) == 0:

            if DEBUG_PRINT: print("RES " + str(res) + " REMAINING NODES IN SUBGAME " + str(g.get_nodes()))

            break
    # TODO return the remaining game and the other winning region
    return g.get_nodes()


def avoid_set_classical(g, b):
    """
    This procedure is part of buchi_classical and computes the set of states in G from which player 1
    can avoid reaching b. Assumes player 1 has the Buchi objective.
    :param g: a game graph.
    :param B: a set of nodes in g.
    :return: w the set of nodes from which player 1 can avoid reaching b.
    """
    if DEBUG_PRINT:
        print("----------------------------")
        print("     AVOID SET")

    r, t_r = attractors.attractor(g, b, 0)

    if DEBUG_PRINT: print("     R " + str(r) + " TR " + str(t_r))

    w, not_w = attractors.attractor(g, t_r, 1)

    if DEBUG_PRINT:
        print("     W " + str(w) + " NOT W " + str(not_w))
        print("----------------------------")

    return w, not_w


def buchi_classical_player(g, b, j):
    """
    Classical algorithm in O(n.m) to solve Buchi games.
    :param g: a game graph.
    :type g: Graph
    :param b: a set of nodes in g.
    :param j: the player with the Buchi objective.
    :return: w_0, w_1 the solution of the Buchi game.
    """

    # We don't want g to be modified
    g = copy.deepcopy(g)
    res = []

    # This is a reapeat until loop which creates a fixpoint
    while True:
        # TODO check if I really need to compute the intersection here or I can just ignore it and handle it in
        # the attractor directly.

        if DEBUG_PRINT:
            print("--------------------------------------------------------------")
            print("B is " + str(b))
            print("V is " + str(g.get_nodes()))

        b_inter_v = list(set(b).intersection(set(g.get_nodes())))

        if DEBUG_PRINT: print("B inter V " + str(b_inter_v))

        w, v = avoid_set_classical_player(g, b_inter_v, j)

        if DEBUG_PRINT: print("AVOID SET " + str(w) + " " + str(v))

        g = g.subgame(v)

        if DEBUG_PRINT:
            print("SUBGAME")
            print(g)

        res.extend(w)

        if DEBUG_PRINT: print("RES " + str(res))

        if len(w) == 0:

            if DEBUG_PRINT: print("RES " + str(res) + " REMAINING NODES IN SUBGAME " + str(g.get_nodes()))

            break
    # TODO return the remaining game and the other winning region
    return g.get_nodes()


def avoid_set_classical_player(g, b, j):
    """
    This procedure is part of buchi_classical and computes the set of states in G from which player 1
    can avoid reaching b.
    :param g: a game graph.
    :param B: a set of nodes in g.
    :param j: the player with the Buchi objective.
    :return: w the set of nodes from which player 1 can avoid reaching b.
    """
    if DEBUG_PRINT:
        print("----------------------------")
        print("     AVOID SET")

    r, t_r = attractors.attractor(g, b, j)

    if DEBUG_PRINT: print("     R " + str(r) + " TR " + str(t_r))

    w, not_w = attractors.attractor(g, t_r, (j + 1) % 2)

    if DEBUG_PRINT:
        print("     W " + str(w) + " NOT W " + str(not_w))
        print("----------------------------")

    return w, not_w
