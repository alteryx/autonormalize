import featuretools as ft

from . import dfd, normalize
from .classes import Dependencies


def find_dependencies(df, accuracy=0.98, rep_percent=0.85, index=None):
    """
    Finds dependencies within dataframe df with the DFD search algorithm.
    Returns the dependencies as a Dependencies object.

    Arugments:

    df (Dataframe object): the dataframe containing data

    accuracy (0 < float <= 1.00; default = 0.98): the accuracy threshold
    required in order to conclude a dependency (i.e. with accuracy = 0.98,
    0.98 of the rows must hold true the dependency LHS --> RHS)

    rep_percent (0 < float <= 1.00; default = 0.85): the maximum amount of
    data that may be unique in order to determine a dependency (i.e. with
    rep_percent = 0.85, if less than 15% of rows are repeated for the columns
    in LHS + RHS, no dependency will be concluded.)

    index (string: optional): name of column that is intended index of df

    Returns:

    dependencies (Dependencies object): the dependencies found in the data
    within the contraints provided
    """
    deps = Dependencies(dfd.dfd(df, accuracy, rep_percent, index))
    if index is None:
        prim_key = list(sorted(deps.find_candidate_keys(), key=len)[0])
        deps.set_prim_key(prim_key)
    else:
        deps.set_prim_key([index])
    return deps


def normalize_dependencies(dependencies):
    """
    Breaks up a set of dependency relations into groups that are normalized,
    meaning there are no partial or transitive dependencies within each group.

    Arguments:

    dependencies (Dependencies object): the dependencies to be normalized

    Returns:

    dependencies_groups (Dependencies list): list of Dependencies objects each
    containing the relations in a new group
    """
    return normalize.normalize(dependencies)


def normalize_dataframe(df, dependencies):
    """
    Normalizes a dataframe based on the dependencies given.

    Arguments:
    df (DataFrame): dataframe to split up
    dependencies (Dependencies object): the dependencies to be normalized

    Returns:
    new_dfs (DataFrame list): list of new dataframes
    """
    depdf = normalize.DepDF(dependencies, df, dependencies.get_prim_key())
    normalize.normalize_dataframe(depdf)
    return depdf.return_dfs()


def make_entityset(df, dependencies, name=None, time_index=None):
    """
    Creates a normalized EntitySet from df based on the dependencies given.

    Arguments:
    df (DataFrame): dataframe to normalize and make entity set from
    dependencies (Dependenies object): the dependencies discovered in df
    name (string: optional): the name of created EntitySet

    Returns:
    entityset (ft.EntitySet object): created entity set
    """
    depdf = normalize.DepDF(dependencies, df, dependencies.get_prim_key())
    normalize.normalize_dataframe(depdf)
    normalize.make_indexes(depdf)

    entities = {}
    relationships = []

    stack = [depdf]

    while stack != []:
        current = stack.pop()
        if time_index in current.df.columns:
            entities[current.index[0]] = (current.df, current.index[0], time_index)
        else:
            entities[current.index[0]] = (current.df, current.index[0])
        for child in current.children:
            # add to stack
            # add relationship
            stack.append(child)
            relationships.append((child.index[0], child.index[0], current.index[0], child.index[0]))

    return ft.EntitySet(name, entities, relationships)


def auto_entityset(df, accuracy=0.98, rep_percent=0.85, index=None, name=None, time_index=None):
    """
    Creates a normalized entityset from a dataframe.

    Arugments:

    df (Dataframe object): the dataframe containing data

    accuracy (0 < float <= 1.00; default = 0.98): the accuracy threshold
    required in order to conclude a dependency (i.e. with accuracy = 0.98,
    0.98 of the rows must hold true the dependency LHS --> RHS)

    rep_percent (0 < float <= 1.00; default = 0.85): the maximum amount of
    data that may be unique in order to determine a dependency (i.e. with
    rep_percent = 0.85, if less than 15% of rows are repeated for the columns
    in LHS + RHS, no dependency will be concluded.)

    index (string: optional): name of column that is intended index of df

    name (string: optional): the name of created EntitySet

    time_index (str: optional): name of time column in the dataframe.

    Returns:

    entityset (ft.EntitySet object): created entity set
    """
    return make_entityset(df, find_dependencies(df, accuracy, rep_percent, index), name, time_index)


def auto_normalize(df):
    """
    Normalizes dataframe via dependencies discovered in data.

    Arguments:
    df (DataFrame): dataframe to split up

    Returns:
    new_dfs (DataFrame list): list of new dataframes
    """
    return normalize_dataframe(df, find_dependencies(df))
