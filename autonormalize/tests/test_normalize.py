import pandas as pd
import pytest
from pandas.util.testing import assert_frame_equal

import featuretools as ft
from featuretools.variable_types import (
    Categorical,
    Datetime,
    DatetimeTimeIndex,
    Id,
    Index,
    Numeric,
    Text,
    ZIPCode
)

from autonormalize import autonormalize, classes, normalize

# from classes import Dependencies

# from normalize import normalize, find_most_comm, split_on_dep

@pytest.fixture
def teams_input():
    class Teams:
        def get_df(self):
            dic = {'team': ['Red', 'Red', 'Red', 'Orange', 'Orange', 'Yellow',
                            'Yellow', 'Green', 'Green', 'Blue'],
                   'jersey_num': [1, 2, 3, 1, 2, 1, 5, 8, 2, 2],
                   'player_name': ['A', 'B', 'C', 'D', 'A', 'E', 'B', 'A', 'G', 'H'],
                   'city': ['boston', 'boston', 'boston', 'chicago', 'chicago',
                            'honolulu', 'honolulu', 'boston', 'boston', 'austin'],
                   'state': ['MA', 'MA', 'MA', 'IL', 'IL', 'HI', 'HI', 'MA', 'MA', 'TX']}
            return pd.DataFrame(dic)

        def get_deps(self):
            return classes.Dependencies({'team': [['player_name', 'jersey_num']],
                                         'jersey_num': [['player_name', 'team']],
                                         'player_name': [['team', 'jersey_num']],
                                         'city': [['team'], ['state'], ['player_name', 'jersey_num']],
                                         'state': [['team'], ['player_name', 'jersey_num'],
                                                   ['city']]}, ['team', 'jersey_num'])
    return Teams()


def test_normalize():
    # how to test that relations remain the same???
    # check that there are no new relations?
    # there can be less however?
    dep_dic = {
        'A': [], 'B': [], 'C': [], 'D': [['F']],
        'E': [['A', 'B', 'C', 'D']], 'F': [['A', 'B']]}
    dep = classes.Dependencies(dep_dic, ['A', 'B', 'C'])
    df = pd.DataFrame(columns=['A', 'B', 'C', 'D', 'E', 'F'], dtype='int64')
    new = normalize.normalize(dep, df)
    dep_dic = dep.serialize()
    for x in new:
        trans_deps = x.find_trans_deps()
        normalize.filter(trans_deps, df)
        assert trans_deps == []
        part_deps = x.find_partial_deps()
        normalize.filter(part_deps, df)
        assert part_deps == []
        dic = x.serialize()
        for rhs in dic:
            for lhs in dic[rhs]:
                assert lhs in dep_dic[rhs]


def test_find_most_comm():
    deps = classes.Dependencies({}, ['d'])
    rels = [(['a'], 'b'), (['b'], 'c'), (['b'], 'a'),
            (['d'], 'a')]
    assert normalize.find_most_comm(rels, deps) == ['b']
    rels = [(['a', 'c'], 'b'), (['b'], 'c'), (['b'], 'a'),
            (['d'], 'a'), (['a', 'c'], 'b')]
    assert normalize.find_most_comm(rels, deps) == ['b']


def test_split_on_dep():
    dep_dic = {'A': [], 'B': [], 'C': [['A'], ['B']], 'D': [['B']]}
    new = normalize.split_on_dep(['B'], classes.Dependencies(dep_dic))
    assert new[0].serialize() == {'A': [], 'B': []}
    assert new[1].serialize() == {'B': [], 'C': [['B']], 'D': [['B']]}


def test_drop_primary_dups():
    df_dic = {"city": ['honolulu', 'boston', 'honolulu', 'dallas', 'seattle', 'honolulu', 'boston', 'honolulu', 'seattle', 'boston'],
              "state": ['HI', 'MA', 'HI', 'TX', 'WA', 'AL', 'MA', 'HI', 'WA', 'NA'],
              "is_liberal": [True, True, True, False, True, True, True, True, True, False]}
    df = pd.DataFrame(df_dic)
    new_df = normalize.drop_primary_dups(df, ['city'])

    df_new_dic = {"city": ["boston", "dallas", "honolulu", "seattle"],
                  "state": ["MA", "TX", "HI", "WA"],
                  "is_liberal": [True, False, True, True]}
    assert_frame_equal(pd.DataFrame(df_new_dic), new_df)

    df = pd.DataFrame([[True, True, True], [True, True, True], [False, True, False],
                       [True, False, False], [True, False, False], [False, True, False], [True, False, True]],
                      columns=["requires_light", "is_dark", "light_on"])

    new_df = normalize.drop_primary_dups(df, ['requires_light', 'is_dark'])
    # compare_df = pd.DataFrame([[True, False, False], [False, True, False], [True, True, True]],
    #                           columns=["requires_light", "is_dark", "light_on"])
    # compare_df = compare_df.sort_values(by=["requires_light", "is_dark"]).reset_index(drop=True)

    for index, row in new_df.iterrows():
        if row['requires_light'] and not row['is_dark']:
            assert not row['light_on']
        if not row['requires_light'] and row['is_dark']:
            assert not row['light_on']
        if row['requires_light'] and row['is_dark']:
            assert row['light_on']


def test_filter():
    keys = [(['A'], 'E'), (['A', 'B'], 'E'), (['C', 'D'], 'E')]
    df = pd.DataFrame(columns=['A', 'B', 'C', 'D'])
    df = df.astype({'A': 'float64', 'B': 'int64', 'C': 'category', 'D': 'object'})

    normalize.filter(keys, df)
    assert keys == [(['C', 'D'], 'E')]


def test_choose_index():
    keys = [['A'], ['A_id'], ['B']]
    df = pd.DataFrame(columns=['A', 'B', 'C', 'D'])
    assert normalize.choose_index(keys, df) == ['A_id']

    keys = [['B'], ['C'], ['A']]
    assert normalize.choose_index(keys, df) == ['A']

    keys = [['A', 'C'], ['A', 'B']]
    assert normalize.choose_index(keys, df) == ['A', 'B']


def test_normalize_dataframe(teams_input):
    depdf = normalize.DepDF(teams_input.get_deps(), teams_input.get_df(), teams_input.get_deps().get_prim_key())
    normalize.normalize_dataframe(depdf)
    new_dfs = depdf.return_dfs()

    assert len(new_dfs) == 3

    dic_one = {'team': ['Red', 'Red', 'Red', 'Orange', 'Orange', 'Yellow',
               'Yellow', 'Green', 'Green', 'Blue'],
               'jersey_num': [1, 2, 3, 1, 2, 1, 5, 8, 2, 2],
               'player_name': ['A', 'B', 'C', 'D', 'A', 'E', 'B', 'A', 'G', 'H']}

    dic_two = {'team': ['Red', 'Orange', 'Yellow', 'Green', 'Blue', 'Blue'],
               'city': ['boston', 'chicago', 'honolulu', 'boston', 'austin', 'austin']}

    dic_three = {'city': ['boston', 'chicago', 'honolulu', 'austin', 'austin'],
                 'state': ['MA', 'IL', 'HI', 'TX', 'TX']}

    assert new_dfs[0].equals(normalize.drop_primary_dups(pd.DataFrame(dic_one), ['team', 'jersey_num']))
    assert new_dfs[1].equals(normalize.drop_primary_dups(pd.DataFrame(dic_two), ['team']))
    assert new_dfs[2].equals(normalize.drop_primary_dups(pd.DataFrame(dic_three), ['city']))


def test_make_indexes():

    dic = {"id": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
           "month": ['dec', 'dec', 'jul', 'jul', 'dec', 'jul', 'jul',
                     'jul', 'dec', 'jul'],
           "hemisphere": ['N', 'N', 'N', 'N', 'S', 'S', 'S', 'S', 'S', 'N'],
           "is_winter": [True, True, False, False, False, True, True, True, False, False]}

    df = pd.DataFrame(dic)
    deps = classes.Dependencies({'id': [],
                                 'month': [['id'], ['hemisphere', 'is_winter']],
                                 'hemisphere': [['month', 'is_winter'], ['id']],
                                 'is_winter': [['month', 'hemisphere'], ['id']]}, ['id'])

    depdf = normalize.DepDF(deps, df, deps.get_prim_key())
    normalize.normalize_dataframe(depdf)
    normalize.make_indexes(depdf)
    new_dfs = depdf.return_dfs()

    mask = (new_dfs[1]['month'] == 'dec') & (new_dfs[1]['hemisphere'] == 'N')
    val = new_dfs[1][mask][new_dfs[1].columns[0]].iloc[0]
    assert new_dfs[0][new_dfs[1].columns[0]][0] == val
    assert new_dfs[0][new_dfs[1].columns[0]][1] == val

    mask = (new_dfs[1]['month'] == 'jul') & (new_dfs[1]['hemisphere'] == 'N')
    val = new_dfs[1][mask][new_dfs[1].columns[0]].iloc[0]
    assert new_dfs[0][new_dfs[1].columns[0]][2] == val
    assert new_dfs[0][new_dfs[1].columns[0]][3] == val
    assert new_dfs[0][new_dfs[1].columns[0]][9] == val

    mask = (new_dfs[1]['month'] == 'dec') & (new_dfs[1]['hemisphere'] == 'S')
    val = new_dfs[1][mask][new_dfs[1].columns[0]].iloc[0]
    assert new_dfs[0][new_dfs[1].columns[0]][4] == val
    assert new_dfs[0][new_dfs[1].columns[0]][8] == val

    mask = (new_dfs[1]['month'] == 'jul') & (new_dfs[1]['hemisphere'] == 'S')
    val = new_dfs[1][mask][new_dfs[1].columns[0]].iloc[0]
    assert new_dfs[0][new_dfs[1].columns[0]][5] == val
    assert new_dfs[0][new_dfs[1].columns[0]][6] == val
    assert new_dfs[0][new_dfs[1].columns[0]][7] == val


def test_variable_types():
    df = ft.demo.load_mock_customer(n_customers=20, n_products=12, n_sessions=50,
                                    n_transactions=100, return_single_table=True)
    entityset = ft.EntitySet()
    entityset.entity_from_dataframe(entity_id='Customer Transactions',
                                    dataframe=df,
                                    time_index='transaction_time',
                                    variable_types={'zip_code': ZIPCode})

    normalized_entityset = autonormalize.normalize_entity(entityset)

    assert normalized_entityset['transaction_id'].variable_types['transaction_id'] == Index
    assert normalized_entityset['transaction_id'].variable_types['session_id'] == Id
    assert normalized_entityset['transaction_id'].variable_types['transaction_time'] == DatetimeTimeIndex
    assert normalized_entityset['transaction_id'].variable_types['product_id'] == Id
    assert normalized_entityset['transaction_id'].variable_types['amount'] == Numeric

    assert normalized_entityset['product_id'].variable_types['product_id'] == Index
    assert normalized_entityset['product_id'].variable_types['brand'] == Categorical

    assert normalized_entityset['session_id'].variable_types['session_id'] == Index
    assert normalized_entityset['session_id'].variable_types['customer_id'] == Id
    assert normalized_entityset['session_id'].variable_types['device'] == Categorical
    assert normalized_entityset['session_id'].variable_types['session_start'] == Datetime

    assert normalized_entityset['customer_id'].variable_types['customer_id'] == Index
    assert normalized_entityset['customer_id'].variable_types['join_date'] == Datetime
    assert normalized_entityset['customer_id'].variable_types['date_of_birth'] == Datetime
    assert normalized_entityset['customer_id'].variable_types['zip_code'] == ZIPCode


def test_make_entityset_default_args(teams_input):
    normalized_entityset = autonormalize.make_entityset(teams_input.get_df(), teams_input.get_deps())

    dic_one = {'jersey_num_team': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
               'team': ['Red', 'Red', 'Red', 'Orange', 'Orange', 'Yellow',
                        'Yellow', 'Green', 'Green', 'Blue'],
               'jersey_num': [1, 2, 3, 1, 2, 1, 5, 8, 2, 2],
               'player_name': ['A', 'B', 'C', 'D', 'A', 'E', 'B', 'A', 'G', 'H']}

    dic_two = {'team': ['Blue', 'Green', 'Orange', 'Red', 'Yellow'],
               'city': ['austin', 'boston', 'chicago', 'boston', 'honolulu']}

    dic_three = {'city': ['austin', 'boston', 'chicago', 'honolulu'],
                 'state': ['TX', 'MA', 'IL', 'HI']}

    assert len(normalized_entityset.entities) == 3

    assert normalized_entityset.entities[0].df.equals(pd.DataFrame(dic_one))
    assert normalized_entityset.entities[1].df.equals(pd.DataFrame(
        dic_two, index=['Blue', 'Green', 'Orange', 'Red', 'Yellow']))
    assert normalized_entityset.entities[2].df.equals(pd.DataFrame(
        dic_three, index=['austin', 'boston', 'chicago', 'honolulu']))

    assert normalized_entityset.entities[0].variable_types['jersey_num_team'] == Index
    assert normalized_entityset.entities[0].variable_types['team'] == Id
    assert normalized_entityset.entities[0].variable_types['jersey_num'] == Numeric
    assert normalized_entityset.entities[0].variable_types['player_name'] == Categorical

    assert normalized_entityset.entities[1].variable_types['team'] == Index
    assert normalized_entityset.entities[1].variable_types['city'] == Id

    assert normalized_entityset.entities[2].variable_types['city'] == Index
    assert normalized_entityset.entities[2].variable_types['state'] == Categorical


def test_make_entityset_custom_args(teams_input):
    normalized_entityset = autonormalize.make_entityset(df=teams_input.get_df(),
                                                        dependencies=teams_input.get_deps(),
                                                        name='Teams',
                                                        variable_types={'state': Text})

    dic_one = {'jersey_num_team': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
               'team': ['Red', 'Red', 'Red', 'Orange', 'Orange', 'Yellow',
                        'Yellow', 'Green', 'Green', 'Blue'],
               'jersey_num': [1, 2, 3, 1, 2, 1, 5, 8, 2, 2],
               'player_name': ['A', 'B', 'C', 'D', 'A', 'E', 'B', 'A', 'G', 'H']}

    dic_two = {'team': ['Blue', 'Green', 'Orange', 'Red', 'Yellow'],
               'city': ['austin', 'boston', 'chicago', 'boston', 'honolulu']}

    dic_three = {'city': ['austin', 'boston', 'chicago', 'honolulu'],
                 'state': ['TX', 'MA', 'IL', 'HI']}

    assert len(normalized_entityset.entities) == 3
    assert normalized_entityset.id == 'Teams'

    assert normalized_entityset.entities[0].df.equals(pd.DataFrame(dic_one))
    assert normalized_entityset.entities[1].df.equals(pd.DataFrame(
        dic_two, index=['Blue', 'Green', 'Orange', 'Red', 'Yellow']))
    assert normalized_entityset.entities[2].df.equals(pd.DataFrame(
        dic_three, index=['austin', 'boston', 'chicago', 'honolulu']))

    assert normalized_entityset.entities[0].variable_types['jersey_num_team'] == Index
    assert normalized_entityset.entities[0].variable_types['team'] == Id
    assert normalized_entityset.entities[0].variable_types['jersey_num'] == Numeric
    assert normalized_entityset.entities[0].variable_types['player_name'] == Categorical

    assert normalized_entityset.entities[1].variable_types['team'] == Index
    assert normalized_entityset.entities[1].variable_types['city'] == Id

    assert normalized_entityset.entities[2].variable_types['city'] == Index
    assert normalized_entityset.entities[2].variable_types['state'] == Text


def test_auto_entityset_default_args(teams_input):
    normalized_entityset = autonormalize.auto_entityset(teams_input.get_df())

    dic_one = {'jersey_num_team': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
               'team': ['Red', 'Red', 'Red', 'Orange', 'Orange', 'Yellow',
                        'Yellow', 'Green', 'Green', 'Blue'],
               'jersey_num': [1, 2, 3, 1, 2, 1, 5, 8, 2, 2],
               'player_name': ['A', 'B', 'C', 'D', 'A', 'E', 'B', 'A', 'G', 'H']}

    dic_two = {'team': ['Blue', 'Green', 'Orange', 'Red', 'Yellow'],
               'city': ['austin', 'boston', 'chicago', 'boston', 'honolulu']}

    dic_three = {'city': ['austin', 'boston', 'chicago', 'honolulu'],
                 'state': ['TX', 'MA', 'IL', 'HI']}

    assert len(normalized_entityset.entities) == 3

    assert normalized_entityset.entities[0].df.equals(pd.DataFrame(dic_one))
    assert normalized_entityset.entities[1].df.equals(pd.DataFrame(
        dic_two, index=['Blue', 'Green', 'Orange', 'Red', 'Yellow']))
    assert normalized_entityset.entities[2].df.equals(pd.DataFrame(
        dic_three, index=['austin', 'boston', 'chicago', 'honolulu']))

    assert normalized_entityset.entities[0].variable_types['jersey_num_team'] == Index
    assert normalized_entityset.entities[0].variable_types['team'] == Id
    assert normalized_entityset.entities[0].variable_types['jersey_num'] == Numeric
    assert normalized_entityset.entities[0].variable_types['player_name'] == Categorical

    assert normalized_entityset.entities[1].variable_types['team'] == Index
    assert normalized_entityset.entities[1].variable_types['city'] == Id

    assert normalized_entityset.entities[2].variable_types['city'] == Index
    assert normalized_entityset.entities[2].variable_types['state'] == Categorical


def test_auto_entityset_custom_args(teams_input):
    normalized_entityset = autonormalize.auto_entityset(df=teams_input.get_df(),
                                                        name='Teams',
                                                        variable_types={'state': Text})

    dic_one = {'jersey_num_team': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
               'team': ['Red', 'Red', 'Red', 'Orange', 'Orange', 'Yellow',
                        'Yellow', 'Green', 'Green', 'Blue'],
               'jersey_num': [1, 2, 3, 1, 2, 1, 5, 8, 2, 2],
               'player_name': ['A', 'B', 'C', 'D', 'A', 'E', 'B', 'A', 'G', 'H']}

    dic_two = {'team': ['Blue', 'Green', 'Orange', 'Red', 'Yellow'],
               'city': ['austin', 'boston', 'chicago', 'boston', 'honolulu']}

    dic_three = {'city': ['austin', 'boston', 'chicago', 'honolulu'],
                 'state': ['TX', 'MA', 'IL', 'HI']}

    assert len(normalized_entityset.entities) == 3
    assert normalized_entityset.id == 'Teams'

    assert normalized_entityset.entities[0].df.equals(pd.DataFrame(dic_one))
    assert normalized_entityset.entities[1].df.equals(pd.DataFrame(
        dic_two, index=['Blue', 'Green', 'Orange', 'Red', 'Yellow']))
    assert normalized_entityset.entities[2].df.equals(pd.DataFrame(
        dic_three, index=['austin', 'boston', 'chicago', 'honolulu']))

    assert normalized_entityset.entities[0].variable_types['jersey_num_team'] == Index
    assert normalized_entityset.entities[0].variable_types['team'] == Id
    assert normalized_entityset.entities[0].variable_types['jersey_num'] == Numeric
    assert normalized_entityset.entities[0].variable_types['player_name'] == Categorical

    assert normalized_entityset.entities[1].variable_types['team'] == Index
    assert normalized_entityset.entities[1].variable_types['city'] == Id

    assert normalized_entityset.entities[2].variable_types['city'] == Index
    assert normalized_entityset.entities[2].variable_types['state'] == Text
