from antichain import Antichain
import copy

"""
This file contains the implementation of the symbolic algorithm to solve parity games via safety games.
The implementation contains the algorithm with the point of view of player 1 (counters for odd priorities) and
for player 2 (counters for even priorities).
"""


def intersector(x, y):
    """
    Intersection between two elements [v, c_1, c_3, ..., c_d] [v', c'_1, c'_3, ..., c'_d] is possible
    iff v = v' (else, elements are incomparable and function yields -1). Then we just take the minimum between
    each c_i, c'_i.
    :param x:
    :type x:
    :param y:
    :type y:
    :return:
    :rtype:
    """
    size = len(x)
    if x[0] != y[0]:
        return -1
    else:
        res = [x[0]]
        for i in range(1, size):
            res.append(min(x[i], y[i]))
    return res


def comparator(x, y):
    """
    Comparison between two elements [v, c_1, c_3, ..., c_d] [v', c'_1, c'_3, ..., c'_d] is possible
    iff v = v' (else, elements are incomparable and function yields False). Then we just check whether for all i,
    c_i <= c'_i.
    :param x:
    :type x:
    :param y:
    :type y:
    :return:
    :rtype:
    """
    size = len(x)
    if x[0] != y[0]:
        return False
    else:
        for i in range(1, size):
            if x[i] >  y[i]:
                return False
    return True


def down(element, priority, node, max_counter):
    """
    Computes the largest m = [v, c_1, c_3, ..., c_d] such that up(m, priority) <= element.
    :param element:
    :type element:
    :param priority:
    :type priority:
    :param node:
    :type node:
    :param max_counter:
    :type max_counter:
    :return:
    :rtype:
    """

    # retrieve the position of the counter concerned by the encountered priority
    concerned_counter = (priority // 2) + 1

    if priority % 2 == 0:
        # even priority resets the first few counters to their max value
        succ = [node]+max_counter[0:concerned_counter-1] + element[concerned_counter:]
    else:
        if element[concerned_counter] == 0:
            # we can't decrement 0. Counter is in underflow, the result is the underflow value -1
            return -1
        else:
            # decrement the right counter
            succ = copy.copy(element)
            succ[concerned_counter] -= 1
            succ[0] = node

    return succ


def get_winning_regions(graph):
    """
    Get the winning region of player 0 in the graph.
    :param graph:
    :type graph:
    :return:
    :rtype:
    """

    fixpoint = compute_fixpoint(graph) # compute the fixpoint via symbolic algorithm
    winning_region_0 = []
    winning_region_1 = [] # TODO get the complement of the winning region of player 0

    # TODO should this not be a set to avoid having seveal times the same node in the winning region ?
    # TODO alternatively, could we not just set a flag to true or false depending on the winning region ?
    for element in fixpoint.incomparable_elements:
        winning_region_0.append(element[0])

    return winning_region_0


def compute_max_counter(graph):
    """
    Compute the maximum value for each counter. Returns [max_1, max_3, ...]
    :param graph:
    :type graph:
    :return:
    :rtype:
    """

    # first we find out the number of counters necessary by retrieving the maximum odd priority in the game
    maximum = -1
    for node in graph.get_nodes():
        if graph.get_node_priority(node) > maximum:
            maximum = graph.get_node_priority(node)
    if maximum % 2 == 0:
        maxOdd = maximum - 1
    else:
        maxOdd = maximum

    # get the number of counters and initialize the list of maximum values for those counters
    nbr_counters = (maxOdd // 2) + 1
    max_counter = [0] * nbr_counters

    # counts the number of occurrences of every odd priority
    for node in graph.get_nodes():
        if graph.get_node_priority(node) % 2 != 0:
            position = graph.get_node_priority(node) // 2
            max_counter[position] = max_counter[position] + 1
    return max_counter


def compute_fixpoint(graph):
    """
    Computes the fixpoint obtained by the symbolic version of the backward algorithm for safety games.
    Starts from the antichain of the safety set and works backwards using controllable predecessors.
    :param graph:
    :type graph:
    :return:
    :rtype:
    """

    # wether we want to print the sets during computation
    toPrint = False

    # create the antichain of maximal elements of the safe set
    max_counter = compute_max_counter(graph)
    start_antichain = Antichain(comparator, intersector)
    for node in graph.get_nodes():
        start_antichain.insert([node] + max_counter)


    if (toPrint):
        print("Start antichain : "+str(start_antichain)+"\n")

    antichain1 = start_antichain

    cpre1= Cpre(start_antichain, 1, graph, max_counter)

    if (toPrint):
        print("CPre_1 of start antichain: "+str(cpre1)+"\n")

    cpre0= Cpre(start_antichain, 0, graph, max_counter)

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

        cpre1 = Cpre(antichain1, 1, graph, max_counter)

        if (toPrint):
            print("ITER "+str(nb_iter)+" CPre 1 of prev " + str(cpre1) + "\n")

        cpre0 = Cpre(antichain1, 0, graph, max_counter)

        if (toPrint):
            print("ITER "+str(nb_iter)+" CPre 0 of prev " + str(cpre0) + "\n")

        temp = cpre0.union(cpre1)

        if (toPrint):
            print("ITER "+str(nb_iter)+" Union of Pre 0 and Pre 1  " + str(temp) + "\n")

        antichain2 = antichain1.intersection(temp)

        if (toPrint):
            print("ITER "+str(nb_iter)+" final set  " + str(antichain2) + "\n")

    return antichain1


def Cpre(antichain, player, graph, max_counter):
    """
    Calls the correct controllable predecessor function depending on the player.
    :param antichain:
    :type antichain:
    :param player:
    :type player:
    :param graph:
    :type graph:
    :param max_counter:
    :type max_counter:
    :return:
    :rtype:
    """
    if player == 0:
        return Cpre_0(antichain, graph, max_counter)
    else:
        return Cpre_1(antichain, graph, max_counter)


def Cpre_1(antichain, graph, max_counter):
    """
    Computes the antichain of the controllable predecessors for player 1 of 'antichain'.
    :param antichain:
    :type antichain:
    :param graph:
    :type graph:
    :param max_counter:
    :type max_counter:
    :return:
    :rtype:
    """

    if antichain.incomparable_elements == []:
        return antichain

    cur_antichain = Antichain(comparator, intersector)
    for node in graph.get_nodes():
        if graph.get_node_player(node) == 1:
            first_iteration = True
            temp2 = Antichain(comparator, intersector) # contains the set for the intersection
            for succ in graph.get_successors(node):
                temp1 = Antichain(comparator, intersector)
                for element in antichain.incomparable_elements:
                    if element[0] == succ:
                        computed_down = down(element, graph.get_node_priority(node), node, max_counter)
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


def Cpre_0(antichain, graph, max_counter):
    """
    Computes the antichain of the controllable predecessors for player 0 of 'antichain'.
    :param antichain:
    :type antichain:
    :param graph:
    :type graph:
    :param max_counter:
    :type max_counter:
    :return:
    :rtype:
    """

    if antichain.incomparable_elements == []:
        return antichain

    cur_antichain = Antichain(comparator, intersector)

    # check predecessors of each node present in the antichain
    for element in antichain.incomparable_elements:
            for pred in graph.get_predecessors(element[0]):

                # if said predecessors belong to player 0, compute down and add to the result
                if graph.get_node_player(pred) == 0:

                    computed_down = down(element, graph.get_node_priority(pred), pred, max_counter)

                    if computed_down != -1:
                        cur_antichain.insert(computed_down)

    return cur_antichain


import file_handler as io
g = io.load_from_file("parity_game_example.txt")
fixpoint = compute_fixpoint(g)
winning_region_0 = get_winning_regions(g)
print("Fixpoint : "+str(fixpoint))
print("Winning region of player 0 : "+str(winning_region_0))


"""
The rest of the file contains the same algorithm, but for player 2 (very minor changes)


def downb(element, priority, node, max_counter):
    concerned_counter = (priority // 2) + 1

    if priority % 2 == 1:

        # even priority resets the first few counters to max
        succ = [node]+max_counter[0:concerned_counter] + element[concerned_counter+1:]
    else:
        if element[concerned_counter] == 0:
            # Counter is in underflow, the result is the overflow special value -1
            return -1
        else:
            succ = copy.copy(element)
            succ[concerned_counter] -= 1
            succ[0] = node

    return succ

def get_winning_regionsb(graph):

    nbr_nodes = len(graph.get_nodes())
    fixpoint = compute_fixpointb(graph)
    winning_region_0 = []
    winning_region_1 = []

    for element in fixpoint.incomparable_elements:
        winning_region_0.append(element[0])

    return winning_region_0


def compute_max_counterb(graph):
    # First we find out the number of counters necessary
    maximum = -1
    for node in graph.get_nodes():
        if (graph.get_node_priority(node) > maximum):
            maximum = graph.get_node_priority(node)
    if maximum % 2 == 1:
        maxEven = maximum - 1
    else:
        maxEven = maximum

    nbr_counters = (maxEven // 2) + 1
    max_counter = [0] * nbr_counters

    # counts every odd priority
    
    #for node in graph.get_nodes():
    #    if (graph.get_node_priority(node) % 2 != 1):
    #        position = graph.get_node_priority(node) // 2
    #        max_counter[position] = max_counter[position] + 1
    
    for i in range(nbr_counters):
        max_counter[i] = 3
    return max_counter


def compute_fixpointb(graph):

    toPrint = True

    max_counter = compute_max_counterb(graph)
    start_antichain = Antichain(comparator, intersector)
    for node in graph.get_nodes():
        start_antichain.insert([node] + max_counter)


    if (toPrint):
        print("Start antichain : "+str(start_antichain)+"\n")

    antichain1 = start_antichain



    cpre1= Cpreb(start_antichain, 1, graph, max_counter)

    if (toPrint):
        print("CPre_1 of start antichain: "+str(cpre1)+"\n")

    cpre0= Cpreb(start_antichain, 0, graph, max_counter)

    if (toPrint):
        print("CPre_0 of start antichain: " + str(cpre0) + "\n")


    cpre0.incomparable_elements.extend(cpre1.incomparable_elements)

    if (toPrint):
        print("Union of CPre_0 and CPre_1 " + str(cpre0) + "\n")


    antichain2 = antichain1.intersection(cpre0)

    if (toPrint):
        print("Inter of start and previous union " + str(antichain2) + "\n")

    nb_iter = 0

    while not antichain1.compare(antichain2):

        nb_iter += 1

        antichain1 = antichain2

        cpre1 = Cpreb(antichain1, 1, graph, max_counter)

        if (toPrint):
            print("ITER "+str(nb_iter)+" CPre 1 of prev " + str(cpre1) + "\n")

        cpre0 = Cpreb(antichain1, 0, graph, max_counter)

        if (toPrint):
            print("ITER "+str(nb_iter)+" CPre 0 of prev " + str(cpre0) + "\n")

        temp = cpre0.union(cpre1)

        if (toPrint):
            print("ITER "+str(nb_iter)+" Union of Pre 0 and Pre 1  " + str(temp) + "\n")

        antichain2 = antichain1.intersection(temp)

        if (toPrint):
            print("ITER "+str(nb_iter)+" final set  " + str(antichain2) + "\n")

    return antichain1

def Cpreb(antichain, player, graph, max_counter):
    if player == 1:
        return Cpre_0b(antichain, graph, max_counter)
    else:
        return Cpre_1b(antichain, graph, max_counter)

def Cpre_1b(antichain, graph, max_counter):
    if antichain.incomparable_elements == []:
        #print("Empty antichain")
        return antichain

    cur_antichain = Antichain(comparator, intersector)
    for node in graph.get_nodes():
        if graph.get_node_player(node) == 0:
            first_iteration = True
            temp2 = Antichain(comparator, intersector) #contains the set for intersection
            for succ in graph.get_successors(node):
                temp1 = Antichain(comparator, intersector)
                for element in antichain.incomparable_elements:
                    if element[0] == succ:
                        computed_down = downb(element, graph.get_node_priority(node), node, max_counter)
                        #print("Down = "+str(computed_down)+" Compute down of "+str(element)+" with prio "+str(graph.get_node_priority(node))+" node "+str(node)+" val max "+str(max_counter))

                        if computed_down != -1:
                            temp1.insert(computed_down)

                if first_iteration:
                    temp2 = temp1
                    first_iteration = False
                else:
                    #print("temp1 "+str(temp1)+ " temp2 "+str(temp2))
                    temp2 = temp1.intersection(temp2)
                    #print("inter  "+str(temp2))

            cur_antichain = cur_antichain.union(temp2)

    return cur_antichain

def Cpre_0b(antichain, graph, max_counter):
    if antichain.incomparable_elements == []:
        #print("Empty antichain")
        return antichain

    cur_antichain = Antichain(comparator, intersector)
    for element in antichain.incomparable_elements:
            for pred in graph.get_predecessors(element[0]):
                if graph.get_node_player(pred) == 1:

                    computed_down = downb(element, graph.get_node_priority(pred), pred, max_counter)

                    if computed_down != -1:
                        cur_antichain.insert(computed_down)

    return cur_antichain

"""