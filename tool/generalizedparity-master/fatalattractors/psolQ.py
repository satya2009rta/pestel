from collections import deque, defaultdict

import operations as ops
from attractors import init_out, attractor, attractor_color

DEBUG_PRINT = False


def sort_colors_descending(g):
    """
    Sort priorities occurring in the game in descending order of priority.
    :param g: a game graph.
    :return: the colors in g sorted in descending order.
    """

    # (player, priority) is a value of the node dictionary. We create a set of the priorities to remove duplicates
    # then we sort it
    return sorted(set(k[1] for k in g.nodes.itervalues()), reverse=True)


def permissive_monotone_attractor(g, target_set, d):
    """
    Computes the permissive monotone attractor of the given set of nodes. For details, see the paper 'Fatal Attractors
    inParity Games: Building Blocks for Partial Solvers'.
    :param g: a game graph.
    :param target_set: a set of nodes of same parity in g.
    :return:
    """
    priority = d  # priority is given as parameter as there can be several priorities in target set
    out = init_out(g)  # init out
    queue = deque()  # init queue (deque is part of standard library and allows O(1) append() and pop() at either end)
    # this dictionary is used to know if a node belongs to a winning region without
    # iterating over both winning regions lists (we can check in O(1) in average)
    regions = defaultdict(lambda: -1)
    W = []  # the attractor
    j = priority % 2  # the player for which we compute the attractor
    opponent = ops.opponent(j)  # player j's opponent

    for node in target_set:
        queue.append(node)  # add node to the end of the queue

    if DEBUG_PRINT:
        print("--- Monotone attractor ---")
        print(g)
        print("Set " + str(target_set) + " Player " + str(j) + " Opponent " + str(opponent) + " Prio " + str(priority))
        print("Marked before start " + str(regions) + " Queue before start " + str(queue))

    # while queue is not empty
    while queue:

        if DEBUG_PRINT: print("     Queue " + str(queue))

        s = queue.popleft()  # remove and return node on the left side of the queue (first in, first out)

        if DEBUG_PRINT: print("     Considering node " + str(s))

        # iterating over the predecessors of node s
        for sbis in g.get_predecessors(s):

            # get sbis info
            sbis_player = g.get_node_player(sbis)
            sbis_priority = g.get_node_priority(sbis)

            if DEBUG_PRINT:
                print("         Considering predecessor " + str(sbis) + " Is marked ? " + str(regions[sbis]) + "Player "
                      + str(sbis_player) + " Priority " + str(sbis_priority))

            if regions[sbis] == -1:  # if sbis is not yet visited, its region is -1 by default

                # if node is the correct player and its priority is lower or equal, add it. If it is in the target set,
                # also consider it even if it breaks the condition on priority.
                if sbis_player == j and (sbis_priority <= priority or sbis in target_set):

                    if DEBUG_PRINT: print("             Predecessor " + str(sbis) + " Added ")

                    # if node has not been considered yet (not already been in the queue) add it
                    # this is to avoid considering the same node twice, which can happen only for the target node and
                    # can mess up the decrementation of the counters for nodes of the opponent
                    if sbis not in target_set:
                        queue.append(sbis)

                    # mark accordingly and add to winning region
                    regions[sbis] = j
                    W.append(sbis)

                # if node is the opposite player and its priority is lower or equal, check its counter of successors
                # if it is in the target set, also consider it even if it breaks the condition on priority.
                elif sbis_player == opponent and (sbis_priority <= priority or sbis in target_set):

                    # belongs to j bar, decrement out. If out is 0, set the region accordingly
                    out[sbis] -= 1

                    if DEBUG_PRINT: print("             Predecessor " + str(sbis) + " Decrement, new count = " +
                                          str(out[sbis]))

                    if out[sbis] == 0:

                        if DEBUG_PRINT: print("             Predecessor " + str(sbis) + " Added ")

                        # if node has not been considered yet (not already been in the queue) add it
                        if sbis not in target_set:
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


def layered_attractor(g, p, x):
    """
    Constructs a layered attractor for a given parity. Starts with an attractor the maximal priority of that parity
    in the game, then an attractor to the second maximal \cup the previous attractor and so on until we reached the
    minimum priority in x.
    :param g: the game graph.
    :param p: the maximal priority in g of the parity we consider (so the maximum even or odd priority).
    :param x: all nodes in x have parity p % 2.
    :return:
    """

    a = []  # will contain the layered fatal attractor
    not_a = []

    # due to the fact that we create a fixpoint, X might not have nodes of priority color from psolQ
    # in PSOLQ, we compute a fixpoint which means that we might remove nodes from X and it follows that the minimum
    # priority in X is not always know. We need to retrieve it.
    min_in_x = min(g.nodes[z][1] for z in x)

    # we then consider priorities of the same parity from the max p to the min in x
    for d in range(p, min_in_x - 1, -2):
        y = set(filter(lambda z: g.get_node_priority(z) >= d, x))  # set containing elements of x with priority >= d

        # we work with sets because doing the union of y (the current target) with a (the previous attractors) can lead
        # to duplicates which means that in the permissive monotone attractor some target node could be considered
        # more than once, leading to errors

        a_union_y = y.union(a)

        a, not_a = permissive_monotone_attractor(g, a_union_y, d)

    return a, not_a


def psolQ(g, W1, W2):
    """
    Partial solver psolQ for parity games using fatal attractors.
    :param g: a game graph.
    :return: a partial solution g', W1', W2' in which g is an unsolved subgame of g and W1', W2' are included in the
    two respective winning regions of g.
    """

    # base case : game is empty
    if g.get_nodes() == []:
        return g, W1, W2

    # else sort priorities and retrieve maximum even and odd priorities
    colors_descending = sort_colors_descending(g)
    empty_set = set()  # useful later

    if DEBUG_PRINT: print("Colors descending" + str(colors_descending))

    max_prio = colors_descending[0]
    max_prio_player = max_prio % 2

    if max_prio_player == 0:
        max_even = max_prio
        max_odd = max_prio - 1
    if max_prio_player == 1:
        max_even = max_prio - 1
        max_odd = max_prio

    if DEBUG_PRINT:
        print("MAX EVEN " + str(max_even))
        print("MAX ODD " + str(max_odd))

    for color in colors_descending:

        if DEBUG_PRINT: print("Computing for color " + str(color))

        color_player = color % 2

        # set containing nodes of g with priority >= d and parity color_player
        x = set(filter(lambda z: g.get_node_priority(z) % 2 == color_player and g.get_node_priority(z) >= color,
                       g.nodes.iterkeys()))

        if DEBUG_PRINT: print("NODES COLOR BIGGER THAN " + str(color) + " " + str(x))

        cache = set()

        while cache != x and x != empty_set:

            if DEBUG_PRINT: print("SET X" + str(x))

            cache = x

            if color_player == 0:
                MA, rest = layered_attractor(g, max_even, x)
            else:
                MA, rest = layered_attractor(g, max_odd, x)

            if DEBUG_PRINT: print(" MA " + str(MA) + " Player " + str(g.get_node_player(x[0])) + "\n")

            if x.issubset(MA):

                if DEBUG_PRINT: print("Set " + str(x) + " in MA ")

                att, complement = attractor(g, MA, color_player)

                if color % 2 == 0:
                    W1.extend(att)
                else:
                    W2.extend(att)

                if DEBUG_PRINT:
                    print("TEMP W1 " + str(W1))
                    print("TEMP W2 " + str(W2))
                    print("TEMP REST " + str(complement))

                return psolQ(g.subgame(complement), W1, W2)

            else:
                x = x.intersection(MA)

    return g, W1, W2


def psolQ_classical_attractor(g, W1, W2):
    """
    Partial solver psolQ for parity games using fatal attractors. This implementation uses classical attractors, where
    the nodes in the target set are in the attractor by default.
    :param g: a game graph.
    :return: a partial solution g', W1', W2' in which g is an unsolved subgame of g and W1', W2' are included in the
    two respective winning regions of g.
    """

    # base case : game is empty
    if g.get_nodes() == []:
        return g, W1, W2

    # else sort priorities and retrieve maximum even and odd priorities
    colors_descending = sort_colors_descending(g)
    empty_set = set()  # useful later

    if DEBUG_PRINT: print("Colors descending" + str(colors_descending))

    max_prio = colors_descending[0]
    max_prio_player = max_prio % 2

    if max_prio_player == 0:
        max_even = max_prio
        max_odd = max_prio - 1
    if max_prio_player == 1:
        max_even = max_prio - 1
        max_odd = max_prio

    if DEBUG_PRINT:
        print("MAX EVEN " + str(max_even))
        print("MAX ODD " + str(max_odd))

    for color in colors_descending:

        if DEBUG_PRINT: print("Computing for color " + str(color))

        color_player = color % 2

        # set containing nodes of g with priority >= d and parity color_player
        x = set(filter(lambda z: g.get_node_priority(z) % 2 == color_player and g.get_node_priority(z) >= color,
                       g.nodes.iterkeys()))

        if DEBUG_PRINT: print("NODES COLOR BIGGER THAN " + str(color) + " " + str(x))

        cache = set()

        while cache != x and x != empty_set:

            if DEBUG_PRINT: print("SET X" + str(x))

            cache = x

            if color_player == 0:
                MA, rest = layered_classical_attractor(g, max_even, x)
            else:
                MA, rest = layered_classical_attractor(g, max_odd, x)

            if DEBUG_PRINT: print(" MA " + str(MA) + " Player " + str(g.get_node_player(x[0])) + "\n")

            # Here instead of check for inclusion of the target set x in the attractor MA we consider the nodes in x and
            # check wether they can force for the correct player to go back in the attractor. We can't simply check for
            # inclusion of x in MA since in this version the target set x is added de facto in the attractor
            # we also can't put this step directly inside the attractor, by checking for inclusion of the target set in
            # the attractor because here we check the inclusion in the layered attractor and not in the attractor at a
            # specific step

            is_ok = True

            # create a new version of x which only contains the node in x from which player color_player can ensure to
            # reach MA
            x_new = set()

            # for each node in x
            for node in x:

                # if node belongs to color player, it needs to have one successor in MA
                if g.get_node_player(node) == color_player:
                    for succ in g.get_successors(node):
                        if succ in MA:
                            x_new.add(node)
                            break
                else:
                    # if node belongs to other player, all its successors must be in MA
                    found = True  # does the node have all of its successors in MA
                    for succ in g.get_successors(node):
                        if not (succ in MA):
                            # we have found a successor not in MA
                            found = False
                            break
                    if found:
                        x_new.add(node)

            # if the length of x is different than the length of x_new, we have removed nodes from x and need to
            # continue. Else, the attractor is fatal
            if len(x) != len(x_new):
                is_ok = False

            # replace x by x_new, no intersection with MA can be done per above reasons, but intersection with MA
            # is done implicitly i.e. x_new is actually the intersection
            x = x_new

            if is_ok:

                # attractor is fatal

                if DEBUG_PRINT: print("Set " + str(x) + " in MA ")

                att, complement = attractor(g, MA, color_player)

                if color_player == 0:
                    W1.extend(att)
                else:
                    W2.extend(att)

                if DEBUG_PRINT:
                    print("TEMP W1 " + str(W1))
                    print("TEMP W2 " + str(W2))
                    print("TEMP REST " + str(complement))

                return psolQ_classical_attractor(g.subgame(complement), W1, W2)

    return g, W1, W2


def layered_classical_attractor(g, p, x):
    """
    Constructs a layered attractor for a given parity. Starts with an attractor the maximal priority of that parity
    in the game, then an attractor to the second maximal \cup the previous attractor and so on until we reached the
    minimum priority in x. Attractors used here are classical in the sense that the target set is included in the
    attractor by default, as opposed to the attractor version where it is added during computation.
    :param g: the game graph.
    :param p: the maximal priority in g of the parity we consider (so the maximum even or odd priority).
    :param x: all nodes in x have parity p % 2.
    :return:
    """

    a = []  # will contain the layered fatal attractor
    not_a = []

    # due to the fact that we create a fixpoint, X might not have nodes of priority color from psolQ
    # in PSOLQ, we compute a fixpoint which means that we might remove nodes from X and it follows that the minimum
    # priority in X is not always know. We need to retrieve it.
    min_in_x = min(g.nodes[z][1] for z in x)

    # we then consider priorities of the same parity from the max p to the min in x
    for d in range(p, min_in_x - 1, -2):
        # TODO this is Yd and not Y <= d or >= d because in classical attractor the nodes of colors larger than d would
        # not be considered by the condition which states color must be <= d. To allow larger colors we need to add the
        # condition which states that colors <= d OR node is in the target set, as done in the permissive monotone att
        y = set(filter(lambda z: g.get_node_priority(z) == d, x))  # set containing elements of x with priority >= d

        # we work with sets because doing the union of y (the current target) with a (the previous attractors) can lead
        # to duplicates which means that in the permissive monotone attractor some target node could be considered
        # more than once, leading to errors

        a_union_y = y.union(a)

        a, not_a = attractor_color(g, a_union_y, d % 2, d)

    return a, not_a
