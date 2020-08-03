from ..graph import Graph
from .tsp import tsp_brute_force, tsp_held_karp_bitset, tsp_held_karp_hashset


def hamiltonian_path(graph: Graph, tsp_algorithm):
    """
    Hamiltonian path algorithm based on traveling salesman algorithm.
    To find a path, a tsp algorithm is used.
    The algorithm will always find a hamiltonian cycle if it exists.

    > complexity:
    - time: O(tsp_algorithm)
    - space: O(tsp_algorithm)

    > parameters:
    - `graph: Graph`: graph to find path
    - `tsp_algorithm: (Graph, int?, (int | float)?) => (int | float, int())`: a tsp algorithm, heuristics do not work

    > `return: (bool, int())`: the path is a cycle and the vertices, or `None` if graph does not have a path
    """
    absent_edge_length = sum(abs(edge.length) for edge in graph.edges()) + 1
    distance, path = tsp_algorithm(graph, absent_edge_length=absent_edge_length)
    if distance < absent_edge_length:
        return True, path
    matrix = graph.adjacency_matrix(absent_edge_length=absent_edge_length)
    absent_edges = []
    for i in range(len(path) - 1):
        if matrix[path[i]][path[i + 1]] == absent_edge_length:
            infinity_edges.append((i, i + 1))
    return path[absent_edges[0][1]:] + path[:absent_edges[0][0]] if len(absent_edges) == 1 else None


def test():
    from ...test import benchmark
    from ..factory import random_undirected
    benchmark(
        [
            (' hamiltonian path > tsp brute force', lambda graph: hamiltonian_path(graph, tsp_brute_force)),
            ('      hamiltonina path > tsp bitset', lambda graph: hamiltonian_path(graph, tsp_held_karp_bitset)),
            ('     hamiltonina path > tsp hashset', lambda graph: hamiltonian_path(graph, tsp_held_karp_hashset))
        ],
        test_inputs=(random_undirected(i, density=0.8) for i in (4, 5, 6, 7)),
        bench_sizes=range(1, 11),
        bench_input=lambda s: random_undirected(s)
    )


if __name__ == '__main__':
    test()
