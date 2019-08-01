import pandas as pd

from .classes import Dependencies


def normalize(dependencies, df):
    """
    Normalizes the dependency relationships in dependencies into new
    groups by breaking up all partial and transitive dependencies.

    Arguments:
        dependencies (Dependencies) : the dependencies to be split up

    Returns:
        new_groups (list[Dependencies]) : list of new dependencies objects
        representing the new groups
    """
    dependencies.remove_implied_extroneous()
    no_part_deps = remove_part_deps(dependencies, df)
    no_trans_deps = []
    for grp in no_part_deps:
        no_trans_deps += remove_trans_deps(grp, df)
    return no_trans_deps


class DepDF(object):
    """
    Represents dataframe and functional dependencies between columns in it.
    Used in the normalization process.

    Attributes:
        deps
        df
        parent
        children
        index
    """

    def __init__(self, deps, df, index, parent=None):
        """
        Creates a DepDF.

        Arguments:
            deps (Dependencies) : dependenies among the df
            df (pd.DataFrame) : dataframe for the object
            index (list[str]) : index columns for dataframe
            parent (DepDF, optional) : parent DepDF object
        """
        self.deps = deps
        self.df = df
        self.parent = parent
        self.children = []
        self.index = index

    def return_dfs(self):
        """
        Returns the dataframes stored in self and all its descendents.

        Returns:
            dfs (list[pd.DataFrame]) : dataframes
        """
        if self.children == []:
            return [self.df]
        result = [self.df]
        for child in self.children:
            result += child.return_dfs()
        return result


def make_indexes(depdf):
    """
    Goes through depdf, and all of its descendents, and if any have primary keys
    of more than one attribute, creates a new index column, and replaces the
    old primary key columns with the new column in the parent df.

    Arguments:
        depdf (DepDF) : depDF to make indexes for
    """
    prim_key = depdf.deps.get_prim_key()

    if len(prim_key) > 1:

        depdf.df.insert(0, '_'.join(prim_key), range(0, len(depdf.df)))
        depdf.index = ['_'.join(prim_key)]

        # now need to replace it in the parent df...
        if depdf.parent is not None:

            add = [None] * len(depdf.parent.df)
            indices = depdf.parent.df.groupby(prim_key).indices

            for name in indices:

                mask = None
                for i in range(len(prim_key)):
                    m = depdf.df[prim_key[i]] == name[i]
                    if mask is None:
                        mask = m
                    else:
                        mask = mask & m

                new_val = depdf.df[mask]['_'.join(prim_key)].item()

                for index in indices[name]:
                    add[index] = new_val

            depdf.parent.df.drop(columns=prim_key, inplace=True)
            depdf.parent.df.insert(len(depdf.parent.df.columns), '_'.join(prim_key), add)

    for child in depdf.children:
        make_indexes(child)


def normalize_dataframe(depdf):
    """
    Normalizes the dataframe represetned by depdf, created descendents
    as needed.

    Arguments:
        depdf (DepDF) : depdf to normalize
    """

    part_deps = depdf.deps.find_partial_deps()
    filter(part_deps, depdf.df)
    if part_deps != []:
        split_on = find_most_comm(part_deps, depdf.deps, depdf.df)
        split_up(split_on, depdf)
        return
    trans_deps = depdf.deps.find_trans_deps()
    filter(trans_deps, depdf.df)
    if trans_deps != []:
        split_on = find_most_comm(trans_deps, depdf.deps, depdf.df)
        split_up(split_on, depdf)
        return


def split_up(split_on, depdf):
    """
    Breaks off a depdf and forms its child. Recursively calls normalize on
    the original depdf, and its newly formed child.

    Arguments:
        split_on (list[str]) : attributes to split the dataframe on
        depdf (DepDF) : the depdf ot split
    """
    parent_deps, child_deps = split_on_dep(split_on, depdf.deps)
    child = DepDF(child_deps, form_child(depdf.df, child_deps), split_on, depdf)
    depdf.deps = parent_deps
    depdf.df = depdf.df.drop(columns=list(set(depdf.df.columns).difference(parent_deps.all_attrs())))
    depdf.children.append(child)
    normalize_dataframe(depdf)
    normalize_dataframe(child)


def form_child(df, deps):
    """
    Returns a new dataframe based off of the dependencies in deps.

    Arguments:
        df (pd.DataFrame) : dataframe to create new dataframe from
        deps (Dependencies) : dependencies to base new dataframe off of
    """
    attrs = deps.all_attrs()
    drops = set(df.columns).difference(attrs)
    new_df = df.drop(columns=list(drops))
    new_df = drop_primary_dups(new_df, deps.get_prim_key())
    return new_df


def remove_part_deps(dependencies, df):
    """
    Breaks up the dependency relations in dependencies into new groups of
    relations so that there are no more partial dependencies.

    Arguments:
        dependencies (Dependncies) : the dependencies to be split up

    Returns:
        new_groups (list[Dependencies]) : list of new dependencies objects
        representing the new groups with no partial depenencies
    """
    part_deps = dependencies.find_partial_deps()
    filter(part_deps, df)
    if part_deps == []:
        return [dependencies]
    new_deps = split_on_dep(find_most_comm(part_deps, dependencies), dependencies)
    return remove_part_deps(new_deps[0], df) + remove_part_deps(new_deps[1], df)


def remove_trans_deps(dependencies, df):
    """
    Breaks up the dependency relations in dependencies into new groups of
    relations so that there are no more transitive dependencies.

    Arguments:
        dependencies (Dependencies) : the dependencies to be split up

    Returns:
        new_groups (list[Dependencies]): list of new dependencies objects
        representing the new groups with no transitive depenencies
    """
    trans_deps = dependencies.find_trans_deps()
    filter(trans_deps, df)
    if trans_deps == []:
        return [dependencies]
    new_deps = split_on_dep(find_most_comm(trans_deps, dependencies), dependencies)
    return remove_trans_deps(new_deps[0], df) + remove_trans_deps(new_deps[1], df)


def find_most_comm(deps, dependencies, df=None):
    """
    Given a list of dependency relations, finds the most common set of
    LHS attributes. If more than one LHS set occurs the same amount of
    times, chooses the set with the least number of attributes.

    Arguments:
        deps (list[(set[str], str)]) : list of tuples representing relations
        where the lhs is a set of attribute names, and the rhs is an attribute.

    Returns:
        most_comm (set[str]) : the most common lhs set of attributes
    """
    positions = {}
    priority_lst = []

    for lhs, rhs in deps:
        if frozenset(lhs) in positions:
            ind = positions[frozenset(lhs)]
            score = priority_lst[ind][0] + 1
            while ind != 0 and priority_lst[ind - 1][0] < score:
                priority_lst[ind] = priority_lst[ind - 1]
                positions[frozenset(priority_lst[ind - 1][1])] = ind
                ind -= 1
            priority_lst[ind] = (score, lhs)
            positions[frozenset(lhs)] = ind
        else:
            priority_lst.append((1, lhs))
            positions[frozenset(lhs)] = len(priority_lst) - 1

    # IF THEY ARE THE SAME, CHOOSE ONE WITH SHORTEST LENGHT
    options = [item[1] for item in priority_lst if item[0] == priority_lst[0][0]]
    max_lhs = choose_index(options, df)

    # max_lhs = priority_lst[0][1]
    # scr = priority_lst[0][0]
    # i = 1
    # while i < len(priority_lst) and priority_lst[i][0] == scr:
    #     if len(priority_lst[i][1]) < len(max_lhs):
    #         max_lhs = priority_lst[i][1]
    #     i += 1

    for i in range(len(max_lhs)):
        for key in dependencies.get_prim_key():
            if dependencies.equiv_attrs(max_lhs[i], key):
                max_lhs[i] = key

    return max_lhs


def split_on_dep(lhs_dep, dependencies):
    """
    Given the LHS attributes of a dependency, breaks up the dependency
    relations in dependencies into two groups so that the LHS given is
    the primary key of the new group. The old group keeps the same
    primary key.

    Arguments:
        lhs_dep (list[str]) : set of attributes to be the new group's
        primary key
        dependencies (Dependencies) : dependency relations to be split up

    Returns:
        new_groups ((Dependencies, Dependencies)) : the new groups
    """
    new_deps = {}
    old_deps = dependencies.serialize()

    new_rhs = set()

    # new primary key
    for attr in lhs_dep:
        new_deps[attr] = old_deps[attr][:]

    for rhs in list(old_deps.keys()):
        for lhs in old_deps[rhs]:
            if set(lhs).issubset(lhs_dep):
                # if lhs_dep in old_deps[rhs]:
                new_deps[rhs] = old_deps[rhs]
                old_deps.pop(rhs)
                new_rhs.add(rhs)
                break

    for rhs in old_deps:
        for lhs in old_deps[rhs][:]:
            if len(new_rhs.intersection(lhs)) != 0:
                old_deps[rhs].remove(lhs)

    old_rhs = set(list(old_deps.keys()))
    for attr in lhs_dep:
        old_rhs.remove(attr)

    for rhs in new_deps:
        for lhs in new_deps[rhs][:]:
            if len(old_rhs.intersection(lhs)) != 0:
                new_deps[rhs].remove(lhs)

    return (Dependencies(old_deps, dependencies.get_prim_key()), Dependencies(new_deps, lhs_dep))


def drop_primary_dups(df, prim_key):
    """
    Drops all duplicates based off of the columns in prim_key. If there isn't a
    unique value for the other columns, for every unique instance of columns in
    prim_key, keeps the "mode" of the unique instances' occurance.

    Arguments:
        df (pd.DataFrame) : dataframe to drop duplicates of
        prim_key (list[str]) : columns that form the primary key of the dataframe

    Returns:
        new_df (pd.DataFrame) : dataframe with duplicates dropped
    """
    df_lst = []

    if df.drop_duplicates(prim_key).shape[0] == df.shape[0]:
        return df

    groups = df.groupby(prim_key)

    for name, group in groups:
        df_lst.append(group.mode().iloc[0])
        # new_df = new_df.append(group.mode().iloc[0], ignore_index=True)

    result = (pd.DataFrame(df_lst, columns=df.columns)).reset_index(drop=True)
    return result.astype(dict(df.dtypes))


def choose_index(keys, df):
    """
    Chooses key from a list of keys. Order of priority:
    1) shortest length
    2) has "id" in some form in name of an attribute
    3) has attribute furthest to the left in table

    Arguments:
        keys (list[set[str]]) : list of keys to choose from
        df (pd.DataFrame) : pandas dataframe keys are for

    Returns:
        index (list[str]) : chosen key
    """

    sort_key = sorted(keys, key=len)
    m = len(sort_key[0])
    options = [key for key in sort_key if len(key) == m]
    for key in options:
        for attr in key:
            if "_id" in attr.lower() or " id" in attr.lower() or "id _" in attr.lower() or "id " in attr.lower():
                return list(key)

    if df is None:
        return list(options[0])

    for col in df.columns:
        includes = [option for option in options if col in option]
        if len(includes) == 1:
            return list(includes[0])
        if len(includes) > 1:
            options = includes
    return list(options[0])


def filter(keys, df):
    """
    Filters out any keys that contain attributes that are not strings, ints, or
    categories from a list of relations.

    Arguments:
        keys (list[(list[str], str)]) : relationships to filter out
        df (pd.DataFrame) : dataframe attributes in keys are from
    """
    for key, rhs in keys[:]:
        for attr in key:
            if df[attr].dtypes.name not in set(['category', 'int64', 'object']):
                keys.remove((key, rhs))
                break
