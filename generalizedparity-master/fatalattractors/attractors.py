from collections import defaultdict, deque

import operations as op

DEBUG_PRINT = False


def init_out(g):
    """
    Computes the number of outgoing edges for each node in the graph g.
    :param g: the graph g.
    :return: a dictionary where keys are nodes and values are the number of outgoing edges of that node.
    """
    out = defaultdict(int)

    for node in g.get_nodes():
        out[node] = len(g.get_successors(node))

    return out


def attractor(g, U, j):
    """
    Computes the attractor for player j of the set U in g. Does not create any strategy and only returns the set that
    corresponds to the attractor.
    :param g: the game graph.
    :param U: the target set.
    :param j: the player for which we compute the attractor.
    :return: W the set of nodes corresponding to the attractor.
    """
    out = init_out(g)  # init out
    queue = deque()  # init queue (deque is part of standard library and allows O(1) append() and pop() at either end)
    # this dictionary is used to know if a node belongs to a winning region without
    # iterating over both winning regions lists (we can check in O(1) in average)
    regions = defaultdict(lambda: -1)
    W = []  # the attractor
    opponent = op.opponent(j)  # player j's opponent

    # for each node in the target set U
    for node in U:
        queue.append(node)  # add node to the end of the queue
        regions[node] = j  # set its regions to j (node is winning for j because reachability objective is satisfied)
        W.append(node)  # add the node to the winning region list of j

    # while queue is not empty
    while queue:

        s = queue.popleft()  # remove and return node on the left side of the queue (first in, first out)

        # iterating over the predecessors of node s
        for sbis in g.get_predecessors(s):

            if regions[sbis] == -1:  # if sbis is not yet visited, its region is -1 by default
                if g.get_node_player(sbis) == j:

                    # belongs to j, set regions and strategy accordingly
                    queue.append(sbis)
                    regions[sbis] = j
                    W.append(sbis)

                elif g.get_node_player(sbis) == opponent:
                    # belongs to j bar, decrement out. If out is 0, set the region accordingly
                    out[sbis] -= 1

                    if out[sbis] == 0:
                        queue.append(sbis)
                        regions[sbis] = j
                        W.append(sbis)

    Wbis = []
    for node in g.get_nodes():
        if regions[node] != j:
            Wbis.append(node)

    return W, Wbis


def safe_attractor(g, U, Ubis, j):
    out = init_out(g)
    queue = deque()
    regions = defaultdict(lambda: -1)
    opponent = op.opponent(j)

    for node in set(U) - set(Ubis):
        queue.append(node)  # add node to the end of the queue
        regions[node] = j  # set its regions to j (node is winning for j b/c reachability is satisfied)

    while queue:
        s = queue.popleft()  # remove and return node on the left side of the queue (first in, first out)
        # iterating over the predecessors of node s
        for sbis in set(g.get_predecessors(s)) - set(Ubis):
            if regions[sbis] == -1:  # if sbis is not yet visited, its region is -1 by default
                if g.get_node_player(sbis) == j:
                    # belongs to j, set regions and strategy accordingly
                    queue.append(sbis)
                    regions[sbis] = j
                elif g.get_node_player(sbis) == opponent:
                    # belongs to j bar, decrement out. If out is 0, set the region accordingly
                    out[sbis] -= 1
                    if out[sbis] == 0:
                        queue.append(sbis)
                        regions[sbis] = j

    W = []
    Wbis = []
    for node in g.get_nodes():
        if regions[node] == j:
            W.append(node)
        else:
            Wbis.append(node)

    return W, Wbis


def attractor_color(g, U, j, p):
    """
    Computes the attractor for player j of the set U in g. Does not create any strategy and only returns the set that
    corresponds to the attractor. Nodes used in the attractor cannot have a larger priority than p.
    :param g: the game graph.
    :param U: the target set.
    :param j: the player for which we compute the attractor.
    :param p: nodes used in the computation cannot have a larger priority than p.
    :return: W the set of nodes corresponding to the attractor.
    """
    out = init_out(g)  # init out
    queue = deque()  # init queue (deque is part of standard library and allows O(1) append() and pop() at either end)
    # this dictionary is used to know if a node belongs to a winning region without
    # iterating over both winning regions lists (we can check in O(1) in average)
    regions = defaultdict(lambda: -1)
    W = []  # the attractor
    opponent = op.opponent(j)  # player j's opponent

    # for each node in the target set U
    for node in U:
        queue.append(node)  # add node to the end of the queue
        regions[node] = j  # set its regions to j (node is winning for j because reachability objective is satisfied)
        W.append(node)  # add the node to the winning region list of j
    if DEBUG_PRINT:
        print(g)
        print("Set " + str(U) + " Player " + str(j) + " Opponent " + str(opponent) + " Prio " + str(p))
        print("Marked before start " + str(regions) + " Queue before start " + str(queue))
    # while queue is not empty
    while queue:
        if DEBUG_PRINT: print("     Queue " + str(queue))

        s = queue.popleft()  # remove and return node on the left side of the queue (first in, first out)
        if DEBUG_PRINT: print("     Considering node " + str(s))
        # iterating over the predecessors of node s
        for sbis in g.get_predecessors(s):
            if DEBUG_PRINT:
                print("         Considering predecessor " + str(sbis) + " Is marked ? " + str(
                    regions[sbis]) + "Player " + str(g.get_node_player(sbis)) + " Priority " + str(
                    g.get_node_priority(sbis)))
            if regions[sbis] == -1:  # if sbis is not yet visited, its region is -1 by default
                if g.get_node_player(sbis) == j and g.get_node_priority(sbis) <= p:
                    if DEBUG_PRINT: print("             Predecessor " + str(sbis) + " Added ")

                    # belongs to j, set regions and strategy accordingly
                    queue.append(sbis)
                    regions[sbis] = j
                    W.append(sbis)

                elif g.get_node_player(sbis) == opponent and g.get_node_priority(sbis) <= p:
                    # belongs to j bar, decrement out. If out is 0, set the region accordingly
                    out[sbis] -= 1
                    if DEBUG_PRINT: print("             Predecessor " + str(sbis) + " Decrement, new count = " +
                                          str(out[sbis]))
                    if out[sbis] == 0:
                        if DEBUG_PRINT: print("             Predecessor " + str(sbis) + " Added ")

                        queue.append(sbis)
                        regions[sbis] = j
                        W.append(sbis)

    Wbis = []
    for node in g.get_nodes():
        if regions[node] != j:
            Wbis.append(node)
    if DEBUG_PRINT:
        print("Attractor " + str(W) + " Complement " + str(Wbis))
        print("-------------------------\n")
    return W, Wbis

def attractor_color_vector(g, U, j, priorities):
    """
    Computes the attractor for player j of the set U in g. Does not create any strategy and only returns the set that
    corresponds to the attractor. Nodes used in the attractor cannot have a priority function p_i such that the priority
    p_i(node) of that node is larger than priorities[i].
    :param g: the game graph.
    :param U: the target set.
    :param j: the player for which we compute the attractor.
    :param priorities: vector of priorities.
    :return: W the set of nodes corresponding to the attractor.
    """
    out = init_out(g)  # init out
    queue = deque()  # init queue (deque is part of standard library and allows O(1) append() and pop() at either end)
    # this dictionary is used to know if a node belongs to a winning region without
    # iterating over both winning regions lists (we can check in O(1) in average)
    regions = defaultdict(lambda: -1)
    W = []  # the attractor
    opponent = op.opponent(j)  # player j's opponent
    nbr_func = len(priorities)

    # for each node in the target set U
    for node in U:
        queue.append(node)  # add node to the end of the queue
        regions[node] = j  # set its regions to j (node is winning for j because reachability objective is satisfied)
        W.append(node)  # add the node to the winning region list of j
    if DEBUG_PRINT:
        print(g)
        print("Set " + str(U) + " Player " + str(j) + " Opponent " + str(opponent) + " Prio " + str(priorities))
        print("Marked before start " + str(regions) + " Queue before start " + str(queue))

    # while queue is not empty
    while queue:
        if DEBUG_PRINT: print("     Queue " + str(queue))

        s = queue.popleft()  # remove and return node on the left side of the queue (first in, first out)

        if DEBUG_PRINT: print("     Considering node " + str(s))

        # iterating over the predecessors of node s
        for sbis in g.get_predecessors(s):

            sbis_player = g.get_node_player(sbis)
            # whether sbis has smaller priorities than the provided priority vector.
            # either the priorities are smaller or they are even TODO
            priority_ok = all(g.nodes[sbis][z+1]  % 2 == 0 or g.nodes[sbis][z+1] <= priorities[z] for z in range(nbr_func))


            if DEBUG_PRINT:
                print("         Considering predecessor " + str(sbis) + " Is marked ? " + str(
                    regions[sbis]) + "Player " + str(g.get_node_player(sbis)) + " Priority " + str(
                    g.get_node_priority(sbis)))

            if regions[sbis] == -1:  # if sbis is not yet visited, its region is -1 by default

                if sbis_player == j and priority_ok:

                    if DEBUG_PRINT: print("             Predecessor " + str(sbis) + " Added ")

                    # belongs to j, set regions and strategy accordingly
                    queue.append(sbis)

                    regions[sbis] = j
                    W.append(sbis)

                elif sbis_player == opponent and priority_ok:

                    # belongs to j bar, decrement out. If out is 0, set the region accordingly
                    out[sbis] -= 1

                    if DEBUG_PRINT: print("             Predecessor " + str(sbis) + " Decrement, new count = " +
                                          str(out[sbis]))
                    if out[sbis] == 0:

                        if DEBUG_PRINT: print("             Predecessor " + str(sbis) + " Added ")

                        queue.append(sbis)

                        regions[sbis] = j
                        W.append(sbis)

    # every node that is not marked is not in the attractor, we filter them for speed
    Wbis = filter(lambda x: regions[x] != j, g.nodes.iterkeys())

    if DEBUG_PRINT:
        print("Attractor " + str(W) + " Complement " + str(Wbis))
        print("-------------------------\n")

    return W, Wbis
