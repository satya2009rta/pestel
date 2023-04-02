import operations
from collections import deque, defaultdict
from attractors import init_out, attractor


def R_set(g, target_set, j):
    """
    We compute the attractor of a set of node-priority pairs where the priority
    represents the maximal priority seen so far.
    """
    ascending_priorities = g.get_sorted_priorities()
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
            pred_priority = g.get_node_priority(pred)
            if pred_priority > priority:
                continue  # cannot be a predecessor
            if priority > g.get_node_priority(node):
                options = [priority]
            else:
                assert(priority == g.get_node_priority(node))
                options = filter(lambda x: x >= pred_priority and
                                 x <= priority, ascending_priorities)
                assert(len(options) > 0)
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
        if regions[(n, g.get_node_priority(n))] == j:
            W.add(n)
    return W


def jfs_algo(g, j):
    assert(j == 0 or j == 1)
    j_priorities = filter(lambda x: (x % 2) == j,
                          g.get_sorted_priorities())
    T = set([(v, p) for v in g.get_nodes()
             for p in filter(lambda x: x >= g.get_node_priority(v),
                             j_priorities)])
    next_F = R_set(g, T, j)
    F = set()
    while next_F != F:
        F = next_F
        T = set([(v, p) for v in F
                 for p in filter(lambda x: x >= g.get_node_priority(v),
                                 j_priorities)])
        next_F = R_set(g, T, j)
        next_F = next_F & F
    return F


def psolC(g, W1, W2):
    safe_episodes = jfs_algo(g, 0)
    subgame = g
    if len(safe_episodes) > 0:
        A, complement = attractor(subgame, safe_episodes, 0)
        W1.extend(A)
        subgame = subgame.subgame(complement)
        subgame, W1, W2 = psolC(subgame, W1, W2)
    safe_episodes = jfs_algo(subgame, 1)
    if len(safe_episodes) > 0:
        A, complement = attractor(subgame, safe_episodes, 1)
        W2.extend(A)
        subgame = subgame.subgame(complement)
        subgame, W1, W2 = psolC(subgame, W1, W2)
    return subgame, W1, W2
