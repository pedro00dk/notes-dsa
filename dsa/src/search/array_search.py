import math
from typing import Callable, Optional


def binary_search(
    array: list[float],
    key: float,
    comparator: Callable[[float, float], float] = lambda a, b: a - b,
    left: Optional[int] = None,
    right: Optional[int] = None,
) -> int:
    """
    Binary search algorithm.
    Require `array` to be sorted based on `comparator`.

    > complexity
    - time: `O(log(n))`
    - space: `O(1)`
    - `n`: length of `array`

    > parameters
    - `array`: array to search `key`
    - `key`: key to be search in `array`
    - `comparator`: comparator of values
    - `left`: starting index to search
    - `right`: ending index to search
    - `return`: index of `key` in `array`
    """
    left = left if left is not None else 0
    right = right if right is not None else len(array) - 1
    while left <= right:
        center = (left + right) // 2
        comparison = comparator(key, array[center])
        if comparison < 0:
            right = center - 1
        elif comparison > 0:
            left = center + 1
        else:
            return center
    raise KeyError(f"key ({key}) not found")


def k_ary_search(
    array: list[float],
    key: float,
    comparator: Callable[[float, float], float] = lambda a, b: a - b,
    left: Optional[int] = None,
    right: Optional[int] = None,
    k: int = 4,
) -> int:
    """
    K-ary search algorithm.
    Require `array` to be sorted based on `comparator`.

    > complexity
    - time: `O(k*log(n,k))`
    - space: `O(1)`
    - `n`: length of `array`
    - `k`: search arity, absolute value of parameter `k`

    > parameters
    - `array`: array to search `key`
    - `key`: key to be search in `array`
    - `comparator`: comparator of values
    - `left`: starting index to search
    - `right`: ending index to search
    - `k`: number of buckets to subdivide search
    - `return`: index of `key` in `array`
    """
    left = left if left is not None else 0
    right = right if right is not None else len(array) - 1
    k = max(k, 2)
    while left <= right:
        step = (right - left) / k
        base_left = left
        for i in range(1, k):
            center = base_left + math.floor(step * i)
            comparison = comparator(key, array[center])
            if comparison < 0:
                right = center - 1
                break
            elif comparison > 0:
                left = center + 1
            else:
                return center
    raise KeyError(f"key ({key}) not found")


def interpolation_search(
    array: list[int],
    key: int,
    comparator: Callable[[int, int], int] = lambda a, b: a - b,
    left: Optional[int] = None,
    right: Optional[int] = None,
) -> int:
    """
    Interpolation search algorithm.
    Require `array` to be sorted based on `comparator`.
    Faster than binary search for uniformly distributed arrays.

    > complexity
    - time: `O(log(log(n))) uniformly distributed arrays, worst: O(n)`
    - space: `O(1)`
    - `n`: length of `array`

    > parameters
    - `array`: array to search `key`
    - `key`: key to be search in `array`
    - `comparator`: comparator for `<T>` type values
    - `left`: starting index to search
    - `right`: ending index to search

    - `return`: index of `key` in `array`
    """
    left = left if left is not None else 0
    right = right if right is not None else len(array) - 1
    while array[left] != array[right] and array[left] <= key <= array[right]:
        center = left + ((key - array[left]) * (right - left)) // (array[right] - array[left])
        comparison = comparator(key, array[center])
        if comparison < 0:
            right = center - 1
        elif comparison > 0:
            left = center + 1
        else:
            return center
    if comparator(key, array[left]) == 0:
        return left
    raise KeyError(f"key ({key}) not found")


def exponential_search(
    array: list[float],
    key: float,
    comparator: Callable[[float, float], float] = lambda a, b: a - b,
    left: Optional[int] = None,
    right: Optional[int] = None,
) -> int:
    """
    Exponential search algorithm.
    Require `array` to be sorted based on `comparator`.

    > complexity
    - time: `O(log(i))`
    - space: `O(1)`
    - `i`: index of `key` in `array`

    > parameters
    - `array`: array to search `key`
    - `key`: key to be search in `array`
    - `comparator`: comparator for `<T>` type values
    - `left`: starting index to search
    - `right`: ending index to search

    - `return`: index of `key` in `array`
    """
    left = left if left is not None else 0
    right = right if right is not None else len(array) - 1
    bound = 1
    while bound * 2 <= left or bound <= right and key > array[bound]:
        bound *= 2
    return binary_search(array, key, comparator, max(bound // 2, left), min(bound, right))


def test():
    import random

    from ..test import benchmark, verify

    verify(
        (
            (binary_search, ([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], 6), 6),
            (binary_search, ([0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20], 8), 4),
            (binary_search, ([1, 10, 100, 1000, 10000, 100000, 1000000], 10), 1),
            (k_ary_search, ([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], 6), 6),
            (k_ary_search, ([0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20], 8), 4),
            (k_ary_search, ([1, 10, 100, 1000, 10000, 100000, 1000000], 10), 1),
            (interpolation_search, ([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], 6), 6),
            (interpolation_search, ([0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20], 8), 4),
            (interpolation_search, ([1, 10, 100, 1000, 10000, 100000, 1000000], 10), 1),
            (exponential_search, ([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], 6), 6),
            (exponential_search, ([0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20], 8), 4),
            (exponential_search, ([1, 10, 100, 1000, 10000, 100000, 1000000], 10), 1),
        )
    )
    benchmark(
        (
            ("       binary search", lambda array: binary_search(array, random.sample(array, 1)[0])),
            ("  k-ary search (k=2)", lambda array: k_ary_search(array, random.sample(array, 1)[0], k=2)),
            ("  k-ary search (k=4)", lambda array: k_ary_search(array, random.sample(array, 1)[0], k=4)),
            ("  k-ary search (k=8)", lambda array: k_ary_search(array, random.sample(array, 1)[0], k=8)),
            (" k-ary search (k=16)", lambda array: k_ary_search(array, random.sample(array, 1)[0], k=16)),
            ("interpolation search", lambda array: interpolation_search(array, random.sample(array, 1)[0])),
            ("  exponential search", lambda array: exponential_search(array, random.sample(array, 1)[0])),
        ),
        test_inputs=(),
        bench_sizes=(1, 10, 100, 1000, 10000, 100000),
        bench_input=lambda s: [*range(s)],
        bench_repeat=1,
        bench_tries=100000,
    )


if __name__ == "__main__":
    test()
