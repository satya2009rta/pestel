from fatalattractors import psolC
from fatalattractors.attractors import attractor
import operations as ops
import fatalattractors.psolB as psolB
import fatalattractors.psolQ as psolQ
import fatalattractors.psol as psol


def strong_parity_solver_no_strategies(g):
    """
    Strong parity games solver. This is an implementation of the recursive algorithm used to solve parity games.
    This implementation does not compute the winning strategies (for comparison purpose with other algorithms
    which don't)
    :param g: the game to solve.
    :return: the solution in the following format : (W_0, W_1).
    """
    W1 = []  # Winning region of player 0
    W2 = []  # Winning region of player 1

    # if the game is empty, return the empty regions
    if len(g.nodes) == 0:
        return W1, W2

    else:
        i = ops.max_priority(g)  # get max priority occurring in g

        # determining which player we are considering, if i is even : player 0 and else player 1
        if i % 2 == 0:
            j = 0
        else:
            j = 1

        opponent = ops.opponent(j)  # getting the opponent of the player

        U = ops.i_priority_node(g, i)  # target set for the attractor : nodes of priority i

        # getting the attractor A and discarding the region for the opponent
        A, discard1 = attractor(g, U, j)

        # The subgame G\A is composed of the nodes not in the attractor, thus the nodes of the opposite player's region
        G_A = g.subgame(discard1)

        # Recursively solving the subgame G\A, solution comes as (W_0, W_1)
        sol_player1, sol_player2 = strong_parity_solver_no_strategies(G_A)

        # depending on which player we are considering, assign regions to the proper variables
        # W'_j is noted W_j, sigma'_j is noted sig_j; the same aplies for jbar
        if j == 0:
            W_j = sol_player1
            W_jbar = sol_player2
        else:
            W_j = sol_player2
            W_jbar = sol_player1

        # if W'_jbar is empty we update the regions depending on the current player
        # the region for the whole game for one of the players is empty
        if not W_jbar:
            if j == 0:
                W1.extend(A)
                W1.extend(W_j)
            else:
                W2.extend(A)
                W2.extend(W_j)
        else:
            # compute attractor B
            B, discard1 = attractor(g, W_jbar, opponent)
            # The subgame G\B is composed of the nodes not in the attractor, so of the opposite player's winning region
            G_B = g.subgame(discard1)

            # recursively solve subgame G\B, solution comes as (W_0, W_1)
            sol_player1_, sol_player2_ = strong_parity_solver_no_strategies(G_B)

            # depending on which player we are considering, assign regions to the proper variables
            # W''_j is noted W__j, sigma''_j is noted sig__j; the same aplies for jbar
            if j == 0:
                W__j = sol_player1_
                W__jbar = sol_player2_
            else:
                W__j = sol_player2_
                W__jbar = sol_player1_

            # the last step is to update the winning regions depending on which player we consider
            if j == 0:
                W1 = W__j

                W2.extend(W__jbar)
                W2.extend(B)

            else:
                W2 = W__j

                W1.extend(W__jbar)
                W1.extend(B)

    return W1, W2


def zielonka_with_partial(g, partial_solver):
    """
    This is an implementation of Zielonka's recursive algorithm used to solve parity games. This implementation uses a
    provided partial solver to speed up the solving process. This implementation does not compute the winning strategies
    (for comparison purpose with other algorithms which don't).

    :param g: the game to solve.
    :param partial_solver: a partial solver.
    :return: the solution in the following format : (W_0, W_1).
    """

    rest, partial_1, partial_2 = partial_solver(g, [], [])  # TODO this is the default input for the algorithms
    # a more general way is to use just g as input and add the [] [] in a wrapper function in PSOLB

    W1 = []  # Winning region of player 0
    W2 = []  # Winning region of player 1

    # add the partial solutions to the winning regions
    W1.extend(partial_1)
    W2.extend(partial_2)

    # if the game is empty, return the empty regions
    if len(rest.nodes) == 0:
        return W1, W2

    else:
        i = ops.max_priority(rest)  # get max priority occurring in g

        # determining which player we are considering, if i is even : player 0 and else player 1
        if i % 2 == 0:
            j = 0
        else:
            j = 1

        opponent = ops.opponent(j)  # getting the opponent of the player

        U = ops.i_priority_node(rest, i)  # target set for the attractor : nodes of priority i

        # getting the attractor A and discarding the region for the opponent
        A, discard1 = attractor(rest, U, j)

        # The subgame G\A is composed of the nodes not in the attractor, thus the nodes of the opposite player's region
        G_A = rest.subgame(discard1)

        # Recursively solving the subgame G\A, solution comes as (W_0, W_1)
        sol_player1, sol_player2 = zielonka_with_partial(G_A, partial_solver)

        # depending on which player we are considering, assign regions to the proper variables
        # W'_j is noted W_j, sigma'_j is noted sig_j; the same aplies for jbar
        if j == 0:
            W_j = sol_player1
            W_jbar = sol_player2
        else:
            W_j = sol_player2
            W_jbar = sol_player1

        # if W'_jbar is empty we update the regions depending on the current player
        # the region for the whole game for one of the players is empty
        if not W_jbar:
            if j == 0:
                W1.extend(A)
                W1.extend(W_j)
            else:
                W2.extend(A)
                W2.extend(W_j)
        else:
            # compute attractor B
            B, discard1 = attractor(rest, W_jbar, opponent)
            # The subgame G\B is composed of the nodes not in the attractor, so of the opposite player's winning region
            G_B = rest.subgame(discard1)

            # recursively solve subgame G\B, solution comes as (W_0, W_1)
            sol_player1_, sol_player2_ = zielonka_with_partial(G_B, partial_solver)

            # depending on which player we are considering, assign regions to the proper variables
            # W''_j is noted W__j, sigma''_j is noted sig__j; the same aplies for jbar
            if j == 0:
                W__j = sol_player1_
                W__jbar = sol_player2_
            else:
                W__j = sol_player2_
                W__jbar = sol_player1_

            # the last step is to update the winning regions depending on which player we consider
            if j == 0:
                W1 = W__j

                W2.extend(W__jbar)
                W2.extend(B)

            else:
                W2 = W__j

                W1.extend(W__jbar)
                W1.extend(B)

    return W1, W2


def zielonka_with_psol(g):
    """
    Zielonka's algorithm with psol partial solver.
    :param g: the game to solve.
    :return: the solution in the following format : (W_0, W_1).
    """

    return zielonka_with_partial(g, psol.psol)


def zielonka_with_psolB(g):
    """
    Zielonka's algorithm with psolB partial solver.
    :param g: the game to solve.
    :return: the solution in the following format : (W_0, W_1).
    """

    return zielonka_with_partial(g, psolB.psolB_set)


def zielonka_with_psolB_buchi_safety(g):
    """
    Zielonka's algorithm with psolB partial solver implemented using Buchi inter safety games.
    :param g: the game to solve.
    :return: the solution in the following format : (W_0, W_1).
    """

    return zielonka_with_partial(g, psolB.psolB_buchi_safety)


def zielonka_with_psolB_buchi_cobuchi(g):
    """
    Zielonka's algorithm with psolB partial solver implemented using Buchi inter co-Buchi games.
    :param g: the game to solve.
    :return: the solution in the following format : (W_0, W_1).
    """

    return zielonka_with_partial(g, psolB.psolB_buchi_cobuchi)


def zielonka_with_psolQ(g):
    """
    Zielonka's algorithm with psolQ partial solver.
    :param g: the game to solve.
    :return: the solution in the following format : (W_0, W_1).
    """

    return zielonka_with_partial(g, psolQ.psolQ)


def zielonka_with_psolC(g):
    """
    Zielonka's algorithm with psolC partial solver.
    :param g: the game to solve.
    :return: the solution in the following format : (W_0, W_1).
    """

    return zielonka_with_partial(g, psolC.psolC)


def zielonka_with_single_psolB_iteration(g):
    """
    This is an implementation of Zielonka's recursive algorithm used to solve parity games. This implementation uses one
    iteration of psolB, for the set of nodes of maximum priority retrieved by the algorithm. This implementation does
    not compute the winning strategies (for comparison purpose with other algorithms which don't).
    :param g: the game to solve.
    :return: the solution in the following format : (W_0, W_1).
    """

    W1 = []  # Winning region of player 0
    W2 = []  # Winning region of player 1

    W1_partial = []
    W2_partial = []

    empty_set = set()

    # if the game is empty, return the empty regions
    if len(g.nodes) == 0:
        return W1, W2

    else:
        i = ops.max_priority(g)  # get max priority occurring in g

        # determining which player we are considering, if i is even : player 0 and else player 1
        if i % 2 == 0:
            j = 0
        else:
            j = 1

        opponent = ops.opponent(j)  # getting the opponent of the player

        U = ops.i_priority_node(g, i)  # target set for the attractor : nodes of priority i

        rest = g # from now on we work on the game called rest which is g by default, but can be a sub-game of g

        target_set = set(U)  # set of nodes of color 'color'

        cache = set()

        flag = True

        while flag and cache != target_set and target_set != empty_set:

            cache = target_set

            MA, discard = psolB.monotone_attractor(rest, target_set, i)

            if target_set.issubset(MA):

                att, complement = attractor(rest, MA, i % 2)

                if i % 2 == 0:
                    W1_partial.extend(att)
                else:
                    W2_partial.extend(att)

                # we have updated winning regions, we also remove attractor to obtain a sub-game
                rest = g.subgame(complement)

                if rest.get_nodes() == []:
                    return W1_partial, W2_partial

                i = ops.max_priority(rest)  # get max priority occurring in g

                # determining which player we are considering, if i is even : player 0 and else player 1
                if i % 2 == 0:
                    j = 0
                else:
                    j = 1

                opponent = ops.opponent(j)  # getting the opponent of the player

                U = ops.i_priority_node(rest, i)  # target set for the attractor : nodes of priority i

                flag = False

            else:
                target_set = target_set.intersection(MA)

        # getting the attractor A and discarding the region for the opponent
        A, discard1 = attractor(rest, U, j)

        # The subgame G\A is composed of the nodes not in the attractor, thus the nodes of the opposite player's region
        G_A = rest.subgame(discard1)

        # Recursively solving the subgame G\A, solution comes as (W_0, W_1)
        sol_player1, sol_player2 = zielonka_with_single_psolB_iteration(G_A)

        # depending on which player we are considering, assign regions to the proper variables
        # W'_j is noted W_j, sigma'_j is noted sig_j; the same aplies for jbar
        if j == 0:
            W_j = sol_player1
            W_jbar = sol_player2
        else:
            W_j = sol_player2
            W_jbar = sol_player1

        # if W'_jbar is empty we update the regions depending on the current player
        # the region for the whole game for one of the players is empty
        if not W_jbar:
            if j == 0:
                W1.extend(A)
                W1.extend(W_j)
            else:
                W2.extend(A)
                W2.extend(W_j)
        else:
            # compute attractor B
            B, discard1 = attractor(rest, W_jbar, opponent)
            # The subgame G\B is composed of the nodes not in the attractor, so of the opposite player's winning region
            G_B = rest.subgame(discard1)

            # recursively solve subgame G\B, solution comes as (W_0, W_1)
            sol_player1_, sol_player2_ = zielonka_with_single_psolB_iteration(G_B)

            # depending on which player we are considering, assign regions to the proper variables
            # W''_j is noted W__j, sigma''_j is noted sig__j; the same aplies for jbar
            if j == 0:
                W__j = sol_player1_
                W__jbar = sol_player2_
            else:
                W__j = sol_player2_
                W__jbar = sol_player1_

            # the last step is to update the winning regions depending on which player we consider
            if j == 0:
                W1 = W__j

                W2.extend(W__jbar)
                W2.extend(B)

            else:
                W2 = W__j

                W1.extend(W__jbar)
                W1.extend(B)

    if not flag:
        W1.extend(W1_partial)
        W2.extend(W2_partial)

    return W1, W2

# TODO list :
# Zielonka with a single iteration of psol, further iterations are done implicitly in recursive calls
# with psol, using the highest priority we know that it's the max in the game
# use a dictionnary priority:nodes at creation for faster retrieval ?
