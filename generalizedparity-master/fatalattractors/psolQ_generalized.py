from collections import defaultdict, deque
from fatalattractors.attractors import init_out, attractor, attractor_color_vector
from fatalattractors.psolB_generalized import monotone_attractor
from copy import copy
import operations as ops
from graph import Graph

DEBUG_PRINT = False


def psolQ_generalized(g, W1, W2, inverted=False):
    """
    Adaptation of partial solver psolQ for generalized parity games.
    inverted true means we record odd priorities instead of even ones
    :param g: a game graph.
    :return: a partial solution g', W1', W2' in which g is an unsolved sub-game of g and W1', W2' are included in the
    two respective winning regions of g.
    """

    # base case : game is empty
    if g.get_nodes() == []:
        if DEBUG_PRINT: print("Base case return")
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
        even_priorities[func] = filter(lambda x: x % 2 == inverted, priorities[func])  # keep the sorted even priorities

        # if there are no even priorities according to one of the functions, the game is completely won by player 1
        # return empty game and all nodes added to W2
        if len(even_priorities[func]) == 0:
            W2.extend(g.nodes.keys())
            return Graph(), W1, W2

        sizes[func] = len(priorities[func])
        even_sizes[func] = len(even_priorities[func])

    # here we have sorted lists of priorities as well as their sizes

    indexes = [0] * nbr_func  # index for each function to go trough its priorities
    even_indexes = [0] * nbr_func  # index for each function to go trough its priorities

    if DEBUG_PRINT:
        print("Priorities " + str(priorities))
        print("Sizes " + str(sizes))
        print(("Even" if not inverted else "Odd") + " priorities " + str(even_priorities))
        print("Even sizes " + str(even_sizes))

    # TODO instead of doing as above, go through nodes in iterator order and for each node add priorities to the list
    # of priorities and even priorities. Then we work on those unsorted lists. The order is random but it might still
    # work while avoiding to sort the lists.

    # while we have not considered every priority in the game i.e. not gone trough the list of all priorities
    while not all(indexes[w] == sizes[w] for w in range(nbr_func)):

        if DEBUG_PRINT: print("\nPriorities " + str(priorities) + " Indexes " + str(indexes))

        # for each function, treat odd priorities in order in the list until we have reached an even priority
        for i in range(nbr_func):

            if DEBUG_PRINT: print("     odd : function " + str(i))

            # while we can advance in the list and we encounter an odd priority, we consider it
            while indexes[i] < sizes[i] and priorities[i][indexes[i]] % 2 == (not inverted):

                if DEBUG_PRINT:
                    print("           odd : index " + str(indexes[i]) + " element " + str(priorities[i][indexes[i]]))

                # we have an odd priority to consider
                odd_priority = priorities[i][indexes[i]]

                # set of nodes of color 'odd_priority' according to function i+1
                target_set = set(ops.i_priority_node_function_j(g, odd_priority, i + 1))

                # perform fixpoint computation to find fatal attractor for player odd
                # TODO this is PSOLB for player 1, coudl use PSOLQ

                cache = set()

                while cache != target_set and target_set != empty_set:

                    cache = target_set

                    # uses monotone attractor from psolB generalized
                    MA, rest = monotone_attractor(g, target_set, odd_priority, i + 1)

                    if DEBUG_PRINT: print(" MA " + str(MA) + " Player " + str(1) + "\n")

                    if target_set.issubset(MA):

                        if DEBUG_PRINT: print("Set " + str(target_set) + " in MA ")

                        att, complement = attractor(g, MA, 1)

                        W2.extend(att)

                        return psolQ_generalized(g.subgame(complement), W1, W2, inverted)

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
        # call after handling 5 and 3). Also we know that the lists of even priorities are not empty

        if DEBUG_PRINT: print("\nEven indexes " + str(even_indexes) + " Even priorities " + str(even_priorities))

        # if lists of priorities end with odd priorities we may reach this place and no even priorities remain
        # this means we have handled every priorities and can return. Without this, if every even priorities has
        # been handled already we are 'stuck' with the last even priority of each function and keep recomputing with
        # these even priorities even though we have already done it. Since even indexes can only go to even_size[m]-1
        # the element always exists but we should check whether this is reach to prevent computing the same thing
        # over and over. The previous condition stating all(even_sizes[m] == even_indexes[m] for m in range(nbr_func))
        # could not happen as indexes for even don't go up to sizes

        # TODO all below needs to be computed the first time we reach all(even_sizes[m]-1 == even_indexes[m]
        # but not the times after. A solution is to let go the even indexes to even_sizes[m] which is an index that does
        # not exist but put the statement below going to the next iteration every time its true (done with even, only
        # consider odd). Problem : they don't all reach the even_sizes[m] in a synchronised way so one could be too far
        # actually we are done when for all of them they are to even_sizes[m]-1 then we set them all to even_sizes[m]
        # and use the condition below (or even simply a flag).
        # if all(even_sizes[m] == even_indexes[m] for m in range(nbr_func)):
        #    continue

        # we now retrieve the priorities we want to consider in this iteration
        current_priorities = [even_priorities[j][even_indexes[j]] for j in range(nbr_func)]

        if DEBUG_PRINT: print("Even priorities considered " + str(current_priorities) + "\n")

        # now we create the layered fatal attractor for the given current priorities vector

        # set containing nodes of parity 0 or priority below the required one for all functions, used for potential node
        # this is used to create target sets and is refined until reaching a fixpoint in the layered attractor
        # nodes which don't respect this cannot be used as targets
        # TODO this seems weird compared to PSOLQ
        potential_nodes = set(filter(lambda z: all(
            g.nodes[z][u + 1] % 2 == inverted or g.nodes[z][u + 1] <= current_priorities[u] for u in range(nbr_func)),
                                     g.nodes.iterkeys()))

        if DEBUG_PRINT: print("Potential nodes larger than" + str(current_priorities) + " : " + str(potential_nodes))

        cache = set()

        while cache != potential_nodes and potential_nodes != empty_set:

            if DEBUG_PRINT: print("Potential nodes " + str(potential_nodes))

            cache = potential_nodes

            # create the layered attractor, with the even priorities and the even indexes (to compute every layer)
            # and the potential nodes to consider. Yields the layered attractor and the star nodes of the last layer
            MA, rest, star = layered_attractor(g, even_priorities, even_indexes, potential_nodes, inverted)

            # if the potential nodes v are subset of the star, then (v, M(v)) is in the attractor for each target v
            # making it fatal
            if potential_nodes.issubset(star):

                if DEBUG_PRINT: print("Set " + str(potential_nodes) + " in MA ")

                # TODO does star have more nodes than potential_nodes ? I think it's logical that nodes in star are
                # winning, but are there more than in potential and would they have been caught in attractor anyways ?
                att, complement = attractor(g, star, 0)

                W1.extend(att)

                if DEBUG_PRINT:
                    print("TEMP W1 " + str(W1))
                    print("TEMP W2 " + str(W2))
                    print("TEMP REST " + str(complement))

                return psolQ_generalized(g.subgame(complement), W1, W2, inverted)

            else:
                potential_nodes = potential_nodes.intersection(star)

        # we can also advance in the list of even priorities
        for l in range(nbr_func):
            if even_indexes[l] < even_sizes[l] - 1:  # TODO added -1, handle as described above
                even_indexes[l] += 1

    return g, W1, W2


def layered_attractor(g, even_priorities, even_indexes, candidates, inverted=False):
    """
    Computes the layered attractor.
    :param g: a game graph.
    :param even_priorities: the lists of even priorities for each function.
    :param even_indexes: the lists of current indexes of even priorities for each function.
    :param candidates: the candidate nodes used as targets.
    :return: the layered attractor, star nodes of the last layer and complement of layered attractor.
    """

    if DEBUG_PRINT: print("     LAYERED ATT " + "even prios " + str(even_priorities) + "even indexes " + str(
        even_indexes) + "candidates " + str(candidates))

    a = []  # will contain the layered fatal attractor
    not_a = []
    v_star = set()  # star nodes are sets
    nbr_func = g.get_nbr_priority_functions()

    # contrarely to PSOLQ we don't retrieve a min value here for each function, layers with non existing node of the
    # required priorities because of the fixpoint will just be empty

    # we go from the max even priorities to the current even priorities, indexes at zero is the max
    current_indexes = [0] * nbr_func
    lay = 0  # index of the layer

    # TODO we know that at the beginning the nodes with such priorities exist as we take the priorities from the actual
    # nodes but is may not be the case after fixpoint is computed.

    # we then consider vector of even priorities from the maximal one to the current one
    while not all(current_indexes[w] == even_indexes[w] + 1 for w in range(nbr_func)):

        if DEBUG_PRINT: print(
            "     LAYER" + str(lay) + " indexes " + str(even_indexes) + " prios " + str(even_priorities))

        current_priorities = [even_priorities[j][even_indexes[j]] for j in range(nbr_func)]

        # y = set(filter(lambda z: g.get_node_priority(z) >= d, x))  # set containing elements of x with priority >= d

        # we work with sets because doing the union of y (the current target) with a (the previous attractors) can lead
        # to duplicates which means that in the permissive monotone attractor some target node could be considered
        # more than once, leading to errors

        if DEBUG_PRINT: print("     current priorities" + str(current_priorities))

        target = create_target_set(g, current_priorities, candidates, inverted)

        if DEBUG_PRINT: print("     target" + str(target))

        a, not_a = permissive_monotone_attractor(g, v_star, target, current_priorities, inverted)

        # Once a layer a has been computed, check which candidate (i.e. targets) have their (v, M(v)) in that layer.
        # it can happen that a candidate is not in a target but has its (v, M(v)) in the layer TODO check correctness
        new_star = set()
        for nf in candidates:
            if init_memory(g, nf, current_priorities) in a:
                new_star.add(nf)
        v_star = v_star.union(new_star)

        # we can also advance in the list of even priorities
        for l in range(nbr_func):
            # TODO <= instead of < because if index is [0,0] we don't do the iteration added + 1  in the while
            # does it not fail if current_indexes[l] = even_indexes[l]+1 and even index is last of the list .
            if current_indexes[l] <= even_indexes[l]:
                current_indexes[l] += 1

    return a, not_a, v_star


def create_target_set(game, priorities, candidates, inverted=False):
    """
    Create the target set for a specific layer.
    :param game: a game graph.
    :param priorities: the current considered priorities, for this layer.
    :param candidates: the candidate nodes that can be used as target.
    :return: the target set i.e. all nodes which respect the conditions on priorities, with every boolean at True.
    """
    target = []
    nbr_func = len(priorities)
    for node in candidates:
        # nodes with priority larger than what we want to see and odd won't be added to attractor for this layer and we
        # don't want to go to them as it breaks the condition of what we want to see. It follows that they should not
        # be targets. TODO does this influence the fixpoint computation
        if all(game.nodes[node][i + 1] % 2 == inverted or game.nodes[node][i + 1] <= priorities[i] for i in range(nbr_func)):
            target.append((node, tuple([True] * nbr_func)))  # TODO create tuple properly
    return target


def init_memory(g, nf, current_priorities):
    """
    Create the node (nf, M(nf)) given nf and the current priorities for the current layer.
    :param g: a game graph.
    :param nf: a node id.
    :param current_priorities: the current priorities for this layer.
    :return:
    """
    return (nf, tuple([g.nodes[nf][i + 1] >= current_priorities[i] for i in range(g.get_nbr_priority_functions())]))


def create_predecessors(g, node, priorities, v_star, inverted=False):
    """
    Create the predecessors of node (v, M), given the current priorities and the current v_star.
    :param g: a game graph.
    :param node: a nodes (v, M).
    :param priorities: the current priorities.
    :param v_star: the current v_star.
    :return:
    """

    actual_node = node[0]  # node id in original game
    nbr_func = len(priorities)
    candidates = []  # candidates are node ids of predecessors of actual_node which respect a series of properties
    for pre in g.get_predecessors(actual_node):
        # nodes in v star are already handled in the attractor, don't consider them
        if not pre in v_star:
            ok = True
            for i in range(len(priorities)):
                if (g.nodes[pre][i + 1] % 2 == (not inverted) and g.nodes[pre][i + 1] >= priorities[i]) or (
                                (not node[1][i]) and g.nodes[pre][i + 1] >= priorities[i] and g.nodes[pre][
                                i + 1] % 2 == inverted):
                    ok = False
                    break
            if ok:
                candidates.append(pre)
    # print("candidates " + str(candidates))
    # we have v the predecessors valid in candidates
    preds = []
    total = node[1] # the memory of node

    for nod in candidates:
        indices = []
        partial = [False] * nbr_func # default is false for every set
        # handle all possible cases of predecessors, considering the memory and the previously seen priority
        for i in range(nbr_func):
            if total[i]:
                prio_nod = g.get_node_priority_function_i(nod, i + 1)
                if prio_nod >= priorities[i] and prio_nod % 2 == inverted:
                    partial[i] = True
                elif g.get_node_priority_function_i(actual_node, i + 1) < priorities[
                    i] or g.get_node_priority_function_i(actual_node, i + 1) % 2 == (not inverted):
                    partial[i] = True
                else:
                    partial[i] = -1
                    indices.append(i)
        # for each value -1, it must be replaced by True or False and composed into every possibility
        # this generates 2^n possibilities and replaces -1 by every possible combination
        for b in range(0, 1 << len(indices)):
            t = copy(partial)
            for j in range(len(indices)):
                t[indices[j]] = (b & (1 << j)) != 0

            preds.append((nod, tuple(t)))

    return preds


def permissive_monotone_attractor(g, v_star, target_set, current_priorities, inverted=False):
    """
    Attractor for one layer, handling previously computed v_star
    :param g: a game graph.
    :param v_star: the previously computed v_star.
    :param target_set: the target set (nodes with memory).
    :param current_priorities: the current priorities for this layer.
    :return:
    """

    out_base = init_out(g) # init out in base game
    nbr_func = g.get_nbr_priority_functions()
    out = defaultdict(lambda: -1) # this out is used for nodes with memory
    queue = deque()  # init queue (deque is part of standard library and allows O(1) append() and pop() at either end)
    # this dictionary is used to know if a node belongs to a winning region without
    # iterating over both winning regions lists (we can check in O(1) in average)
    regions = defaultdict(lambda: -1)
    W = []  # the attractor
    j = 0  # the player for which we compute the attractor
    opponent = ops.opponent(j)  # player j's opponent

    # in the attractor we won't consider (v, M) such that v is in star, either in predecessors or in target
    star_attractor, not_star_attractor = attractor_color_vector(g, v_star, 0, current_priorities)

    # for each predecessor of nodes in star of the original game, decrement their counter as they have a successor
    # already winning
    for star in star_attractor:
        for pr in g.get_predecessors(star):
            out_base[pr] -= 1

    for node in target_set:
        # todo added 3 june morning because since this was not removed, the out[base] was -1 for node v in star att but
        # then some (v, M) was seen and a further decrement was done
        # only consider targets which are not in star
        if not node[0] in star_attractor:
            queue.append(node)  # add node to the end of the queue

    if DEBUG_PRINT:
        print("--- Monotone attractor ---")
        print(g)
        print("star attractor " + str(star_attractor))
        print("out base " + str(out_base))

        print("Set " + str(target_set) + " Player " + str(j) + " Opponent " + str(opponent) + " Prio " + str(
            current_priorities))
        print("Marked before start " + str(regions) + " Queue before start " + str(queue))

    # while queue is not empty
    while queue:

        if DEBUG_PRINT: print("     Queue " + str(queue))

        s = queue.popleft()  # remove and return node on the left side of the queue (first in, first out)

        if DEBUG_PRINT: print("     Considering node " + str(s))

        # here we need to create the predecessors
        preds = create_predecessors(g, s, current_priorities, star_attractor, inverted)

        # iterating over the predecessors of node s
        for sbis in preds:

            sbis_node = sbis[0]
            sbis_memory = sbis[1]

            # get sbis info sbis = node, memory
            sbis_player = g.get_node_player(sbis_node)
            priority_ok = all(
                g.nodes[sbis_node][z + 1] % 2 == inverted or g.nodes[sbis_node][z + 1] <= current_priorities[z] for z in
                range(nbr_func))

            # TODO verifying that the priorities are correct is done when predecessors are created
            if DEBUG_PRINT:
                print("         Considering predecessor " + str(sbis) + " Is marked ? " + str(regions[sbis]) + "Player "
                      + str(sbis_player) + " Priority " + str(current_priorities))

            if regions[sbis] == -1:  # if sbis is not yet visited, its region is -1 by default

                # if node is the correct player and its priority is lower or equal, add it. If it is in the target set,
                # also consider it even if it breaks the condition on priority.
                # and (sbis_priority <= priority or sbis in target_set)
                # condition on priorities is true
                if sbis_player == j:

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
                # and (sbis_priority <= priority or sbis in target_set)
                elif sbis_player == opponent:

                    if out[sbis] == -1:
                        # first ime, init out
                        out[sbis] = out_base[sbis_node]
                        if DEBUG_PRINT: print("init out node " + str(sbis) + " out " + str(out[sbis]) + " out base " +
                                              str(
                            out_base[sbis_node]))

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


"""
import file_handler as io

g = io.load_generalized_from_file("../examples/example_10.txt")
print g
print(psolQ_generalized(g, [], []))
"""