import copy

from antichain import Antichain


def intersector(x, y):
    """
    Intersection between two tuples of counters [c_1, c_3, ..., c_d] [c'_1, c'_3, ..., c'_d].
    Corresponds to the minimum between each c_i, c'_i.
    :param x:
    :type x:
    :param y:
    :type y:
    :return:
    :rtype:
    """

    size = len(x)
    res = []
    for i in range(0, size):
        res.append(min(x[i], y[i]))
    return res


def comparator(x, y):
    """
    Comparison between two tuples of counters [c_1, c_3, ..., c_d] [c'_1, c'_3, ..., c'_d].
    Check whether for all i, c_i <= c'_i.
    :param x:
    :type x:
    :param y:
    :type y:
    :return:
    :rtype:
    """

    size = len(x)
    for i in range(0, size):
        if x[i] > y[i]:
            return False
    return True


def intersector_generalized_0(x, y):
    """
    Intersection between two elements [v, (c_1, c_3, ..., c_d1), ..., (c_1, c_3, ..., c_dk)]
    [v', (c'_1, c'_3, ..., c'_d1), ..., (c'_1, c'_3, ..., c'_dk)] is possible iff v = v' (else, elements are
    incomparable and function yields -1). Then we just apply intersection between each tuple of counters.
    :param x:
    :type x:
    :param y:
    :type y:
    :return:
    :rtype:
    """

    if x[0] != y[0]:
        return -1
    else:
        nbr_functions = len(x)
        res = [x[0]]
        for func in range(1, nbr_functions):
            res.append(intersector(x[func], y[func]))

    return res


def comparator_generalized_0(x, y):
    """
    Intersection between two elements [v, (c_1, c_3, ..., c_d1), ..., (c_1, c_3, ..., c_dk)]
    [v', (c'_1, c'_3, ..., c'_d1), ..., (c'_1, c'_3, ..., c'_dk)] is possible iff v = v' (else, elements are
    incomparable and function yields False). Then we just compare every tuples of counters.
    :param x:
    :type x:
    :param y:
    :type y:
    :return:
    :rtype:
    """

    if x[0] != y[0]:
        return False
    else:
        nbr_functions = len(x)

        for func in range(1, nbr_functions):
            if not comparator(x[func], y[func]):
                return False
    return True


def down_generalized_0(element, priorities, node, nbr_functions, max_value):
    """
    Computes the largest m = [v, (c_1, c_3, ..., c_d1), ..., (c_1, c_3, ..., c_dk)] such that
    up(m, priorities) <= element. Here, we have a single maximum value for every counters. When computing
    down, priorities is a tuple of size k which gives the encountered priority according to each priority
    function.
    :param element:
    :type element:
    :param priorities:
    :type priorities:
    :param node:
    :type node:
    :param nbr_functions:
    :type nbr_functions:
    :param max_value:
    :type max_value:
    :return:
    :rtype:
    """

    # resulting node
    res = [node]

    # for each tuple of counters
    for func in range(1, nbr_functions + 1):

        # retrieve the position of the counter concerned by the encountered priority according to the right function
        concerned_counter = (priorities[func - 1] // 2)

        if priorities[func - 1] % 2 == 0:
            # even priority resets the first few counters to the max value
            succ = (concerned_counter) * [max_value] + element[func][concerned_counter:]
        else:
            if element[func][concerned_counter] == 0:
                # we can't decrement 0. Counter is in underflow, the result is the underflow value -1
                # if there is at least one underflow, the whole node is in underflow
                return -1
            else:
                # decrement the right counter
                succ = copy.copy(element[func])
                succ[concerned_counter] -= 1

        res.append(succ)

    return res


def compute_counters_sizes_0(graph):
    """
    Computes the required number of counters for each function in order to create the
    tuple of counters.
    :param graph:
    :type graph:
    :return:
    :rtype:
    """

    # first we find out the number of counters necessary
    nbr_functions = graph.get_nbr_priority_functions()
    graph_nodes = graph.get_nodes()

    # initialize the list holding the required number of counters per function
    nbr_counters_per_function = [0] * nbr_functions

    for func in range(1, nbr_functions + 1):
        # first we find out the number of counters necessary by retrieving the maximum odd priority in the game
        maximum = -1
        for node in graph_nodes:
            if graph.get_node_priority_function_i(node, func) > maximum:
                maximum = graph.get_node_priority_function_i(node, func)
        if maximum % 2 == 0:
            maxOdd = maximum - 1
        else:
            maxOdd = maximum

        # get the number of counters and update the list of required number of counters
        nbr_counters = (maxOdd // 2) + 1
        nbr_counters_per_function[func - 1] = nbr_counters

    return nbr_functions, nbr_counters_per_function


def compute_fixpoint_0(graph, max_value):
    """
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

    # wether we want to print the sets during computation
    toPrint = False

    # get the values to create the create the antichain of maximal elements of the safe set
    nbr_functions, nbr_counters_per_function = compute_counters_sizes_0(graph)

    start_antichain = Antichain(comparator_generalized_0, intersector_generalized_0)

    # create the antichain of maximal elements of the safe set
    # every counter in every tuple has the maximal value
    for node in graph.get_nodes():
        temp = [node]
        for func in range(0, nbr_functions):
            temp.append(nbr_counters_per_function[func] * [max_value])
        start_antichain.insert(temp)

    if (toPrint):
        print("Start antichain : " + str(start_antichain) + "\n")

    antichain1 = start_antichain

    cpre1 = Cpre(start_antichain, 1, graph, nbr_functions, max_value)

    if (toPrint):
        print("CPre_1 of start antichain: " + str(cpre1) + "\n")

    cpre0 = Cpre(start_antichain, 0, graph, nbr_functions, max_value)

    if (toPrint):
        print("CPre_0 of start antichain: " + str(cpre0) + "\n")

    # we know the elements of cpre0 and cpre1 to be incomparable. Union of the two antichains can be done through
    # simple extend
    cpre0.incomparable_elements.extend(cpre1.incomparable_elements)

    if (toPrint):
        print("Union of CPre_0 and CPre_1 " + str(cpre0) + "\n")

    antichain2 = antichain1.intersection(cpre0)

    if (toPrint):
        print("Inter of start and previous union " + str(antichain2) + "\n")

    nb_iter = 0

    # while we have not obtained the fixpoint
    while not antichain1.compare(antichain2):

        nb_iter += 1

        antichain1 = antichain2

        cpre1 = Cpre(antichain1, 1, graph, nbr_functions, max_value)
        if (toPrint):
            print("ITER " + str(nb_iter) + " CPre 1 of prev " + str(cpre1) + "\n")

        cpre0 = Cpre(antichain1, 0, graph, nbr_functions, max_value)

        if (toPrint):
            print("ITER " + str(nb_iter) + " CPre 0 of prev " + str(cpre0) + "\n")

        temp = cpre0.union(cpre1)

        if (toPrint):
            print("ITER " + str(nb_iter) + " Union of Pre 0 and Pre 1  " + str(temp) + "\n")

        antichain2 = antichain1.intersection(temp)

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

    cur_antichain = Antichain(comparator_generalized_0, intersector_generalized_0)
    for node in graph.get_nodes():
        if graph.get_node_player(node) == 1:
            first_iteration = True
            temp2 = Antichain(comparator_generalized_0, intersector_generalized_0)  # contains the set for intersection
            for succ in graph.get_successors(node):
                temp1 = Antichain(comparator_generalized_0, intersector_generalized_0)
                for element in antichain.incomparable_elements:
                    if element[0] == succ:

                        computed_down = down_generalized_0(element, graph.nodes[node][1:], node, nbr_functions, max_value)
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

    cur_antichain = Antichain(comparator_generalized_0, intersector_generalized_0)
    for element in antichain.incomparable_elements:
        for pred in graph.get_predecessors(element[0]):
            if graph.get_node_player(pred) == 0:
                computed_down = down_generalized_0(element, graph.nodes[pred][1:], pred, nbr_functions,
                                                   max_value)
                if computed_down != -1:
                    cur_antichain.insert(computed_down)

    return cur_antichain


"""
The same algorithm for player 2 is similar to the one for player 1. However we have shown that
we do not have equivalence between the generalized parity game and safety game for that player.
"""


def get_winning_regions_incremental(graph):
    """
    Incremental algorithm to obtain the solution of the generalized parity game from the solutions of the
    safety games with incrementally larger maximum values.
    :param graph:
    :type graph:
    :return:
    :rtype:
    """

    # start with small maximum value
    max_value = 1

    # the game is completely solved if we have decided a winner for each node
    completely_solved = False

    nbr_nodes = len(graph.get_nodes())
    while not completely_solved:

        # compute both fixpoints for the current maximal value
        fixpoint_0 = compute_fixpoint_0(graph, max_value)
        # TODO this shoould be fixpoint_1 = compute_fixpoint_p1(graph, max_value)
        fixpoint_1 = Antichain(comparator_generalized_0, intersector_generalized_0)

        # extract both winning regions
        winning_region_0 = set()
        winning_region_1 = set()

        for element in fixpoint_0.incomparable_elements:
            winning_region_0.add(element[0])

        for element in fixpoint_1.incomparable_elements:
            winning_region_1.add(element[0])

        # check if the game is completely solved
        # TODO we need a stopping criterion when the theoretical maximal value that gives the equivalence is reached
        # TODO for testing purposes, stop at max_value = 100
        if len(winning_region_0) + len(winning_region_1) == nbr_nodes or max_value == 100:
            completely_solved = True

            # print("MAX VALUE "+str(max_value))
            # print("winning 0 " + str(winning_region_0))
            # print("winning 1 " + str(winning_region_1))

        # if it is not, increment the maximal value
        max_value += 1
        # print("value "+str(max_value)+" current fixpoint 0 : "+ str( fixpoint_0))
        # print("value "+str(max_value)+" current fixpoint 1 : "+ str( fixpoint_1))

    return list(winning_region_0), list(winning_region_1)


import file_handler as io
g = io.load_generalized_from_file("generalized_parity_game_example.txt")
fixpoint = compute_fixpoint_0(g, 4)
winning_region_0, winning_region_1 = get_winning_regions_incremental(g)
print("Fixpoint : " + str(fixpoint))
print("Winning region of player 0 : " + str(winning_region_0) + " Winning region of player 1 : " + str(winning_region_1))
# solution should be [1, 2] and [3,4,5]
