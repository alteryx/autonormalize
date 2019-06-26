import os

import pytest
import pandas as pd

from classes import BitIndexSet, LHSs, Dependencies, Node
import dfd

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
df_2 = pd.read_csv(os.path.join(path, 'example_3'))


def serialization_equal(dic_1, dic_2):
    for x in dic_1:
        if not x in dic_2:
            return False
        if sorted(dic_1[x]) != sorted(dic_2[x]):
            return False
    return True


def test_dfd():
    dep = {"id": [], "age": [["height"], ["id"]], "height": [["age"], ["id"]],
        "less_than_5": [["age"], ["height"], ["id"]]}
    assert serialization_equal(dfd.dfd(df_1).serialize(), dep)

    dep = {"A": [], "B": [["A"]], "C": [["D", "G"], ["A"]], "D": [["C", "G"], ["A"]],
        "E": [["C"], ["D", "G"], ["A"]], "F": [["B"], ["A"]], "G": [["C", "D"], ["A"]]}
    assert serialization_equal(dfd.dfd(df_2).serialize(), dep)
