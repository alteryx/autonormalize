import featuretools as ft

from . import dfd, normalize
from .classes import Dependencies


def find_dependencies(df, accuracy=0.98, index=None):
    """
    Finds dependencies within dataframe df with the DFD search algorithm.
    Returns the dependencies as a Dependencies object.

    Arugments:

        df (pd.Dataframe) : the dataframe containing data

        accuracy (0 < float <= 1.00; default = 0.98) : the accuracy threshold
        required in order to conclude a dependency (i.e. with accuracy = 0.98,
        0.98 of the rows must hold true the dependency LHS --> RHS)

        index (str, optional) : name of column that is intended index of df

    Returns:

        dependencies (Dependencies) : the dependencies found in the data
        within the contraints provided
    """
    deps = Dependencies(dfd.dfd(df, accuracy, index))
    if index is None:
        prim_key = normalize.choose_index(deps.find_candidate_keys(), df)
        deps.set_prim_key(prim_key)
    else:
        deps.set_prim_key([index])
    return deps


def normalize_dependencies(df, dependencies):
    """
    Breaks up a set of dependency relations into groups that are normalized,
    meaning there are no partial or transitive dependencies within each group.

    Arguments:

        dependencies (Dependencies) : the dependencies to be normalized

    Returns:

        dependencies_groups (list[Dependencies]) : list of Dependencies objects each
        containing the relations in a new group
    """
    return normalize.normalize(dependencies, df)


def normalize_dataframe(df, dependencies):
    """
    Normalizes a dataframe based on the dependencies given. Keys for the newly
    created DataFrames can only be columns that are strings, ints, or
    categories. Keys are chosen according to the priority:
    1) shortest lenghts 2) has "id" in some form in the name of an attribute
    3) has attribute furthest to left in the table

    Arguments:
        df (pd.DataFrame) : dataframe to split up
        dependencies (Dependencies) : the dependencies to be normalized

    Returns:
        new_dfs (list[DataFrame]) : list of new dataframes
    """
    depdf = normalize.DepDF(dependencies, df, dependencies.get_prim_key())
    normalize.normalize_dataframe(depdf)
    return depdf.return_dfs()


def make_entityset(df, dependencies, name=None, time_index=None):
    """
    Creates a normalized EntitySet from df based on the dependencies given.
    Keys for the newly created DataFrames can only be columns that are strings,
    ints, or categories. Keys are chosen according to the priority:
    1) shortest lenghts 2) has "id" in some form in the name of an attribute
    3) has attribute furthest to left in the table

    Arguments:
        df (pd.DataFrame) : dataframe to normalize and make entity set from
        dependencies (Dependenies) : the dependencies discovered in df
        name (str, optional) : the name of created EntitySet

    Returns:
        entityset (ft.EntitySet) : created entity set
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


def auto_entityset(df, accuracy=0.98, index=None, name=None, time_index=None):
    """
    Creates a normalized entityset from a dataframe.

    Arugments:

        df (pd.Dataframe) : the dataframe containing data

        accuracy (0 < float <= 1.00; default = 0.98) : the accuracy threshold
        required in order to conclude a dependency (i.e. with accuracy = 0.98,
        0.98 of the rows must hold true the dependency LHS --> RHS)

        index (str, optional) : name of column that is intended index of df

        name (str, optional) : the name of created EntitySet

        time_index (str, optional) : name of time column in the dataframe.

    Returns:

        entityset (ft.EntitySet) : created entity set
    """
    return make_entityset(df, find_dependencies(df, accuracy, index), name, time_index)


def auto_normalize(df):
    """
    Normalizes dataframe via dependencies discovered in data.

    Arguments:
        df (pd.DataFrame) : dataframe to split up

    Returns:
        new_dfs (list[pd.DataFrame]) : list of new dataframes
    """
    return normalize_dataframe(df, find_dependencies(df))


def normalize_entity(es, accuracy=0.98):
    """
    Returns a new normalized EntitySet from an EntitySet with a single entity.

    Arguments:
        es (ft.EntitySet) : EntitySet to normalize
        accuracy (0 < float <= 1.00; default = 0.98) : the accuracy threshold
        required in order to conclude a dependency (i.e. with accuracy = 0.98,
        0.98 of the rows must hold true the dependency LHS --> RHS)

    Returns:
        new_es (ft.EntitySet) : new normalized EntitySet
    """
    # TO DO: add option to pass an EntitySet with more than one entity, and specify which one
    # to normalize while preserving existing relationships

    if len(es.entities) > 1:
        raise ValueError('There is more than one entity in this EntitySet')
    if len(es.entities) == 0:
        raise ValueError('This EntitySet is empty')
    entity = es.entities[0]
    new_es = auto_entityset(entity.df, accuracy, index=entity.index, name=es.id, time_index=entity.time_index)
    return new_es
