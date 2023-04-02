import copy


def compress_function(g, i):
    """
    Compresses the priorities of priority function i in the game graph g.
    Function i must be between 1 and k (the number of functions in g).
    This modifies the game arena g.
    :param g: a game arena, this arena is going to be modified.
    :param i: the id of the priority function to compress.
    :return: the game arena g in which the priorities according to function i have been compressed.
    """

    nodes = g.get_nodes_descriptors()  # Nodes from g

    priorities = sorted(nodes.iteritems(), key=lambda x: x[1][i])  # Sorts nodes by priority

    current = priorities[0][1][i]  # Take the first node, its information and value nbr i

    if current % 2 == 0:
        start = 0
    else:
        start = 1

    val = start

    for elem in priorities:

        if elem[1][i] % 2 == start:
            # Replace the info for the node : keep player and priorities and change priority
            # according to function nbr i
            g.nodes[elem[0]] = tuple(elem[1][:i] + tuple([val]) + elem[1][i + 1:])
        else:
            val += 1
            start = ((start + 1) % 2)
            g.nodes[elem[0]] = tuple(elem[1][:i] + tuple([val]) + elem[1][i + 1:])

    return g


def compress_priorities(g):
    """
    Compresses the priorities in a regular parity game (with one priority function).
    This yields a new arena g in which the priorities have been compressed
    :param g: a game arena.
    :return: a new game arena in which the priorities have been compressed.
    """

    # We work on a copy of g, which we modify
    g_copy = copy.deepcopy(g)

    return compress_function(g_copy, 1)


def compress_priorities_generalized(g):
    """
    Compresses the priorities in a generalized parity game.
    This yields a new arena g in which, the priorities have been compressed for each priority function.
    :param g: a game arena.
    :return: a new game arena in which the priorities have been compressed.
    """

    # We work on a copy of g, which we modify
    g_copy = copy.deepcopy(g)

    # Compress every priority function
    for i in range(1, g.get_nbr_priority_functions()+1):
        compress_function(g_copy, i)

    return g_copy

def compress_priorities_generalized_testing(g):
    """
    Compresses the priorities in a generalized parity game.
    This yields a new arena g in which, the priorities have been compressed for each priority function.
    :param g: a game arena.
    :return: a new game arena in which the priorities have been compressed.
    """

    # We work on a copy of g, which we modify
    g_copy = copy.deepcopy(g)
    print g.get_nbr_priority_functions()
    print(list(range(1, g.get_nbr_priority_functions())))
    # Compress every priority function
    for i in range(1, g.get_nbr_priority_functions()+1):
        compress_function_testing(g_copy, i)

    return g_copy

def compress_function_testing(g, i):
    """
    Compresses the priorities of priority function i in the game graph g.
    Function i must be between 1 and k (the number of functions in g).
    This modifies the game arena g.
    :param g: a game arena, this arena is going to be modified.
    :param i: the id of the priority function to compress.
    :return: the game arena g in which the priorities according to function i have been compressed.
    """

    nodes = g.get_nodes_descriptors()  # Nodes from g

    priorities = sorted(nodes.iteritems(), key=lambda x: x[1][i])  # Sorts nodes by priority
    print(priorities)
    s = len(priorities)/2
    current = priorities[s][1][i]  # Take the first node, its information and value nbr i

    if current % 2 == 0:
        start = 0
    else:
        start = 1

    val = priorities[s][1][i]

    for elem in priorities[s:]:

        if elem[1][i] % 2 == start:
            # Replace the info for the node : keep player and priorities and change priority
            # according to function nbr i
            g.nodes[elem[0]] = tuple(elem[1][:i] + tuple([val]) + elem[1][i + 1:])
        else:
            val += 1
            start = ((start + 1) % 2)
            g.nodes[elem[0]] = tuple(elem[1][:i] + tuple([val]) + elem[1][i + 1:])

    return g

# Old version of compression for parity games, might be used for regression testing later.
"""
def compress_priorities(g):

    g_copy = copy.deepcopy(g)
    nodes = g_copy.get_nodes_descriptors()  # Nodes from g
    priorities = sorted(nodes.iteritems(), key=lambda x:x[1][1]) # sorts nodes per priority
    current = priorities[0][1][1]
    if current % 2 == 0:
        start = 0
    else:
        start = 1
    val = start
    for elem in priorities:
        if(elem[1][1] % 2 == start):
            g_copy.nodes[elem[0]] = tuple([elem[1][0], val])
        else:
            val += 1
            start = ((start + 1) %2)
            g_copy.nodes[elem[0]] = tuple([elem[1][0], val])

    return g_copy
"""
