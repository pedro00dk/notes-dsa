from .hashtable import Hashtable


class DisjointSet:
    def __init__(self, size=0):
        self.sets = [i for i in range(size)]
        self.ranks = [0 for i in range(size)]
        self.sizes = [1 for i in range(size)]
        self.count = len(self.sets)

    def __str__(self):
        lines = '\n'.join(
            [f'{i} -> {self.sets[i]} # rank: {self.ranks[i]} size: {self.sizes[i]}' for i in range(len(self.sets))]
        )
        return f'Disjoint Set [\n{lines}\n]'

    def __len__(self):
        return len(self.sets)

    def groups(self):
        return self.count

    def size(self, key):
        return self.sizes[self.find(key)]

    def make_set(self):
        key = len(self.sets)
        self.sets.append(key)
        self.ranks.append(0)
        self.sizes.append(1)
        self.count += 1
        return key

    def find(self, key):
        if key < 0 or key >= len(self.sets):
            raise KeyError('not found')
        root = key
        while root != self.sets[root]:
            root = self.sets[root]
        while key != self.sets[key]:
            key, self.sets[key] = self.sets[key], root
        return root

    def union(self, key_a, key_b):
        key_a = self.find(key_a)
        key_b = self.find(key_b)
        if key_a == key_b:
            return
        if self.ranks[key_a] < self.ranks[key_b]:
            key_a, key_b = key_b, key_a
        self.sets[key_b] = key_a
        self.ranks[key_a] += 1 if self.ranks[key_a] == self.ranks[key_b] else 0
        self.sizes[key_a] += self.sizes[key_b]
        self.count -= 1

    def connected(self, key_a, key_b):
        return self.find(key_a) == self.find(key_b)


class HashDisjointSet:
    def __init__(self):
        self.disjoint_set = DisjointSet()
        self.map = Hashtable()
        self.__len__ = self.disjoint_set.__len__
        self.groups = self.disjoint_set.groups

    def __str__(self):
        return f'Hash Disjoint Set {{\n{str(self.disjoint_set)}\n{str(self.map)}\n}}'

    def __len__(self):
        return len(self.disjoint_set)

    def size(self, key):
        return self.disjoint_set.size(self.map.get(key))

    def make_set(self, key):
        try:
            return self.map.get(key)
        except:
            inner_key = self.disjoint_set.make_set()
            self.map.put(key, inner_key)
            return inner_key

    def find(self, key):
        return self.disjoint_set.find(self.map.get(key))

    def union(self, key_a, key_b):
        return self.disjoint_set.union(self.map.get(key_a), self.map.get(key_b))

    def connected(self, key_a, key_b):
        return self.disjoint_set.connected(self.map.get(key_a), self.map.get(key_b))


def test():
    from .util import match
    d = HashDisjointSet()
    match([
        (d.make_set, ['a'], None),
        (d.make_set, ['e'], None),
        (d.make_set, ['i'], None),
        (d.make_set, ['o'], None),
        (d.make_set, ['u'], None),
        (d.make_set, ['0'], None),
        (d.make_set, ['1'], None),
        (d.make_set, ['2'], None),
        (d.make_set, ['3'], None),
        (d.make_set, ['4'], None),
        (print, [d], None),
        (d.union, ['a', 'e'], None),
        (d.union, ['i', 'o'], None),
        (d.union, ['a', 'o'], None),
        (d.union, ['u', 'a'], None),
        (d.union, ['0', '1'], None),
        (d.union, ['2', '3'], None),
        (d.union, ['4', '0'], None),
        (d.union, ['1', '2'], None),
        (print, [d], None),
        (d.connected, ['a', 'i'], True),
        (d.connected, ['e', 'o'], True),
        (d.connected, ['e', 'u'], True),
        (d.connected, ['3', 'u'], False),
        (d.connected, ['0', 'e'], False),
        (d.connected, ['1', '4'], True),
        (d.connected, ['1', '2'], True),
        (d.connected, ['2', '0'], True),
        (d.connected, ['i', '4'], False),
        (d.connected, ['u', '1'], False),
        (len, [d], 10),
        (d.groups, [], 2),
        (d.size, ['a'], 5),
        (d.size, ['0'], 5)
    ])


if __name__ == '__main__':
    test()