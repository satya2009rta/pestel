import fatalattractors.attractors as attractors
import copy

DEBUG_PRINT = False


def generalized_buchi_classical(g, sets):
    """
    Classical algorithm in O(k.n.m) to solve genralized Buchi games. Assumes player 1 has the generalized Buchi
    objective.
    :param g: a game graph.
    :param sets: a list of sets of nodes in g.
    :return: w_0, w_1 the solution of the Buchi game.
    """

    # We don't want g to be modified # TODO check if this is required as subgames don't modify the object
    g = copy.deepcopy(g)
    nbr_of_sets = len(sets)
    # This is a reapeat until loop which creates a fixpoint
    while True:

        for l in range(nbr_of_sets):



            y, s = attractors.attractor(g, sets[l], 0)

            if s != []:
                break


        d, not_d = attractors.attractor(g, s, 1)



        # TODO check if I really need to compute the intersection here or I can just ignore it and handle it in
        # the attractor directly.
        sets[l] = list(set(sets[l]).intersection(set(g.get_nodes())))
        # TODO check sets operations for removing nodes, check bi sets


        g = g.subgame(not_d)





        if len(d) == 0:


            break
    # TODO return the remaining game and the other winning region
    return g.get_nodes()


