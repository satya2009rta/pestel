from collections import deque, defaultdict
import operations as ops
from buchi import generalized_buchi_inter_safety
from attractors import init_out, attractor
from graph import Graph

DEBUG_PRINT = False


def monotone_attractor(g, target_set, color, func):
    """
    Computes the monotone attractor of the target set, meaning the attractor without visiting bigger priorities than
    the one of the target set.
    :param g: a game graph.
    :param target_set: a target set of nodes.
    :param color: the color of the nodes in target set.
    :param func: the priority function we consider.
    :return: W, Wbis the attractor and the nodes which are not in the attractor.
    """

    priority = color  # priority of the node gives us the player for which we compute the attractor
    out = init_out(g)  # init out
    queue = deque()  # init queue (deque is part of standard library and allows O(1) append() and pop() at either end)
    # this dictionary is used to know if a node belongs to a winning region without
    # iterating over both winning regions lists (we can check in O(1) in average)
    regions = defaultdict(lambda: -1)
    W = []  # the attractor
    j = 1  # the player for which we compute the attractor
    opponent = 0  # player j's opponent

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
            sbis_priority = g.get_node_priority_function_i(sbis, func)

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


def even_tuples_iterator(depth, priorities, sizes, li, k, t):
    """
    Iterate over the k-uples consisting of even priorities.
    :param depth:
    :param priorities:
    :param sizes:
    :param list:
    :param k:
    :param t:
    :return:
    """

    if DEBUG_PRINT:
        print("----------------------------")
        print(depth)
        print(priorities)
        print(sizes)
        print(li)
        print(enumerate(li))
        print(k)
        print(t)

    if depth == 0:
        yield [priorities[index][element] for index, element in enumerate(li)]

    else:
        for i in range(t, k):
            li[i] += 1
            if not li[i] >= sizes[i]:
                for j in even_tuples_iterator(depth - 1, priorities, sizes, li, k, i):
                    yield j
            li[i] -= 1


def psolB_generalized(g, W1, W2):
    """
    Adaptation of partial solver psolB for generalized parity games.
    :param g: a game graph.
    :return: a partial solution g', W1', W2' in which g is an unsolved subgame of g and W1', W2' are included in the
    two respective winning regions of g.
    """

    # base case : game is empty
    if g.get_nodes() == []:
        return g, W1, W2

    # else retrieve useful information on the game
    nbr_func = g.get_nbr_priority_functions()  # number of functions
    priorities = [[] for z in xrange(nbr_func)]  # setup list containing list of priorities for each function
    even_priorities = [[] for z in xrange(nbr_func)]  # setup list containing list of even priorities for each function
    sizes = [0] * nbr_func  # setup the sizes for the lists of priorities
    even_sizes = [0] * nbr_func  # setup the sizes for the lists of even priorities
    empty_set = set()  # useful when computing fatal attractor for player 1

    # first, retrieve all priorities and put them in the lists of priorities for each function
    for node in g.nodes.iterkeys():
        for func in range(nbr_func):
            priorities[func].append(g.get_node_priority_function_i(node, func + 1))  # function are numbered 1 to k

    # sort priorities and create the lists containing only the even priorities
    for func in range(nbr_func):
        # TODO we transform into set to remove duplicate, might check itertools, ordered dicts and heaps also
        priorities[func] = sorted(set(priorities[func]), reverse=True)  # change into set to remove duplicates and sort
        even_priorities[func] = filter(lambda x: x % 2 == 0, priorities[func])

        # if there are no even priorities according to one of the functions, the game is completely won by player 1
        # return empty game and all nodes added to W2
        if len(even_priorities[func]) == 0:
            W2.extend(g.nodes.keys())
            return Graph(), W1, W2

        sizes[func] = len(priorities[func])
        even_sizes[func] = len(even_priorities[func])

    # here we have sorted lists of priorities as well as their sizes

    indexes = [0] * nbr_func  # index for each function to go trough its priorities
    depth = 0  # depth is needed for the level of the lattice
    max_size = max(even_sizes)  # needed for the maximum level of the lattice

    if DEBUG_PRINT:
        print("priorities " + str(priorities))
        print("even priorities " + str(even_priorities))
        print("sizes " + str(sizes))
        print("depth " + str(depth))
        print("max_size " + str(max_size))

    # TODO instead of doing as above, go through nodes in iterator order and for each node add priorities to the list
    # of priorities and even priorities. Then we work on those unsorted lists. The order is random but it might still
    # work while avoiding to sort the lists.

    # while we have not considered every couple of the lattice i.e. not reached the maximal depth for the levels in
    # the lattice for the even priorities or we have not considered every priority in the list of priorities
    while (not all(indexes[w] == sizes[w] for w in range(nbr_func))) or (depth != max_size + 2):

        if DEBUG_PRINT: print("iteration " + str(depth) + " indexes " + str(indexes))

        # for each function, we treat odd priorities in order in the list until we have reached an even priority
        for i in range(nbr_func):

            if DEBUG_PRINT: print("     function " + str(i))

            # while we can advance in the list and we encounter an odd priority, we consider it
            while indexes[i] < sizes[i] and priorities[i][indexes[i]] % 2 == 1:

                if DEBUG_PRINT:
                    print("           index " + str(indexes[i]) + " element " + str(priorities[i][indexes[i]]))
                    print("           fonction " + str(i + 1) + " " + str(priorities[i][indexes[i]]))

                # we have an odd priority to consider
                odd_priority = priorities[i][indexes[i]]

                # set of nodes of color 'odd_priority' according to function i+1
                target_set = set(ops.i_priority_node_function_j(g, odd_priority, i + 1))

                # perform fixpoint computation to find fatal attractor for player odd

                cache = set()

                while cache != target_set and target_set != empty_set:

                    cache = target_set

                    MA, rest = monotone_attractor(g, target_set, odd_priority, i + 1)

                    if DEBUG_PRINT: print(" MA " + str(MA) + " Player " + str(1) + "\n")

                    if target_set.issubset(MA):

                        if DEBUG_PRINT: print("Set " + str(target_set) + " in MA ")

                        att, complement = attractor(g, MA, 1)

                        W2.extend(att)

                        return psolB_generalized(g.subgame(complement), W1, W2)

                    else:
                        target_set = target_set.intersection(MA)

                # if we have not found a fatal attractor, we go forward in the list and restart the same logic until
                # reaching an even priority or the end of the list
                indexes[i] += 1

            # we have found an even priority at position indexes[i], at next iteration of the outer while, we restart
            # from the next index in the list
            if indexes[i] < sizes[i]:
                indexes[i] += 1

        # when this is reached, we know we have handled every odd priorities until reaching an even priority for each
        # function i.e. if [5,3,4,1,0] and [2,1,0] are the priorities, after first iteration of outer while we have
        # handled 5, 3 and reached 4 in the first list and reached 2 in the second (assuming there was no recursive
        # call after handling 5 and 3).

        # TODO if we have gone trough the whole list for each function, player 2 wins ? i.e. index is list size for each
        # TODO bug : sometimes there are no even priorities according to some function : even_tuples_iterator bugs
        # go through every k-uple of even priorities in the current level
        for kuple in even_tuples_iterator(depth, even_priorities, even_sizes, [0] * nbr_func, nbr_func, 0):

            if DEBUG_PRINT: print("     " + str(kuple))

            # we now will compute a generalized buchi inter safety game
            avoid = []  # nodes for the safety game, to be avoided
            sets_gen = [[] for z in xrange(nbr_func)]  # sets of nodes to be visited infinitely often

            for nod in g.nodes.iterkeys():

                flag = False  # is the node to be avoided (greater priority than required for some function)

                # for each function
                for f in range(1, nbr_func + 1):

                    # priority of the node according to that function
                    prio = g.get_node_priority_function_i(nod, f)

                    if DEBUG_PRINT:
                        print("          " + str(prio))
                        print("          " + str(prio % 2 == 1) + " " + str(prio > kuple[f - 1]))

                    # priority is odd and greater than the corresponding one in the k-uple, we want to avoid the node
                    if prio % 2 == 1 and prio > kuple[f - 1]:
                        flag = True
                    # else if the priority is the one we want to see, add it to the set to be visited infinitely often
                    elif prio == kuple[f - 1]:
                        sets_gen[f - 1].append(nod)

                # if the flag is true, we don't want to see this node
                if flag:
                    avoid.append(nod)

            if DEBUG_PRINT:
                print("sets " + str(sets_gen))
                print("avoid " + str(avoid))

            # solution of the generalized buchi inter safety game
            win = generalized_buchi_inter_safety.generalized_buchi_inter_safety(g, sets_gen, avoid)

            if DEBUG_PRINT:
                print(g)
                print("=========================== win " + str(win))

            # if we have some winning region
            if len(win) != 0:
                att2, comp = attractor(g, win, 0)
                W1.extend(att2)
                return psolB_generalized(g.subgame(comp), W1, W2)

        depth += 1

    return g, W1, W2


def psolB_generalized_inline(g, W1, W2):
    """
    Adaptation of partial solver psolB for generalized parity games. This implementation uses inline version of
    generalized buchi inter safety games.
    :param g: a game graph.
    :return: a partial solution g', W1', W2' in which g is an unsolved subgame of g and W1', W2' are included in the
    two respective winning regions of g.
    """

    # base case : game is empty
    if g.get_nodes() == []:
        return g, W1, W2

    # else retrieve useful information on the game
    nbr_func = g.get_nbr_priority_functions()  # number of functions
    priorities = [[] for z in xrange(nbr_func)]  # setup list containing list of priorities for each function
    even_priorities = [[] for z in xrange(nbr_func)]  # setup list containing list of even priorities for each function
    sizes = [0] * nbr_func  # setup the sizes for the lists of priorities
    even_sizes = [0] * nbr_func  # setup the sizes for the lists of even priorities
    empty_set = set()  # useful when computing fatal attractor for player 1

    # first, retrieve all priorities and put them in the lists of priorities for each function
    for node in g.nodes.iterkeys():
        for func in range(nbr_func):
            priorities[func].append(g.get_node_priority_function_i(node, func + 1))  # function are numbered 1 to k

    # sort priorities and create the lists containing only the even priorities
    for func in range(nbr_func):
        # TODO we transform into set to remove duplicate, might check itertools, ordered dicts and heaps also
        priorities[func] = sorted(set(priorities[func]), reverse=True)  # change into set to remove duplicates and sort
        even_priorities[func] = filter(lambda x: x % 2 == 0, priorities[func])

        # if there are no even priorities according to one of the functions, the game is completely won by player 1
        # return empty game and all nodes added to W2
        if len(even_priorities[func]) == 0:
            W2.extend(g.nodes.keys())
            return Graph(), W1, W2

        sizes[func] = len(priorities[func])
        even_sizes[func] = len(even_priorities[func])

    # here we have sorted lists of priorities as well as their sizes

    indexes = [0] * nbr_func  # index for each function to go trough its priorities
    depth = 0  # depth is needed for the level of the lattice
    max_size = max(even_sizes)  # needed for the maximum level of the lattice

    if DEBUG_PRINT:
        print("priorities " + str(priorities))
        print("even priorities " + str(even_priorities))
        print("sizes " + str(sizes))
        print("depth " + str(depth))
        print("max_size " + str(max_size))

    # TODO instead of doing as above, go through nodes in iterator order and for each node add priorities to the list
    # of priorities and even priorities. Then we work on those unsorted lists. The order is random but it might still
    # work while avoiding to sort the lists.

    # while we have not considered every couple of the lattice i.e. not reached the maximal depth for the levels in
    # the lattice for the even priorities or we have not considered every priority in the list of priorities
    while (not all(indexes[w] == sizes[w] for w in range(nbr_func))) or (depth != max_size + 2):

        if DEBUG_PRINT: print("iteration " + str(depth) + " indexes " + str(indexes))

        # for each function, we treat odd priorities in order in the list until we have reached an even priority
        for i in range(nbr_func):

            if DEBUG_PRINT: print("     function " + str(i))

            # while we can advance in the list and we encounter an odd priority, we consider it
            while indexes[i] < sizes[i] and priorities[i][indexes[i]] % 2 == 1:

                if DEBUG_PRINT:
                    print("           index " + str(indexes[i]) + " element " + str(priorities[i][indexes[i]]))
                    print("           fonction " + str(i + 1) + " " + str(priorities[i][indexes[i]]))

                # we have an odd priority to consider
                odd_priority = priorities[i][indexes[i]]

                # set of nodes of color 'odd_priority' according to function i+1
                target_set = set(ops.i_priority_node_function_j(g, odd_priority, i + 1))

                # perform fixpoint computation to find fatal attractor for player odd

                cache = set()

                while cache != target_set and target_set != empty_set:

                    cache = target_set

                    MA, rest = monotone_attractor(g, target_set, odd_priority, i + 1)

                    if DEBUG_PRINT: print(" MA " + str(MA) + " Player " + str(1) + "\n")

                    if target_set.issubset(MA):

                        if DEBUG_PRINT: print("Set " + str(target_set) + " in MA ")

                        att, complement = attractor(g, MA, 1)

                        W2.extend(att)

                        return psolB_generalized_inline(g.subgame(complement), W1, W2)

                    else:
                        target_set = target_set.intersection(MA)

                # if we have not found a fatal attractor, we go forward in the list and restart the same logic until
                # reaching an even priority or the end of the list
                indexes[i] += 1

            # we have found an even priority at position indexes[i], at next iteration of the outer while, we restart
            # from the next index in the list
            if indexes[i] < sizes[i]:
                indexes[i] += 1

        # when this is reached, we know we have handled every odd priorities until reaching an even priority for each
        # function i.e. if [5,3,4,1,0] and [2,1,0] are the priorities, after first iteration of outer while we have
        # handled 5, 3 and reached 4 in the first list and reached 2 in the second (assuming there was no recursive
        # call after handling 5 and 3).

        # TODO if we have gone trough the whole list for each function, player 2 wins ? i.e. index is list size for each
        # TODO bug : sometimes there are no even priorities according to some function : even_tuples_iterator bugs
        # go through every k-uple of even priorities in the current level
        for kuple in even_tuples_iterator(depth, even_priorities, even_sizes, [0] * nbr_func, nbr_func, 0):

            if DEBUG_PRINT: print("     " + str(kuple))

            # we now will compute a generalized buchi inter safety game
            avoid = []  # nodes for the safety game, to be avoided
            sets_gen = [[] for z in xrange(nbr_func)]  # sets of nodes to be visited infinitely often

            for nod in g.nodes.iterkeys():

                flag = False  # is the node to be avoided (greater priority than required for some function)

                # for each function
                for f in range(1, nbr_func + 1):

                    # priority of the node according to that function
                    prio = g.get_node_priority_function_i(nod, f)

                    if DEBUG_PRINT:
                        print("          " + str(prio))
                        print("          " + str(prio % 2 == 1) + " " + str(prio > kuple[f - 1]))

                    # priority is odd and greater than the corresponding one in the k-uple, we want to avoid the node
                    if prio % 2 == 1 and prio > kuple[f - 1]:
                        flag = True
                    # else if the priority is the one we want to see, add it to the set to be visited infinitely often
                    elif prio == kuple[f - 1]:
                        sets_gen[f - 1].append(nod)

                # if the flag is true, we don't want to see this node
                if flag:
                    avoid.append(nod)

            if DEBUG_PRINT:
                print("sets " + str(sets_gen))
                print("avoid " + str(avoid))

            # solution of the generalized buchi inter safety game
            win = generalized_buchi_inter_safety.inlined_generalized_buchi_inter_safety(g, sets_gen, avoid)

            if DEBUG_PRINT:
                print(g)
                print("=========================== win " + str(win))

            # if we have some winning region
            if len(win) != 0:
                att2, comp = attractor(g, win, 0)
                W1.extend(att2)
                return psolB_generalized_inline(g.subgame(comp), W1, W2)

        depth += 1

    return g, W1, W2


"""
import file_handler as io
g = io.load_generalized_from_file("../examples/example_10.txt")
print g
print(psolB_generalized_inline(g, [], []))
print("===============================================================================")
print(psolB_generalized_inline_odd(g, [], []))
"""