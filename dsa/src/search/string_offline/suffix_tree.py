from __future__ import annotations

import collections
import dataclasses
import itertools
from typing import Any, Generator, Literal, Optional, cast

from ...search.rmq_lca.abc import lca_to_rmq
from ...search.rmq_lca.v4 import RangeMinimumQueryV4
from .abc import StringOffline, match_slices


@dataclasses.dataclass
class Node:
    """
    Represents a node of the suffix tree.
    Each node contains the information necessary to verify if a match arrives on it.

    > parameters
    - `id`: node unique id, used internally by the suffix tree
    - `left`: the starting index of the match from the parent node to arrive at the current node
    - `right`: the endding index (exclusive) of the match from the parent node to arrive at the current node
    - `match`: the starting index of a suffix in `tid` represented by this node (matching index), this also means
        the node is a leaf, internal nodes must set this to -1 to initialize the `children` property
    """

    id: int
    left: int
    right: int
    match: int = -1
    parent: Node = cast(Any, None)
    children: dict[str, Node] = dataclasses.field(default_factory=dict)


class SuffixTree(StringOffline):
    """
    Suffix tree implementation.

    > complexity
    - space: `O(n)`
    - `n`: length of `text` argument in `__init__`
    """

    def __init__(self, text: str, strategy: Literal["naive", "ukkonen"]):
        """
        Initialize the suffix tree given the received `text` and `strategy`.
        The space used is proportional to the length of `text` independently of `strategy`.

        > complexity
        - time: `O(n)` if `strategy == 'ukkonen'` else `O(n**2)`
        - space: `O(n)`
        - `n`: length of `text`

        > parameters
        - `texts`: list of texts to be indexed
        - `strategy`: build strategy
        """
        self._text = text + chr(0x10FFFF)
        self._id_gen = itertools.count()
        build_function = {"ukkonen": self._build_ukkonen, "naive": self._build_naive}[strategy]
        self._root = build_function()
        self._node_count = next(self._id_gen)
        # fast query preprocessing utilities
        # these functions could be implemented by the build functions but this would make them harder to understand
        # although all have linear time and space complexity, they impact heavily on performance (~3 times slower)
        self._node_depths = self._compute_node_depths()  # required: longest_repeated_substring, longest_common_prefix
        self._subtree_leaves = self._compute_subtree_leaves()  # required: occurrences_count, longest_repeated_substring
        self._leaves_references = self._compute_leaves_references()  # required: longest_common_prefix
        self._rmq_data, self._rmq_backward_mapper, self._rmq_forward_mapper = lca_to_rmq(
            self._root, lambda node: node.id, lambda node: iter(node.children.values()), lambda node: node, False, True
        )
        self._rmq = RangeMinimumQueryV4(self._rmq_data)  # required: longest_common_prefix

    def __str__(self) -> str:
        nodes: list[str] = []
        for node in self._pre(self._root):
            text_slice = self._text[node.left : node.right]
            leaf = f"<{node.match}>" if node.match != -1 else ""
            parent_depth = self._node_depths[node.parent.id] if node.parent is not None else 0
            nodes.append(f'{" " * parent_depth}├{text_slice} - {leaf}')
        all_nodes = "\n".join(nodes)
        return f"{type(self).__name__} [\n{all_nodes}\n]"

    def _build_naive(self) -> Node:
        """
        Build the suffix tree using the naive strategy.
        For each suffix, a path from the root is followed, and new nodes are created when necessary.

        > complexity
        - time: `O(n**2)`
        - space: `O(n)`
        - `n`: length of `self._text`
        """
        root = Node(next(self._id_gen), -1, 0)
        for i in range(len(self._text)):
            j = i
            cursor = root
            while self._text[j] in cursor.children:
                child: Node = cursor.children[self._text[j]]
                match_length = match_slices(self._text, j, len(self._text), self._text, child.left, child.right)
                j += match_length
                if match_length == child.right - child.left:
                    cursor = child
                    continue
                split = Node(next(self._id_gen), child.left, child.left + match_length)
                child.left += match_length
                cursor.children[self._text[split.left]] = split
                split.children[self._text[child.left]] = child
                split.parent = cursor
                child.parent = split
                cursor = split
                break
            leaf = Node(next(self._id_gen), j, len(self._text), i)
            cursor.children[self._text[j]] = leaf
            leaf.parent = cursor
        return root

    def _build_ukkonen(self) -> Node:
        """
        Build the suffix tree using ukkonen algorithm.
        This implementation is not online, since it immediately sets the final right value of the leafs.
        Although, it can be converted to the online version by making the node.right property a reference.

        Different from Node class, the right index used in ukkonen construction functions is inclusive.

        > complexity
        - time: `O(n)`
        - space: `O(n)`
        - `n`: length of `self._text`
        """

        def update(
            cursor: Node, left: int, right: int, slinks: dict[int, Node], match: int
        ) -> tuple[Node, int, int, int]:
            previous_border: Optional[Node] = None
            is_terminal, border = test_and_split(cursor, left, right)
            while not is_terminal:
                leaf_node = Node(next(self._id_gen), right, len(self._text), match)
                match += 1
                border.children[self._text[right]] = leaf_node
                leaf_node.parent = border
                if previous_border is not None:
                    slinks[previous_border.id] = border
                previous_border = border
                cursor, left, right = canonise(slinks[cursor.id], left, right)
                is_terminal, border = test_and_split(cursor, left, right)
            if previous_border and border:
                slinks[previous_border.id] = border
            return cursor, left, right, match

        def test_and_split(cursor: Node, left: int, right: int) -> tuple[bool, Node]:
            if right == left:
                return cursor.id == -1 or cursor.children is not None and self._text[right] in cursor.children, cursor
            child = cursor.children[self._text[left]]
            if self._text[child.left + (right - left)] == self._text[right]:
                return True, cursor
            split_node = Node(next(self._id_gen), child.left, child.left + (right - left))
            child.left += right - left
            cursor.children[self._text[split_node.left]] = split_node
            split_node.children[self._text[child.left]] = child
            split_node.parent = cursor
            child.parent = split_node
            return False, split_node

        def canonise(cursor: Node, left: int, right: int) -> tuple[Node, int, int]:
            if right == left:
                return cursor, left, right
            child = cursor.children[self._text[left]]
            while child.right - child.left <= right - left:
                left += child.right - child.left
                cursor = child
                if left < right:
                    child = cursor.children[self._text[left]]
            return cursor, left, right

        root = Node(next(self._id_gen), -1, 0)
        ground = Node(-1, -1, -1)
        ground.children = collections.defaultdict(lambda: root)
        root.parent = ground
        suffix_links: dict[int, Node] = {}
        suffix_links[root.id] = ground
        cursor = root
        left = 0
        right = 0
        match = 0
        for _ in range(len(self._text)):
            cursor, left, right, match = update(cursor, left, right, suffix_links, match)
            cursor, left, right = canonise(cursor, left, right + 1)
        root.parent = cast(Any, None)
        return root

    def _pre(self, node: Node) -> Generator[Node, None, None]:
        """
        Helper to navigate `node` children in pre order.
        """
        yield node
        if node.children is not None:
            for child in node.children.values():
                yield from self._pre(child)

    def _post(self, node: Node) -> Generator[Node, None, None]:
        """
        Helper to navigate `node` children in post order.
        """
        if node.children is not None:
            for child in node.children.values():
                yield from self._post(child)
        yield node

    def _compute_node_depths(self) -> list[int]:
        """
        Compute the depth of all nodes in the suffix tree.

        > complexity
        - time: `O(n)`
        - space: `O(n)`
        - `n`: number of nodes in the suffix tree, which is proportional to the length of `self._text`

        > parameters
        - `return`: list indexed by node ids containing the node depth
        """
        node_depths = [0] * self._node_count
        for node in self._pre(self._root):
            if node.parent is not None:
                node_depths[node.id] = node_depths[node.parent.id] + (node.right - node.left)
        return node_depths

    def _compute_subtree_leaves(self) -> list[int]:
        """
        Compute the number of leaves for all subtrees of the suffix tree.
        Each subtree is represented by its local root node id.

        > complexity
        - time: `O(n)`
        - space: `O(n)`
        - `n`: number of nodes in the suffix tree, which is proportional to the length of `self._text`

        > parameters
        - `return`: list indexed by node id containing number of leaf nodes in the subtree represented by that node
        """
        subtree_leaves = [0] * self._node_count
        for node in self._post(self._root):
            if node.match != -1:
                subtree_leaves[node.id] = 1
            if node.parent is not None:
                subtree_leaves[node.parent.id] += subtree_leaves[node.id]
        return subtree_leaves

    def _compute_leaves_references(self) -> list[Node]:
        """
        Compute a list with references for all leaves of the tree indexed by match index
        Only leaves can be correctly indexed in this manner, the output list has the size of `self._text`, each index
        points to a leaf of the tree.

        > complexity
        - time: `O(n)`
        - space: `O(n)`
        - `n`: number of nodes in the suffix tree, which is proportional to the length of `self._text`

        > parameters
        - `return`: list of leaf nodes, indexed by match index
        """
        leaves_references: list[Node] = [self._root] * len(self._text)
        for node in self._pre(self._root):
            if node.match != -1:
                leaves_references[node.match] = node
        return leaves_references

    def _search(self, pattern: str) -> Optional[Node]:
        """
        Find the node where the occurrence of `pattern` ends in the suffix tree.
        If `pattern` ends in the middle of an edge, the next node is returned, if `pattern` falls of the tree, `None` is
        returned.

        > complexity
        - time: `O(p)`
        - space: `O(1)`
        - `p`: length of `pattern`

        > parameters
        - `pattern`: pattern
        - `return`: node of the `pattern` occurrence
        """
        if len(pattern) == 0:
            raise Exception("empty pattern")
        j = 0
        cursor = self._root
        while pattern[j] in cursor.children:
            child: Node = cursor.children[pattern[j]]
            match_length = match_slices(pattern, j, len(pattern), self._text, child.left, child.right)
            j += match_length
            cursor = child
            if match_length == child.right - child.left and j < len(pattern):
                continue
            break
        return cursor if j == len(pattern) else None

    def occurrences(self, pattern: str) -> list[int]:
        """
        Check base class.

        > complexity
        - time: `O(p+q)`
        - space: `O(q)`
        - `p`: length of `pattern`
        - `q`: number of occurrences
        """
        cursor = self._search(pattern)
        if cursor is None:
            return []
        return [node.match for node in self._pre(cursor) if node.match != -1]

    def occurrences_count(self, pattern: str) -> int:
        """
        Check base class.

        > complexity
        - time: `O(p)`
        - space: `O(1)`
        - `p`: length of `pattern`
        """
        cursor = self._search(pattern)
        if cursor is None:
            return 0
        return self._subtree_leaves[cursor.id]

    def longest_repeated_substring(self, repetitions: int = 2) -> list[int]:
        """
        Check base class.

        > complexity
        - time: `O(n+q)`
        - space: `O(q)`
        - `n`: number of nodes in the suffix tree, which is proportional to the length of `self._text`
        - `q`: number of occurrences
        """
        if repetitions < 2:
            raise Exception("repetitions must be at least 2")
        current = self._root
        depth = self._node_depths[current.id]
        for node in self._pre(self._root):
            if self._subtree_leaves[node.id] >= repetitions and (node_depth := self._node_depths[node.id]) > depth:
                current = node
                depth = node_depth
        return [node.match for node in self._pre(current) if node.match != -1] if depth > 0 else list[int]()

    def longest_common_prefix(self, i: int, j: int) -> int:
        """
        Check base class.

        > complexity
        - time: `O(1)`
        - space: `O(1)`
        """
        i, j = (i, j) if i < j else (j, i)
        if not (0 <= i <= j < len(self._text)):
            raise IndexError(f"text index i ({i}) or j ({j}) out of range [0, {len(self._text)})")
        i_match_node = self._leaves_references[i]
        j_match_node = self._leaves_references[j]
        lowest_common_ancestor = self._rmq_backward_mapper[
            self._rmq.rmq(self._rmq_forward_mapper[i_match_node.id][0], self._rmq_forward_mapper[j_match_node.id][0])
        ]
        return self._node_depths[lowest_common_ancestor.id]


def test():
    import random
    import string

    from ...test import benchmark, verify

    for strategy in ("naive", "ukkonen"):
        print("strategy:", strategy)
        suffix_tree = SuffixTree("senselessness", cast(Any, strategy))
        print(suffix_tree)
        verify(
            (
                (suffix_tree.occurrences, ("s",)),
                (suffix_tree.occurrences, ("e",)),
                (suffix_tree.occurrences, ("ss",)),
                (suffix_tree.occurrences_count, ("s",)),
                (suffix_tree.occurrences_count, ("ss",)),
                (suffix_tree.longest_repeated_substring, (2,)),
                (suffix_tree.longest_repeated_substring, (4,)),
                (suffix_tree.longest_common_prefix, (0, 0)),
                (suffix_tree.longest_common_prefix, (0, 3)),
                (suffix_tree.longest_common_prefix, (6, 10)),
            )
        )
        print()
    benchmark(
        (
            ("  suffix tree naive", lambda text: SuffixTree(text, "naive")),
            ("suffix tree ukkonen", lambda text: SuffixTree(text, "ukkonen")),
        ),
        test_inputs=("hello world!", "cagtcatgcatacgtctatatcggctgc"),
        bench_sizes=(0, 1, 10, 100, 1000, 10000, 100000),
        bench_input=lambda s: "".join(random.choices(string.printable, k=s)),
        bench_repeat=10,
    )


if __name__ == "__main__":
    test()
