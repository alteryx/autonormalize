import os

import pandas as pd

from autonormalize import dfd
from autonormalize.classes import Masks

path = os.getcwd()

dic_1 = {
    "id": [100, 101, 102, 103, 104, 105, 106, 107, 109],
    "age": [1, 2, 3, 4, 5, 6, 7, 5, 6],
    "height": [4, 5, 6, 7, 8, 9, 10, 8, 9],
    "less_than_5": [1, 1, 1, 1, 0, 0, 0, 0, 0]
}

df_1 = pd.DataFrame(dic_1)
# A = index,   B = random,   C = random,   D = random,
# E = c != 1,   F = b < 10,   G = c + d
df_2 = pd.read_csv(os.path.join(path, 'autonormalize/examples/example_3'))


def assert_equal_dependency_dics(dep1, dep2):

    assert set(dep1.keys()) == set(dep2.keys())

    for rhs in dep1.keys():
        one = map(frozenset, dep1[rhs])
        two = map(frozenset, dep2[rhs])
        assert set(one) == set(two)


def serialization_equal(dic_1, dic_2):
    for x in dic_1:
        if x not in dic_2:
            return False
        if sorted(dic_1[x]) != sorted(dic_2[x]):
            return False
    return True


def test_dfd():
    dep = {"id": [], "age": [["height"], ["id"]], "height": [["age"], ["id"]],
           "less_than_5": [["age"], ["height"], ["id"]]}
    assert_equal_dependency_dics(dfd.dfd(df_1, 0.98).serialize(), dep)

    dep = {"A": [], "B": [["A"]], "C": [["D", "G"], ["A"]], "D": [["C", "G"], ["A"]],
           "E": [["C"], ["D", "G"], ["A"]], "F": [["B"], ["A"]], "G": [["C", "D"], ["A"]]}
    assert_equal_dependency_dics(dfd.dfd(df_2, 0.98).serialize(), dep)


def test_compute_partitions():
    mask = Masks(['a', 'b', 'c'])
    a = [6, 2, 3, 7, 8, 1, 0, 2, 0, 3, 6, 0, 4, 6, 8, 7, 6, 8, 1, 5, 1, 3, 3, 0, 0, 4, 5, 5, 7, 0, 8, 2, 4, 7, 0, 0, 6, 4, 6, 8]
    # b = [int(x%2 == 0) for x in a]
    b = [1, 1, 0, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1]
    # c = [(a[i] + b[i])<4 for i in range(40)]
    c = [False, True, True, False, False, True, True, True, True, True, False, True, False, False, False, False, False, False, True, False, True, True, True, True, True, False, False, False, False, True, False, True, False, False, True, True, False, False, False, False]
    df = pd.DataFrame({'a': a, 'b': b, 'c': c})
    assert dfd.compute_partitions(df, 'c', frozenset(['a', 'b']), {}, 1.00, mask)
    assert dfd.compute_partitions(df, 'c', frozenset(['a', 'b']), {}, 0.90, mask)

    assert not dfd.compute_partitions(df, 'a', frozenset(['c']), {}, 1.00, mask)
    assert not dfd.compute_partitions(df, 'a', frozenset(['c']), {}, 0.90, mask)

    c[0] = True
    df = pd.DataFrame({'a': a, 'b': b, 'c': c})
    assert dfd.compute_partitions(df, 'c', frozenset(['a', 'b']), {}, 0.97, mask)
    assert not dfd.compute_partitions(df, 'c', frozenset(['a', 'b']), {}, 0.98, mask)
    c[35] = False
    df = pd.DataFrame({'a': a, 'b': b, 'c': c})
    assert dfd.compute_partitions(df, 'c', frozenset(['a', 'b']), {}, 0.95, mask)
    assert not dfd.compute_partitions(df, 'c', frozenset(['a', 'b']), {}, 0.96, mask)


# def test_approximate_dependencies():
#     mask = dfd.Masks(['a', 'b', 'c'])
#     a = [6, 2, 3, 7, 8, 1, 0, 2, 0, 3, 6, 0, 4, 6, 8, 7, 6, 8, 1, 5, 1, 3, 3, 0, 0, 4, 5, 5, 7, 0, 8, 2, 4, 7, 0, 0, 6, 4, 6, 8]
#     # b = [int(x%2 == 0) for x in a]
#     b = [1, 1, 0, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1]
#     # c = [(a[i] + b[i])<4 for i in range(40)]
#     c = [False, True, True, False, False, True, True, True, True, True, False, True, False, False, False, False, False, False, True, False, True, True, True, True, True, False, False, False, False, True, False, True, False, False, True, True, False, False, False, False]
#     df = pd.DataFrame({'a': a, 'b': b, 'c': c})
#     assert dfd.approximate_dependencies([0, 1], 2, df, 1.00, mask, 0.90)
#     assert dfd.approximate_dependencies(set([0, 1]), 2, df, .90, mask, 0.90)
#     c[0] = True
#     df = pd.DataFrame({'a': a, 'b': b, 'c': c})
#     assert dfd.approximate_dependencies([0, 1], 2, df, .97, mask, 0.90)
#     assert not dfd.approximate_dependencies(set([0, 1]), 2, df, .98, mask, 0.90)
#     c[35] = False
#     df = pd.DataFrame({'a': a, 'b': b, 'c': c})
#     assert dfd.approximate_dependencies([0, 1], 2, df, .95, mask, 0.90)
#     assert not dfd.approximate_dependencies([0, 1], 2, df, .96, mask, 0.90)
