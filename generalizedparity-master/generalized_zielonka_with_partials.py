import copy

import operations as ops
import fatalattractors.psolB_generalized as psolB_gen
import fatalattractors.psolQ_generalized as psolQ_gen
import fatalattractors.psolC_generalized as psolC_gen
import fatalattractors.psol_generalized as psol_gen
import fatalattractors.attractors as reachability
import generalized_parity_recursive as regular_generalized_parity


def transform_game(g, k):
    """
    Transforms a game as a pre-processing to the generalized parity games solver.
    Every priority function is "complemented" (each priority is incremented by 1)
    :param g: the game to complement
    :param k:
    :return: the compemented game
    """
    g_copy = copy.deepcopy(g)  # Deep copy of the game g
    descriptors = g_copy.get_nodes_descriptors()  # Descriptors of the nodes (player, priority_1, ..., priority_k)
    # For each node, get the descriptor and update the descriptor by adding 1 to each priority
    for node in g_copy.get_nodes():
        current = descriptors[node]
        descriptors[node] = tuple([current[0]] + map(lambda x: x + 1, current[1:]))
    return g_copy


def generalized_parity_solver_with_partial_preprocessing(g, partial_solver):
    """
    Generalized parity games solver. This is an implementation of the classical algorithm used to solve generalized
    parity games. This is the wrapper function which complements every priority and calls the actual algorithm.
    :param g: the game to solve.
    :param partial_solver: a partial solver.
    :return: the solution in the following format : (W_0, W_1).
    """

    rest, W0, W1 = partial_solver(g, [], [], inverted=False)  # call to the partial solver

    if len(rest.nodes) == 0:
        return W0, W1


    # nbr of functions is the length of the descriptor minus 1 (because the descriptor contains the player)
    nbrFunctions = len(rest.get_nodes_descriptors()[rest.get_nodes()[0]]) - 1
    # Transforming the game
    transformed = transform_game(rest, nbrFunctions)
    # Initializing the max values list
    maxValues = [0] * nbrFunctions

    # Getting the maximum value according to each priority function
    descriptors = transformed.get_nodes_descriptors()

    # Get the maximal priority in the game according to every priority function.
    for node in transformed.get_nodes():
        current = descriptors[node]
        for i in range(1, nbrFunctions + 1):
            if current[i] > maxValues[i - 1]:
                maxValues[i - 1] = current[i]

    # Max values need to be odd, if some are even, add 1
    for i in range(0, nbrFunctions):
        if maxValues[i] % 2 == 0:
            maxValues[i] += 1

    # call to classical disj parity win
    W0_bis, W1_bis = regular_generalized_parity.disj_parity_win(transformed, maxValues, nbrFunctions, 0)
    W0.extend(W0_bis)
    W1.extend(W1_bis)
    return W0, W1



def generalized_zielonka_with_psol_preprocessing(g):
    """
    Zielonka's algorithm with psol partial solver.
    :param g: the game to solve.
    :return: the solution in the following format : (W_0, W_1).
    """

    return generalized_parity_solver_with_partial_preprocessing(g, psol_gen.psol_generalized)


def generalized_with_psolB_preprocessing(g):
    """
    Zielonka's algorithm with psolB partial solver.
    :param g: the game to solve.
    :return: the solution in the following format : (W_0, W_1).
    """

    return generalized_parity_solver_with_partial_preprocessing(g, psolB_gen.psolB_generalized_inline)


def generalized_zielonka_with_psolQ_preprocessing(g):
    """
    Zielonka's algorithm with psolQ partial solver.
    :param g: the game to solve.
    :return: the solution in the following format : (W_0, W_1).
    """

    return generalized_parity_solver_with_partial_preprocessing(g, psolQ_gen.psolQ_generalized)


def generalized_parity_solver_with_partial(g, partial_solver):
    """
    Generalized parity games solver. This is an implementation of the classical algorithm used to solve generalized
    parity games. This is the wrapper function which complements every priority and calls the actual algorithm.
    :param g: the game to solve.
    :param partial_solver: a partial solver.
    :return: the solution in the following format : (W_0, W_1).
    """

    if len(g.nodes) == 0:
        return [], []

    # nbr of functions is the length of the descriptor minus 1 (because the descriptor contains the player)
    nbrFunctions = len(g.get_nodes_descriptors()[g.get_nodes()[0]]) - 1
    # Transforming the game
    transformed = transform_game(g, nbrFunctions)
    # Initializing the max values list
    maxValues = [0] * nbrFunctions

    # Getting the maximum value according to each priority function
    descriptors = transformed.get_nodes_descriptors()

    # Get the maximal priority in the game according to every priority function.
    for node in transformed.get_nodes():
        current = descriptors[node]
        for i in range(1, nbrFunctions + 1):
            if current[i] > maxValues[i - 1]:
                maxValues[i - 1] = current[i]

    # Max values need to be odd, if some are even, add 1
    for i in range(0, nbrFunctions):
        if maxValues[i] % 2 == 0:
            maxValues[i] += 1

    # call to classical disj parity win
    return disj_parity_win_with_partial(transformed, maxValues, nbrFunctions, 0, partial_solver)


def disj_parity_win_with_partial(g, maxValues, k, u, partial):
    """
    Recursive solver for generalized parity games. Implements the classical algorithm which solves generalized parity
    games.
    :param g: the game to solve
    :param maxValues: the maximum value according to each priority function
    :param k: the number of priority functions
    :param u: integer for testing purposes
    :param partial: partial solver.
    :return: W1, W2 the winning regions in the game for player 1 and player 2
             (for the original game, without complement)
    """

    # Base case : all maxValues are 1 or the game is empty
    if all(value == 1 for value in maxValues) or len(g.get_nodes()) == 0:
        return g.get_nodes(), []

    rest, W0_partial, W1_partial = partial(g, [], [], inverted=True)  # call to the partial solver

    if len(rest.nodes) == 0:
        return W0_partial, W1_partial

    # For the correctness argument to work, and for the base case too,
    # we need the max value of each priority to be odd!
    assert(all(m % 2 == 1 for m in maxValues))

    # FIXME: the code below is a hacked base case, remove it when the bug is
    # fixed. Clement added this condition, which states that if there is only
    # one node left with only odd priorities, it is winning for player 1
    # (since we work with complemented priorities in this algorithm)
    # if len(g.nodes) == 1 and all(value % 2 == 1 for value in g.nodes[g.get_nodes()[0]][1:]):
    #     return g.get_nodes(), []
    for i in range(k):

        # We only consider priority functions according to which every value is not 1
        if maxValues[i] != 1:

            # if u <= 4:
            #     print("-" * u + str(i))
            attMaxOdd, compl_attMaxOdd = reachability.attractor(rest, ops.i_priority_node_function_j(rest, maxValues[i], i + 1),
                                                                0)
            G1 = rest.subgame(compl_attMaxOdd)
            attMaxEven, compl_attMaxEven = reachability.attractor(G1, ops.i_priority_node_function_j(G1, maxValues[i] - 1,
                                                                                                     i + 1), 1)
            H1 = G1.subgame(compl_attMaxEven)
            while True:
                h1_old_len = len(H1.get_nodes())
                copy_maxValues = copy.copy(maxValues)
                copy_maxValues[i] -= 2
                # sanity check: on recursive calls we have less priorities
                # It should not be the case that negative max priorities occur as we only consider functions
                # in which the max odd value is > 1. Negative values happened when we considered the following
                # instruction when maxValue is 1.
                assert(copy_maxValues[i] >= 0)
                assert(copy_maxValues[i] == maxValues[i] - 2)
                # end of sanity check
                W1, W2 = disj_parity_win_with_partial(H1, copy_maxValues, k, u + 1, partial)
                # sanity check: if all priorities were odd, then W1 union G1.V should be g.V
                assert(set(G1.get_nodes()).union(set(W1)) != rest.get_nodes()
                       or any(rest.get_node_priority_function_i(n, i) % 2 == 0
                              for n in rest.get_nodes()))
                # end of sanity check

                if len(G1.get_nodes()) == 0 or set(W2) == set(H1.get_nodes()):
                    break

                T, compl_T = reachability.attractor(G1, W1, 0)
                G1 = G1.subgame(compl_T)
                E, compl_E = reachability.attractor(G1,
                                                    ops.i_priority_node_function_j(G1, maxValues[i] - 1, i + 1), 1)
                H1 = G1.subgame(compl_E)
                # assert(len(H1.get_nodes()) < h1_old_len)

            # checks after the end of the loop (base cases, essentially)
            if set(W2) == set(H1.get_nodes()) and len(G1.get_nodes()) > 0:
                assert(len(G1.get_nodes()) > 0)  # otherwise this makes no sense!
                B, compl_B = reachability.attractor(rest, G1.get_nodes(), 1)
                # sanity check: we always do a recursive call on a smaller game
                # and so necessarily B is non-empty
                assert(len(B) > 0)
                # end of sanity check
                W1, W2 = disj_parity_win_with_partial(rest.subgame(compl_B), maxValues, k, u + 1, partial)
                B.extend(W2)

                return W1 + W0_partial, B + W1_partial

    return W0_partial + rest.get_nodes(), W1_partial


def generalized_zielonka_with_psol(g):
    """
    Zielonka's algorithm with psol partial solver.
    :param g: the game to solve.
    :return: the solution in the following format : (W_0, W_1).
    """

    return generalized_parity_solver_with_partial(g, psol_gen.psol_generalized)


def generalized_with_psolB(g):
    """
    Zielonka's algorithm with psolB partial solver.
    :param g: the game to solve.
    :return: the solution in the following format : (W_0, W_1).
    """

    return generalized_parity_solver_with_partial(g, psolB_gen.psolB_generalized_inline)


def generalized_zielonka_with_psolQ(g):
    """
    Zielonka's algorithm with psolQ partial solver.
    :param g: the game to solve.
    :return: the solution in the following format : (W_0, W_1).
    """

    return generalized_parity_solver_with_partial(g, psolQ_gen.psolQ_generalized)


def generalized_zielonka_with_psolC(g):
    """
    Zielonka's algorithm with psolC partial solver.
    :param g: the game to solve.
    :return: the solution in the following format : (W_0, W_1).
    """

    return generalized_parity_solver_with_partial(g, psolC_gen.psolC_generalized)