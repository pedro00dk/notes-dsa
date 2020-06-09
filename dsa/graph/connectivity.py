from ..dset import DisjointSet
from .graph import Graph


def connected_traverse(graph: Graph, /, mode='depth'):
    """
    Find connected groups in `graph` using traversals to expand groups.
    `graph` must be undirected, otherwise, the algorithm can not assure the groups are strongly connected.

    > complexity:
    - time: `O(v + e)`
    - space: `O(v)`

    > parameters:
    - `graph: Graph`: graph to search groups
    - `mode: ('depth' | 'breadth')? = 'depth'`: the traversal algorithm to use

    > `return: Vertex[][]`: list containing vertex groups
    """
    if not graph.is_undirected():
        raise Exception('connected algorithm only works with undirected graphs')
    visited = [False] * len(graph)
    groups = []
    for vertex in graph.vertices():
        if visited[vertex._id]:
            continue
        groups.append([v for v, *_ in graph.traverse(vertex._id, mode, visited=visited)])
    return groups


def connected_disjoint_set(graph: Graph):
    """
    Find connected groups in `graph` using a disjoint set.
    `graph` must be undirected, otherwise, the algorithm can not assure the groups are strongly connected.

    > complexity:
    - time: `O(v + e)`, the extra `v` is due to disjoint set operations to extract group as a `Vertex[][]` object
    - space: `O(v)`

    > parameters:
    - `graph: Graph`: graph to search groups
    - `mode: ('depth' | 'breadth')? = 'depth'`: the traversal algorithm to use

    > `return: Vertex[][]`: list containing vertex groups
    """
    if not graph.is_undirected():
        raise Exception('connected algorithm only works with undirected graphs')
    disjoint_set = DisjointSet(graph.vertices_count())
    for edge in graph.edges():
        disjoint_set.union(edge._source, edge._target)
    groups = [[] for i in range(disjoint_set.sets())]
    index = 0
    indices = {}
    for id in range(graph.vertices_count()):
        group = disjoint_set.find(id)
        if group not in indices:
            indices[group] = index
            index += 1
        groups[indices[group]].append(graph.get_vertex(id))
    return groups

# def tarjan_strong(graph: Graph):
#     visited = [False] * len(graph)
#     parent_link = [i for i in range(graph.vertices_count())]
#     groups = []
     
#     for vertex in graph.vertices():
#         if visited[vertex._id]:
#             continue
#         # groups.append([v for v, *_ in graph.traverse(vertex._id, mode, visited=visited)])
#         for vertex, parent, edge in graph.traverse(vertex._id, 'depth', visited,False, True):
#             parent_link[vertex]

#     return groups

#     pass

def test():
    from . import factory
    from ..test import benchmark
    benchmark(
        [
            (
                '  connected traverse depth',
                lambda graph: [[vertex._id for vertex in group] for group in connected_traverse(graph, mode='depth')]
            ),
            (
                'connected traverse breadth',
                lambda graph: [[vertex._id for vertex in group] for group in connected_traverse(graph, mode='breadth')]
            ),
            (
                '    connected disjoint set',
                lambda graph: [[vertex._id for vertex in group] for group in connected_disjoint_set(graph)]
            )
        ],
        loads=[connected_traverse],
        test_input_iter=(factory.random_undirected(i, 0.1) for i in (5, 10, 15, 20)),
        bench_size_iter=(1, 10, 100, 1000),
        bench_input=lambda s, r: factory.random_undirected(s, 0.05),
        bench_tries=50
    )


if __name__ == '__main__':
    test()
