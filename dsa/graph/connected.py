from ..disjoint_set import DisjointSet
from .graph import Graph


def connected(graph):
    visited = [False] * len(graph)
    groups = [None] * len(graph)
    if len(graph) == 0:
        return groups
    group = 0
    for vertex in range(len(graph)):
        if visited[vertex]:
            continue
        for traverse_vertex, _ in graph.traverse(vertex, 'dfs', visited):
            visited[traverse_vertex] = True
            groups[traverse_vertex] = group
        group += 1
    return groups


def test():
    g = Graph.random(20, 0.1)
    print(g)
    print(connected(g))


if __name__ == '__main__':
    test()
