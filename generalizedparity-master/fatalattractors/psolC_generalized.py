import copy

from antichain import Antichain
from graph import Graph
import operations
from collections import deque, defaultdict
from attractors import init_out, attractor

DEBUG_PRINT = False


# TODO careful of aliases on the values in the lists, changing one somewhere might change another somewhere else

# The following functions are cced and adapted from psolC


def R_set_func(g, func, target_set, j):
    """
    We compute the attractor of a set of node-priority pairs where the priority
    represents the maximal priority seen so far.
    """
    ascending_priorities = g.get_sorted_priorities_func(func)
    v_out = init_out(g)  # a counter for visited edges from each vertex
    out = {(v, p): v_out[v] for v in g.get_nodes()
           for p in ascending_priorities}
    regions = defaultdict(lambda: -1)
    adversary = operations.opponent(j)

    # we keep a queue of newly found winning vertex-priority pairs
    queue = deque(target_set)
    while queue:
        (node, priority) = queue.popleft()
        for pred in g.get_predecessors(node):
            pred_player = g.get_node_player(pred)
            pred_priority = g.get_node_priority_function_i(pred, func)
            if pred_priority > priority:
                continue  # cannot be a predecessor
            if priority > g.get_node_priority_function_i(node, func):
                options = [priority]
            else:
                assert (priority == g.get_node_priority_function_i(node, func))
                options = filter(lambda x: x >= pred_priority and
                                           x <= priority, ascending_priorities)
                assert (len(options) > 0)
            for p in options:
                if regions[(pred, p)] == -1:  # vertex-priority is undecided
                    if pred_player == j:
                        regions[(pred, p)] = j
                        if (pred, p) not in target_set:
                            queue.append((pred, p))
                    elif pred_player == adversary:
                        out[(pred, p)] -= 1
                        if out[(pred, p)] == 0:
                            regions[(pred, p)] = j
                            if (pred, p) not in target_set:
                                queue.append((pred, p))
    # prepare output
    W = set()
    for n in g.get_nodes():
        if regions[(n, g.get_node_priority_function_i(n, func))] == j:
            W.add(n)
    return W


def jfs_algo_func(g, func, j):
    assert (j == 0 or j == 1)
    j_priorities = filter(lambda x: (x % 2) == j,
                          g.get_sorted_priorities_func(func))
    T = set([(v, p) for v in g.get_nodes()
             for p in filter(lambda x: x >= g.get_node_priority_function_i(v, func),
                             j_priorities)])
    next_F = R_set_func(g, func, T, j)
    F = set()
    while next_F != F:
        F = next_F
        T = set([(v, p) for v in F
                 for p in filter(lambda x: x >= g.get_node_priority_function_i(v, func),
                                 j_priorities)])
        next_F = R_set_func(g, func, T, j)
        next_F = next_F & F
    return F


def psolC_func(g, func, W1, W2):
    safe_episodes = jfs_algo_func(g, func, 0)
    subgame = g
    if len(safe_episodes) > 0:
        A, complement = attractor(subgame, safe_episodes, 0)
        W1.extend(A)
        subgame = subgame.subgame(complement)
        subgame, W1, W2 = psolC_func(subgame, func, W1, W2)
    safe_episodes = jfs_algo_func(subgame, func, 1)
    if len(safe_episodes) > 0:
        A, complement = attractor(subgame, safe_episodes, 1)
        W2.extend(A)
        subgame = subgame.subgame(complement)
        subgame, W1, W2 = psolC_func(subgame, func, W1, W2)
    return subgame, W1, W2


def psolC_generalized(g, W0, W1):
    # base case : game is empty
    if g.get_nodes() == []:
        if DEBUG_PRINT: print("Base case return")
        return g, W0, W1

    # else retrieve useful information on the game
    nbr_func = g.get_nbr_priority_functions()  # number of functions
    priorities = [[] for z in xrange(nbr_func)]  # setup list containing list of priorities for each function
    even_priorities = [[] for z in xrange(nbr_func)]  # setup list containing list of even priorities for each function

    # first, retrieve all priorities and put them in the lists of priorities for each function
    for node in g.nodes.iterkeys():
        for func in range(nbr_func):
            priorities[func].append(g.get_node_priority_function_i(node, func + 1))  # function are numbered 1 to k

    # sort priorities and create the lists containing only the even priorities
    for func in range(nbr_func):
        priorities[func] = sorted(set(priorities[func]), reverse=False)  # change into set to remove duplicates and sort
        even_priorities[func] = filter(lambda x: x % 2 == 0, priorities[func])  # keep the sorted even priorities

        # if there are no even priorities according to one of the functions, the game is completely won by player 1
        # return empty game and all nodes added to W1
        if len(even_priorities[func]) == 0:
            W1.extend(g.nodes.keys())
            return Graph(), W0, W1

    if DEBUG_PRINT:
        print("Priorities " + str(priorities))
        print("Even priorities " + str(even_priorities))


    # handle odd priorities by calling psolC with the correct function
    for i in range(1, nbr_func + 1):
        safe_episodes = jfs_algo_func(g, i, 1)
        if len(safe_episodes) > 0:
            A, complement = attractor(g, safe_episodes, 1)
            W1.extend(A)
            subgame = g.subgame(complement)
            return psolC_generalized(subgame, W0, W1)

    # handle even priorities
    w = truc(g, nbr_func, even_priorities, priorities)
    if len(w) > 0:
        A, complement = attractor(g, w, 0)
        W0.extend(A)
        subgame = g.subgame(complement)
        return psolC_generalized(subgame, W0, W1)

    return g, W0, W1


def truc(g, nbr_func, even_priorities, priorities):
    """
    Compute the fixpoint with candidate set F and target set T
    :param g:
    :type g:
    :param nbr_func:
    :type nbr_func:
    :param even_priorities:
    :type even_priorities:
    :return:
    :rtype:
    """

    # priorities are sorted so we can take the min priority easily
    max_values = [l[len(l)-1] for l in priorities]
    #print("max priorities "+str(max_even_priorities))

    empty_set = set()
    cache = set()
    t = set(g.nodes.keys())

    while cache != t and t != empty_set:

        cache = t
        att = compute_fixpoint(g, t, nbr_func, even_priorities, max_values)

        res = set()
        for elem in init_nodes(g, t, nbr_func):
            if att.contains_element(elem):
                res.add(elem[0])

        t = t.intersection(res)

    return t


def init_nodes(graph, nodes, nbr_func):
    res = []
    for node in nodes:
        init = [0] * (nbr_func + 1)
        init[0] = node
        for i in range(1, nbr_func + 1):
            init[i] = graph.get_node_priority_function_i(node, i)

        res.append(init)

    return res


def intersector(x, y):
    """
    Intersection between two memory values x = m' and y = m.
    """
    parity_x = x % 2
    parity_y = y % 2

    if parity_x == 1:
        if parity_y == 1:
            return min(x, y)
        else:
            return y
    if parity_x == 0:
        if parity_y == 0:
            return max(x, y)
        else:
            return x


def comparator(x, y):
    """
    Comparison between two memory values x = m' and y = m. We want to check whether x <= y
    """
    parity_x = x % 2
    parity_y = y % 2

    if parity_x == 1:
        if parity_y == 1:
            return x <= y
        else:
            return False
    if parity_x == 0:
        if parity_y == 0:
            return x >= y
        else:
            return True


def intersector_generalized(x, y):
    """
    Intersection between two elements [v', m_1', ... m'_k] [v, m_1, ... m_k] is possible iff v = v' (else, elements are
    incomparable and function yields -1). Then we just apply intersection between each memory value.
    """

    if x[0] != y[0]:
        return -1
    else:
        nbr_functions = len(x)
        res = [x[0]]
        for func in range(1, nbr_functions):
            res.append(intersector(x[func], y[func]))

    return res


def comparator_generalized(x, y):
    """
    Comparison between two elements [v', m_1', ... m'_k] [v, m_1, ... m_k] is possible iff v = v' (else, elements are
    incomparable and function yields False). Then we just compare each memory value.
    """

    if x[0] != y[0]:
        return False
    else:
        nbr_functions = len(x)
        for func in range(1, nbr_functions):
            if not comparator(x[func], y[func]):
                return False
    return True


def down_generalized(element, priorities, node, nbr_functions, max_values):
    """
    Computes the largest m = [m_1, ..., m_k] such that up(m, priorities) <= m' = element[1:]. Then we add node to
    obtain [node, m]. When computing down, priorities is a tuple of size k which gives the encountered priority
    according to each priority function. Max_values records the maximum value to know when a memory value is not
    defined.
    """

    # print(element, priorities, node, nbr_functions, max_values)

    # resulting node
    res = [0] * (nbr_functions + 1)
    res[0] = node

    # for each priority function (numbered from 1 to k)
    for func in range(1, nbr_functions + 1):

        encountered_priority_p = priorities[func - 1]

        # if priority encountered is even
        if encountered_priority_p % 2 == 0:

            m_prim = element[func]

            if encountered_priority_p < m_prim:
                res[func] = m_prim

            else:
                res[func] = max(encountered_priority_p - 1, 0)

        else:

            m_prim = element[func]

            if encountered_priority_p <= m_prim:
                res[func] = m_prim

            else:

                if encountered_priority_p != max_values[func - 1]:
                    res[func] = encountered_priority_p + 1
                else:
                    return -1

    return res


def create_start_antichain(starting_nodes, nbr_func, even_values):
    # TODO this is a crude creation adding every possibility, we can directly add the max elements io the max
    # even value for each
    start_antichain = Antichain(comparator_generalized, intersector_generalized)

    # create the antichain of maximal elements of the safe set
    # every counter in every tuple has the maximal value
    for node in starting_nodes:
        temp = [0] * (nbr_func + 1)
        temp[0] = node
        for func in range(1, nbr_func + 1):
            # even values are sorted
            temp[func] = even_values[func - 1][0] # even values are sorted so first is smallest
        start_antichain.insert(temp)

    return start_antichain


def compute_fixpoint(graph, starting_nodes, nbr_func, even_values, max_values):
    """
    This is the attractor starting node is f_j
    Computes the fixpoint obtained by the symbolic version of the backward algorithm for safety games.
    Starts from the antichain of the safe set and works backwards using controllable predecessors.
    The maximum value for the counters is a parameter to facilitate the incremental algorithm.
    :param graph:
    :type graph:
    :param max_value:
    :type max_value:
    :return:
    :rtype:
    """

    if DEBUG_PRINT:
        print("ARRIVING IN FIXPOINT ")
        print(graph)
        print("even_values " + str(even_values))
        print("max values " + str(max_values))

    # wether we want to print the sets during computation
    toPrint = False

    # start antichain is antichain of tj
    start_antichain = create_start_antichain(starting_nodes, nbr_func, even_values)

    # TODO change intersection to union, also add target as union when computing cpre, also the true start is
    # the cpre of start

    if (toPrint):
        print("Dtart antichain  : " + str(start_antichain) + "\n")

    cpre1 = Cpre(start_antichain, 1, graph, nbr_func, max_values)

    if (toPrint):
        print("CPre_1 of start antichain - new start : " + str(cpre1) + "\n")

    cpre0 = Cpre(start_antichain, 0, graph, nbr_func, max_values)

    if (toPrint):
        print("CPre_0 of start antichain - new start : " + str(cpre0) + "\n")

    # we know the elements of cpre0 and cpre1 to be incomparable. Union of the two antichains can be done through
    # simple extend
    cpre0.incomparable_elements.extend(cpre1.incomparable_elements)

    if (toPrint):
        print("New start antichain : " + str(cpre0) + "\n")

    antichain1 = cpre0

    antichain1_union_start = Antichain(comparator_generalized, intersector_generalized)
    antichain1_union_start.union(cpre0)
    antichain1_union_start.union(start_antichain)

    cpre1 = Cpre(antichain1_union_start, 1, graph, nbr_func, max_values)

    if (toPrint):
        print("CPre_1 of start antichain: " + str(cpre1) + "\n")

    cpre0 = Cpre(antichain1_union_start, 0, graph, nbr_func, max_values)

    if (toPrint):
        print("CPre_0 of start antichain: " + str(cpre0) + "\n")

    # we know the elements of cpre0 and cpre1 to be incomparable. Union of the two antichains can be done through
    # simple extend
    cpre0.incomparable_elements.extend(cpre1.incomparable_elements)

    if (toPrint):
        print("Union of CPre_0 and CPre_1 " + str(cpre0) + "\n")

    tmp = copy.deepcopy(antichain1)
    antichain2 = antichain1.union(cpre0)
    antichain1 = tmp

    if (toPrint):
        print("Union of new start and previous union " + str(antichain2) + "\n")

    nb_iter = 0

    #print("antichain 1"+str(antichain1))
    #print("antichain 2" +str(antichain2))
    # while we have not obtained the fixpoint
    while not antichain2.compare(antichain1):

        nb_iter += 1

        antichain1 = antichain2

        antichain1_union_start = Antichain(comparator_generalized, intersector_generalized)
        antichain1_union_start.union(antichain1)
        antichain1_union_start.union(start_antichain)

        cpre1 = Cpre(antichain1_union_start, 1, graph, nbr_func, max_values)
        if (toPrint):
            print("ITER " + str(nb_iter) + " CPre 1 of prev " + str(cpre1) + "\n")

        cpre0 = Cpre(antichain1_union_start, 0, graph, nbr_func, max_values)

        if (toPrint):
            print("ITER " + str(nb_iter) + " CPre 0 of prev " + str(cpre0) + "\n")

        temp = cpre0.union(cpre1)

        if (toPrint):
            print("ITER " + str(nb_iter) + " Union of Pre 0 and Pre 1  " + str(temp) + "\n")

        tmp = copy.deepcopy(antichain1)
        antichain2 = antichain1.union(temp)
        antichain1 = tmp


        if (toPrint):
            print("ITER " + str(nb_iter) + " final set  " + str(antichain2) + "\n")

    return antichain1


def Cpre(antichain, player, graph, nbr_functions, max_value):
    """
    Calls the correct controllable predecessor function depending on the player.
    :param antichain:
    :type antichain:
    :param player:
    :type player:
    :param graph:
    :type graph:
    :param nbr_functions:
    :type nbr_functions:
    :param max_value:
    :type max_value:
    :return:
    :rtype:
    """
    if player == 0:
        return Cpre_0(antichain, graph, nbr_functions, max_value)
    else:
        return Cpre_1(antichain, graph, nbr_functions, max_value)


def Cpre_1(antichain, graph, nbr_functions, max_value):
    """
    Computes the antichain of the controllable predecessors for player 1 of 'antichain'.
    :param antichain:
    :type antichain:
    :param graph:
    :type graph:
    :param nbr_functions:
    :type nbr_functions:
    :param max_value:
    :type max_value:
    :return:
    :rtype:
    """

    if antichain.incomparable_elements == []:
        return antichain

    cur_antichain = Antichain(comparator_generalized, intersector_generalized)
    for node in graph.get_nodes():
        if graph.get_node_player(node) == 1:
            first_iteration = True
            temp2 = Antichain(comparator_generalized, intersector_generalized)  # contains the set for intersection
            for succ in graph.get_successors(node):
                temp1 = Antichain(comparator_generalized, intersector_generalized)
                for element in antichain.incomparable_elements:
                    if element[0] == succ:

                        computed_down = down_generalized(element, graph.nodes[node][1:], node, nbr_functions, max_value)
                        # print("Down = "+str(computed_down)+" Compute down of "+str(element)+" with prio "+str(graph.get_node_priority(node))+" node "+str(node)+" val max "+str(max_counter))

                        if computed_down != -1:
                            temp1.insert(computed_down)

                if first_iteration:
                    temp2 = temp1
                    first_iteration = False
                else:
                    # print("temp1 "+str(temp1)+ " temp2 "+str(temp2))
                    temp2 = temp1.intersection(temp2)
                    # print("inter  "+str(temp2))

            cur_antichain = cur_antichain.union(temp2)

    return cur_antichain


def Cpre_0(antichain, graph, nbr_functions, max_value):
    """
    Computes the antichain of the controllable predecessors for player 0 of 'antichain'.
    :param antichain:
    :type antichain:
    :param graph:
    :type graph:
    :param nbr_functions:
    :type nbr_functions:
    :param max_value:
    :type max_value:
    :return:
    :rtype:
    """

    if antichain.incomparable_elements == []:
        return antichain

    cur_antichain = Antichain(comparator_generalized, intersector_generalized)
    for element in antichain.incomparable_elements:
        for pred in graph.get_predecessors(element[0]):
            if graph.get_node_player(pred) == 0:
                computed_down = down_generalized(element, graph.nodes[pred][1:], pred, nbr_functions,
                                                 max_value)
                if computed_down != -1:
                    cur_antichain.insert(computed_down)

    return cur_antichain
