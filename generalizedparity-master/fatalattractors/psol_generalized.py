from collections import defaultdict, deque

import operations as op
from fatalattractors.attractors import init_out, attractor

DEBUG_PRINT = False


def monotone_attractor_player0(g, node, priorities, player):
    """
    Computes an attractor to a single node while making sure that no priority greater than that of the target node
    is visited (for every priority functions).
    :param g: a game graph.
    :param node: a target node.
    :param priorities: the informations regarding that node : (player, priority_1, ..., priority_k).
    :param player: the player for which we compute the attractor.
    :return: the monotone attractor of node in g.
    """

    nbr_func = len(priorities) - 1  # number of priority functions
    out = init_out(g)  # init out
    queue = deque()  # init queue (deque is part of standard library and allows O(1) append() and pop() at either end)
    # this dictionary is used to know if a node belongs to a winning region without
    # iterating over both winning regions lists (we can check in O(1) in average)
    regions = defaultdict(lambda: -1)
    W = []  # the attractor
    j = player  # the player for which we compute the attractor
    opponent = op.opponent(j)  # player j's opponent

    queue.append(node)  # add node to the end of the queue.
    # Note: node is not de facto in the attractor, it will be added during computations if it is

    if DEBUG_PRINT:
        print("--- Monotone attractor ---")
        print(g)
        print("Node " + str(node) + " Player " + str(j) + " Opponent " + str(opponent) + " Priority " + str(priorities))
        print("Marked before start " + str(regions) + " Queue before start " + str(queue))

    # while queue is not empty
    while queue:

        if DEBUG_PRINT: print("     Queue " + str(queue))

        s = queue.popleft()  # remove and return node on the left side of the queue (first in, first out)

        if DEBUG_PRINT: print("     Considering node " + str(s))

        # iterating over the predecessors of node s
        for sbis in g.get_predecessors(s):

            sbis_priority = g.get_node_priority(sbis)
            sbis_player = g.get_node_player(sbis)

            if DEBUG_PRINT: print(
                "         Considering predecessor " + str(sbis) + " Is marked ? " + str(
                    regions[sbis]) + " Player " + str(
                    sbis_player) + " Priority " + str(sbis_priority))

            if regions[sbis] == -1:  # if sbis is not yet visited, its region is -1 by default

                # in any case, we only consider predecessors which have smaller priorities according to every function
                flag = False  # records wether a priority function i has been found such that alpha_i(sbis) > alpha_i(s)

                # functions are from 1 to k
                for index in range(1, nbr_func + 1):

                    # priority of sbis according to function index
                    prio = g.get_node_priority_function_i(sbis, index)

                    # TODO add prio % 2 != player and here if we are to consider the extended condition on priorities

                    # if the priority of sbis is greater, we break because we have found a function which falsifies
                    if prio > priorities[index]:
                        flag = True
                        break

                # if the node is not to be considered, continue to the next iteration of the loop, else check the player
                if flag: continue

                # if node is the correct player (its priority is lower or equal per the above check)
                if sbis_player == j:

                    if DEBUG_PRINT: print("             Predecessor " + str(sbis) + " Added ")

                    # if node has not been considered yet (not already been in the queue) add it
                    # this is to avoid considering the same node twice, which can happen only for the target node and
                    # can mess up the decrementation of the counters for nodes of the opponent
                    if sbis != node:
                        queue.append(sbis)

                    # mark accordingly and add to winning region
                    regions[sbis] = j
                    W.append(sbis)

                # if node is the opposite player, check its counter of successors
                elif sbis_player == opponent:

                    # belongs to opponent, decrement out. If out is 0, set the region accordingly
                    out[sbis] -= 1

                    if DEBUG_PRINT: print(
                        "             Predecessor " + str(sbis) + " Decrement, new count = " + str(out[sbis]))

                    if out[sbis] == 0:

                        if DEBUG_PRINT: print("             Predecessor " + str(sbis) + " Added ")

                        # if node has not been considered yet (not already been in the queue) add it
                        if sbis != node:
                            queue.append(sbis)

                        # mark accordingly and add to winning region
                        regions[sbis] = j
                        W.append(sbis)

    Wbis = filter(lambda x: regions[x] != j, g.nodes.iterkeys())

    if DEBUG_PRINT:
        print("Attractor " + str(W) + " Complement " + str(Wbis))
        print("-------------------------\n")

    return W, Wbis


def monotone_attractor_player1(g, node, function):
    """
    Computes a monotone attractor similarly to psol, while only considering one of the priority functions.
    :param g: a game graph.
    :param node: a target node.
    :param function: the priority function to consider.
    :return: the monotone attractor of node in g.
    """

    priority = g.get_node_priority_function_i(node, function)  # priority of the node according to function i
    out = init_out(g)  # init out
    queue = deque()  # init queue (deque is part of standard library and allows O(1) append() and pop() at either end)
    # this dictionary is used to know if a node belongs to a winning region without
    # iterating over both winning regions lists (we can check in O(1) in average)
    regions = defaultdict(lambda: -1)
    W = []  # the attractor
    j = 1  # the player for which we compute the attractor
    opponent = 0  # player j's opponent

    queue.append(node)  # add node to the end of the queue.
    # note: node is not de facto in the attractor, it will be added during computations if it belongs to it

    if DEBUG_PRINT:
        print("--- Monotone attractor ---")
        print(g)
        print("Node " + str(node) + " Player " + str(j) + " Opponent " + str(opponent) + " Priority " + str(priority))
        print("Marked before start " + str(regions) + " Queue before start " + str(queue))

    # while queue is not empty
    while queue:

        if DEBUG_PRINT: print("     Queue " + str(queue))

        s = queue.popleft()  # remove and return node on the left side of the queue (first in, first out)

        if DEBUG_PRINT: print("     Considering node " + str(s))

        # iterating over the predecessors of node s
        for sbis in g.get_predecessors(s):

            # retrieve node player and priority
            sbis_priority = g.get_node_priority_function_i(sbis, function)
            sbis_player = g.get_node_player(sbis)

            if DEBUG_PRINT: print("         Considering predecessor " + str(sbis) + " Is marked ? " + str(regions[sbis])
                                  + " Player " + str(sbis_player) + " Priority " + str(sbis_priority))

            if regions[sbis] == -1:  # if sbis is not yet visited, its region is -1 by default

                # if node is the correct player and its priority is lower or equal, add it
                if sbis_player == j and sbis_priority <= priority:

                    if DEBUG_PRINT: print("             Predecessor " + str(sbis) + " Added ")

                    # if node has not been considered yet (not already been in the queue) add it
                    # this is to avoid considering the same node twice, which can happen only for the target node and
                    # can mess up the decrementation of the counters for nodes of the opponent
                    if sbis != node:
                        queue.append(sbis)

                    # mark accordingly and add to winning region
                    regions[sbis] = j
                    W.append(sbis)

                # if node is the opposite player and its priority is lower or equal, check its counter of successors
                elif sbis_player == opponent and sbis_priority <= priority:

                    # belongs to opponent, decrement out. If out is 0, set the region accordingly
                    out[sbis] -= 1

                    if DEBUG_PRINT: print(
                        "             Predecessor " + str(sbis) + " Decrement, new count = " + str(out[sbis]))

                    if out[sbis] == 0:

                        if DEBUG_PRINT: print("             Predecessor " + str(sbis) + " Added ")

                        # if node has not been considered yet (not already been in the queue) add it
                        if sbis != node:
                            queue.append(sbis)

                        # mark accordingly and add to winning region
                        regions[sbis] = j
                        W.append(sbis)

    # every node that is not marked is not in the attractor, we filter them for speed
    Wbis = filter(lambda x: regions[x] != j, g.nodes.iterkeys())

    if DEBUG_PRINT:
        print("Attractor " + str(W) + " Complement " + str(Wbis))
        print("-------------------------\n")

    return W, Wbis


def psol_generalized(g, W1, W2, inverted=False):
    """
    Adaptation of psol partial solver to generalized parity games.
    inverted true means we record odd priorities instead of even ones
    :param g: a game graph.
    :return: a partial solution g', W1', W2' in which g is an unsolved subgame of g and W1', W2' are included in the
    two respective winning regions of g.
    """

    # TODO we can add ordering on the nodes, such as considering those with odd priorities first

    # we iterate over the node, node_info in the game
    for node, info in g.nodes.iteritems():

        found_odd = False  # have we found an odd priority for the node

        # iterate over priority functions
        for i in range(1, len(info)):

            # one of the priorities is odd
            if info[i] % 2 == (not inverted):

                found_odd = True

                # note : we can reuse the monotone attractor of player 0 for player 1 but it is a stronger condition
                # than needed indeed, we ask that no bigger priority is visited according to every function, instead of
                # focusing on one

                # compute the monotone attractor for this node, for player 1 on the correct function
                MA, rest = monotone_attractor_player1(g, node, i)

                # if the attractor is fatal
                if node in MA:

                    if DEBUG_PRINT: print("Node " + str(node) + " in MA ")

                    att, complement = attractor(g, MA, 1)

                    W2.extend(att)

                    return psol_generalized(g.subgame(complement), W1, W2, inverted)

        # if we get here, then every priority is even or none of the computed attractors are fatal

        # if every priority is even
        if not found_odd:

            # compute the monotone attractor for this node, for player 0 on the correct function
            MA, rest = monotone_attractor_player0(g, node, info, 0)

            # if the attractor is fatal
            if node in MA:

                if DEBUG_PRINT: print("Node " + str(node) + " in MA ")

                att, complement = attractor(g, MA, 0)

                W1.extend(att)

                return psol_generalized(g.subgame(complement), W1, W2, inverted)

    return g, W1, W2
