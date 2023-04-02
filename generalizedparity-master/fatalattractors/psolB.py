from collections import deque, defaultdict

import operations as ops

import buchi.buchi_inter_cobuchi as cobuchi
import buchi.buchi_inter_safety as safety
from attractors import init_out, attractor

DEBUG_PRINT = False


def sort_colors_ascending(g):
    """
    Sort priorities occurring in the game in ascending order of priority.
    :param g: a game graph.
    :return: the colors in g sorted in ascending order.
    """

    # (player, priority) is a value of the node dictionary. We create a set of the priorities to remove duplicates
    # then we sort it
    return sorted(set(k[1] for k in g.nodes.itervalues()))


def monotone_attractor_including_target(g, target_set, color):
    """
    Computes the monotone attractor of the target set, meaning the attractor without visiting bigger priorities than
    the one of the target set. This implementation adds the target set in the attractor at the start and checks during
    computation if the nodes of that target set would have been added to the attractor had they not been added at the
    start. This differs from the usual implementation which does not add the target set to the attractor at the start.
    In theory, this should allow us a quicker check of inclusion of the target set in the attractor.
    :param g: a game graph.
    :param target_set: a target set of nodes.
    :param color: the color of the nodes in target set.
    :return: W, in_att, Wbis the attractor, a dictionary of which nodes in the target set are in the attractor and the
    nodes which are not in the attractor.
    """

    p = color  # priority of the node gives us the player for which we compute the attractor
    out = init_out(g)  # init out
    queue = deque()  # init queue (deque is part of standard library and allows O(1) append() and pop() at either end)
    # this dictionary is used to know if a node belongs to a winning region without
    # iterating over both winning regions lists (we can check in O(1) in average)
    regions = defaultdict(lambda: -1)
    W = []  # the attractor
    j = p % 2  # the player for which we compute the attractor
    opponent = ops.opponent(j)  # player j's opponent

    in_att = defaultdict(lambda: 0)

    # for each node in the target set U
    for node in target_set:
        queue.append(node)  # add node to the end of the queue
        regions[node] = j  # set its regions to j (node is winning for j because reachability objective is satisfied)
        W.append(node)  # add the node to the winning region list of j

    if DEBUG_PRINT:
        print(g)
        print("Set " + str(target_set) + " Player " + str(j) + " Opponent " + str(opponent) + " Prio " + str(p))
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

            # if the predecessor is in the target set
            # TODO here instead of in, we can use a special value in the regions dictionnary for nodes in target
            # set for quicker check, if so we also need to modify Wbis computation to take this into account
            if sbis in target_set:

                # if it belongs to player 1, sbis is in the attractor so we mark it
                if sbis_player == j:
                    in_att[sbis] = 1

                # else  we decrement its out value, and when it is 0 we mark it
                else:
                    out[sbis] -= 1
                    if out[sbis] == 0:
                        in_att[sbis] = 1

            if regions[sbis] == -1:  # if sbis is not yet visited, its region is -1 by default

                if sbis_player == j and sbis_priority <= p:

                    if DEBUG_PRINT: print("             Predecessor " + str(sbis) + " Added ")

                    # belongs to j, set regions and strategy accordingly
                    queue.append(sbis)
                    regions[sbis] = j
                    W.append(sbis)

                elif sbis_player == opponent and sbis_priority <= p:
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

    return W, in_att, Wbis


def monotone_attractor(g, target_set, color):
    """
    Computes the monotone attractor of the target set, meaning the attractor without visiting bigger priorities than
    the one of the target set.
    :param g: a game graph.
    :param target_set: a target set of nodes.
    :param color: the color of the nodes in target set.
    :return: W, Wbis the attractor and the nodes which are not in the attractor.
    """

    priority = color  # priority of the node gives us the player for which we compute the attractor
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

                # if node is the correct player and its priority is lower or equal, add it
                if sbis_player == j and sbis_priority <= priority:

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
                elif sbis_player == opponent and sbis_priority <= priority:

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


def psolB(g, W1, W2):
    """
    Partial solver psolB for parity games using fatal attractors.
    :param g: a game graph.
    :return: a partial solution g', W1', W2' in which g is an unsolved subgame of g and W1', W2' are included in the
    two respective winning regions of g.
    """

    for color in sort_colors_ascending(g):

        if DEBUG_PRINT: print("Computing for color " + str(color))

        target_set = ops.i_priority_node(g, color)  # set of nodes of color 'color'

        cache = set()

        # TODO check list comparison efficiency
        while cache != set(target_set) and target_set != []:

            cache = target_set

            MA, rest = monotone_attractor(g, target_set, color)

            if DEBUG_PRINT: print(" MA " + str(MA) + " Player " + str(g.get_node_player(target_set[0])) + "\n")

            if set(target_set).issubset(MA):

                if DEBUG_PRINT: print("Set " + str(target_set) + " in MA ")

                att, complement = attractor(g, MA, color % 2)

                if color % 2 == 0:
                    W1.extend(att)
                else:
                    W2.extend(att)

                return psolB(g.subgame(complement), W1, W2)

            else:
                target_set = list(set(target_set).intersection(set(MA)))

    return g, W1, W2


def psolB_set(g, W1, W2):
    """
    Partial solver psolB for parity games using fatal attractors. Implementation using sets.
    :param g: a game graph.
    :return: a partial solution g', W1', W2' in which g is an unsolved subgame of g and W1', W2' are included in the
    two respective winning regions of g.
    """

    empty_set = set()

    for color in sort_colors_ascending(g):

        if DEBUG_PRINT: print("Computing for color " + str(color))

        target_set = set(ops.i_priority_node(g, color))  # set of nodes of color 'color'

        cache = set()

        while cache != target_set and target_set != empty_set:

            cache = target_set

            MA, rest = monotone_attractor(g, target_set, color)

            if DEBUG_PRINT: print(" MA " + str(MA) + " Player " + str(g.get_node_player(target_set[0])) + "\n")

            if target_set.issubset(MA):

                if DEBUG_PRINT: print("Set " + str(target_set) + " in MA ")

                att, complement = attractor(g, MA, color % 2)

                if color % 2 == 0:
                    W1.extend(att)
                else:
                    W2.extend(att)

                return psolB_set(g.subgame(complement), W1, W2)

            else:
                target_set = target_set.intersection(MA)

    return g, W1, W2


def psolB_modified_att(g, W1, W2):
    """
    Partial solver psolB for parity games using fatal attractors. Implementation using a variant of attractors.
    :param g: a game graph.
    :return: a partial solution g', W1', W2' in which g is an unsolved subgame of g and W1', W2' are included in the
    two respective winning regions of g.
    """

    for color in sort_colors_ascending(g):

        if DEBUG_PRINT: print("Computing for color " + str(color))

        target_set = ops.i_priority_node(g, color)  # set of nodes of color 'color'

        cache = set()

        # TODO check list comparison efficiency
        while cache != set(target_set) and target_set != []:

            cache = target_set

            MA, in_att, rest = monotone_attractor_including_target(g, target_set, color)

            if DEBUG_PRINT: print(" MA " + str(MA) + " Player " + str(g.get_node_player(target_set[0])) + "\n")

            # if the sum of values is the length of the target set, every node in target is in the attractor
            if sum(in_att.itervalues()) == len(target_set):

                if DEBUG_PRINT: print("Set " + str(target_set) + " in MA ")

                att, complement = attractor(g, MA, color % 2)

                if color % 2 == 0:
                    W1.extend(att)
                else:
                    W2.extend(att)

                return psolB_modified_att(g.subgame(complement), W1, W2)

            else:
                # only keep in target the target nodes that are included in the attractor
                target_set = filter(lambda x: in_att[x] == 1, in_att.iterkeys())

    return g, W1, W2


def psolB_buchi_cobuchi(g, W1, W2):
    """
    Partial solver psolB for parity games. This implementation uses buchi inter co-buchi to find fatal attractors.
    :param g: a game graph.
    :return: a partial solution g', W1', W2' in which g is an unsolved subgame of g and W1', W2' are included in the
    two respective winning regions of g.
    """

    for color in sort_colors_ascending(g):

        if DEBUG_PRINT: print("Computing for color " + str(color))

        target_set = ops.i_priority_node(g, color)  # set of nodes of color 'color'

        # TODO here replace previous call by a call which goes through each node and add it to in/out set of color i
        # we only go trough every node once and add it to greater than color or of priority color

        # record the nodes we don't want to see infinitely often i.e. the ones with greater priority than color
        not_target_set_bigger = []
        for node in g.nodes.iterkeys():
            if g.get_node_priority(node) > color:
                not_target_set_bigger.append(node)

        # winning region of buchi inter co-buchi for player color % 2
        w = cobuchi.buchi_inter_cobuchi_player(g, target_set, not_target_set_bigger, color % 2)

        if DEBUG_PRINT: print(" MA " + str(w) + " Player " + str(g.get_node_player(target_set[0])) + "\n")

        if w != []:

            if DEBUG_PRINT: print("Set " + str(target_set) + " in MA ")

            att, complement = attractor(g, w, color % 2)

            if color % 2 == 0:
                W1.extend(att)
            else:
                W2.extend(att)

            return psolB_buchi_cobuchi(g.subgame(complement), W1, W2)

    return g, W1, W2


def psolB_buchi_safety(g, W1, W2):
    """
    Partial solver psolB for parity games. This implementation uses buchi inter safety to find fatal attractors.
    :param g: a game graph.
    :return: a partial solution g', W1', W2' in which g is an unsolved subgame of g and W1', W2' are included in the
    two respective winning regions of g.
    """

    for color in sort_colors_ascending(g):

        if DEBUG_PRINT: print("Computing for color " + str(color))

        target_set = ops.i_priority_node(g, color)  # set of nodes of color 'color'

        # TODO here replace previous call by a call which goes through each node and add it to in/out set of color i
        # we only go trough every node once and add it to greater than color or of priority color

        # record the nodes we don't want to see infinitely often i.e. the ones with greater priority than color
        not_target_set_bigger = []
        for node in g.nodes.iterkeys():
            if g.get_node_priority(node) > color:
                not_target_set_bigger.append(node)

        # winning region of buchi inter safety for player color % 2
        w = safety.buchi_inter_safety_player(g, target_set, not_target_set_bigger, color % 2)

        if DEBUG_PRINT: print(" MA " + str(w) + " Player " + str(g.get_node_player(target_set[0])) + "\n")

        if w != []:

            if DEBUG_PRINT: print("Set " + str(target_set) + " in MA ")

            att, complement = attractor(g, w, color % 2)

            if color % 2 == 0:
                W1.extend(att)
            else:
                W2.extend(att)

            return psolB_buchi_safety(g.subgame(complement), W1, W2)

    return g, W1, W2
