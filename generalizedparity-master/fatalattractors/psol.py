from collections import defaultdict, deque

import operations as op
from fatalattractors.attractors import init_out, attractor

DEBUG_PRINT = False


def sort_nodes_by_priority(g):
    """
    Sort node ids in ascending order of priority.
    :param g: a game graph.
    :return: the node ids sorted in ascending order of priority.
    """

    # x is a key of the dictionary a value (1, 4) means player 1, priority 4
    # we return the node id, sorted by priority incrementally
    return sorted(g.nodes.iterkeys(), key=lambda x: g.nodes[x][1])


def monotone_attractor(g, node):
    """
    Computes the monotone attractor of the given node. For details, see the paper 'Fatal Attractors in Parity Games:
    Building Blocks for Partial Solvers'.
    :param g: a game graph.
    :param node: a node id.
    :return: the monotone attractor of node in g.
    """

    priority = g.get_node_priority(node)  # priority of the node gives us the player for which we compute the attractor
    out = init_out(g)  # init out
    queue = deque()  # init queue (deque is part of standard library and allows O(1) append() and pop() at either end)
    # this dictionary is used to know if a node belongs to a winning region without
    # iterating over both winning regions lists (we can check in O(1) in average)
    regions = defaultdict(lambda: -1)
    W = []  # the attractor
    j = priority % 2  # the player for which we compute the attractor
    opponent = op.opponent(j)  # player j's opponent

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
            sbis_priority = g.get_node_priority(sbis)
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


def psol(g, W1, W2):
    """
    PSOL partial solver using fatal attractors.
    :param g: a game graph.
    :return: a partial solution g', W1', W2' in which g is an unsolved subgame of g and W1', W2' are included in the
    two respective winning regions of g.
    """

    for node in sort_nodes_by_priority(g):

        if DEBUG_PRINT: print("Computing for node " + str(node))

        # compute monotone attractor
        MA, rest = monotone_attractor(g, node)

        if DEBUG_PRINT: print(" MA " + str(MA) + " Player " + str(g.get_node_player(node)) + "\n")

        # if attractor is fatal
        if node in MA:

            if DEBUG_PRINT: print("Node " + str(node) + " in MA ")

            priority = g.get_node_priority(node)

            # attractor to the fatal attractor, winning for player priority % 2
            att, complement = attractor(g, MA, priority % 2)

            if priority % 2 == 0:
                W1.extend(att)
            else:
                W2.extend(att)

            return psol(g.subgame(complement), W1, W2)

    return g, W1, W2


def psol_edge_removal(g, W1, W2):
    """
    PSOL partial solver using fatal attractors and edge removal.
    /!\ This modifies the arena by removing edges.
    :param g: a game graph.
    :return: a partial solution g', W1', W2' in which g is an unsolved subgame of g and W1', W2' are included in the
    two respective winning regions of g.
    """

    for node in sort_nodes_by_priority(g):

        MA, rest = monotone_attractor(g, node)

        if node in MA:

            priority = g.get_node_priority(node)

            att, complement = attractor(g, MA, priority % 2)

            if priority % 2 == 0:
                W1.extend(att)
            else:
                W2.extend(att)

            return psol(g.subgame(complement), W1, W2)

        # removing edges which can't be used since they would create a fatal attractor
        for successor in g.get_successors(node):
            if successor in MA:
                # TODO check efficiency of edge removal
                g.remove_successor(node, successor)
                g.remove_predecessor(successor, node)

    return g, W1, W2
