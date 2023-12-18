import copy
import file_handler as io

from fatalattractors import attractors as reachability
import operations as ops


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


def disj_parity_win(g, maxValues, k, u):
    """
    Recursive solver for generalized parity games. Implements the classical algorithm which solves generalized parity
    games.
    :param g: the game to solve
    :param maxValues: the maximum value according to each priority function
    :param k: the number of priority functions
    :param u: integer for testing purposes
    :return: W1, W2 the winning regions in the game for player 1 and player 2
             (for the original game, without complement)
    """
    # For the correctness argument to work, and for the base case too,
    # we need the max value of each priority to be odd!
    assert(all(m % 2 == 1 for m in maxValues))

    # Base case : all maxValues are 1 or the game is empty
    if all(value == 1 for value in maxValues) or len(g.get_nodes()) == 0:
        return g.get_nodes(), []

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
            attMaxOdd, compl_attMaxOdd = reachability.attractor(g, ops.i_priority_node_function_j(g, maxValues[i], i + 1),
                                                                0)
            G1 = g.subgame(compl_attMaxOdd)
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
                W1, W2 = disj_parity_win(H1, copy_maxValues, k, u + 1)
                # sanity check: if all priorities were odd, then W1 union G1.V should be g.V
                assert(set(G1.get_nodes()).union(set(W1)) != g.get_nodes()
                       or any(g.get_node_priority_function_i(n, i) % 2 == 0
                              for n in g.get_nodes()))
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
                B, compl_B = reachability.attractor(g, G1.get_nodes(), 1)
                # sanity check: we always do a recursive call on a smaller game
                # and so necessarily B is non-empty
                assert(len(B) > 0)
                # end of sanity check
                W1, W2 = disj_parity_win(g.subgame(compl_B), maxValues, k, u + 1)
                B.extend(W2)
                return W1, B

    return g.get_nodes(), []


def generalized_parity_solver(g):
    """
    Generalized parity games solver. This is an implementation of the classical algorithm used to solve generalized
    parity games. This is the wrapper function which complements every priority and calls the actual algorithm.
    :param g: the arena of the generalized parity game
    :return: the solution in the following format : W_0, W_1
    """
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

    return disj_parity_win(transformed, maxValues, nbrFunctions, 0)


# g = io.load_generalized_from_file("examples/seed_72-10,4,10,1,10.txt")
# W1, W2 = generalized_parity_solver(g)
