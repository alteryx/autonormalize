import pandas as pd

from .classes import Dependencies

# def normalize(dependencies):
#     dependencies.prep()
#     part_deps = dependencies.find_partial_deps()
#     if part_deps != []:
#         new_grps = split_on_dep(find_most_comm(part_deps), dependencies)
#         return normalize(new_grps[0]) + normalize(new_grps[1])
#     trans_deps = dependencies.find_trans_deps()
#     if trans_deps != []:
#         new_grps = split_on_dep(find_most_comm(trans_deps), dependencies)
#         return normalize(new_grps[0]) + normalize(new_grps[1])
#     return [dependencies]

# SHOULD FINDING TRANSITIVE OR PARTIAL DEPS BE ONLY RELATED TO THE PRIM KEY?????


def normalize(dependencies):
    """
    Normalizes the dependency relationships in dependencies into new
    groups by breaking up all partial and transitive dependencies.

    Arguments:
    dependencies (Dependencies object): the dependencies to be split up

    Returns:
    new_groups (Dependencies list): list of new dependencies objects representing
    the new groups
    """
    dependencies.remove_implied_extroneous()
    no_part_deps = remove_part_deps(dependencies)
    no_trans_deps = []
    for grp in no_part_deps:
        no_trans_deps += remove_trans_deps(grp)
    return no_trans_deps


def remove_part_deps(dependencies):
    """
    Breaks up the dependency relations in dependencies into new groups of
    relations so that there are no more partial dependencies.

    Arguments:
    dependencies (Dependneies object): the dependencies to be split up

    Returns:
    new_groups (Dependencies list): list of new dependencies objects representing
    the new groups with no partial depenencies
    """
    part_deps = dependencies.find_partial_deps()
    if part_deps == []:
        return [dependencies]
    new_deps = split_on_dep(find_most_comm(part_deps), dependencies)
    return remove_part_deps(new_deps[0]) + remove_part_deps(new_deps[1])


def remove_trans_deps(dependencies):
    """
    Breaks up the dependency relations in dependencies into new groups of
    relations so that there are no more transitive dependencies.

    Arguments:
    dependencies (Dependneies object): the dependencies to be split up

    Returns:
    new_groups (Dependencies list): list of new dependencies objects representing
    the new groups with no transitive depenencies
    """
    trans_deps = dependencies.find_trans_deps()
    if trans_deps == []:
        return [dependencies]
    new_deps = split_on_dep(find_most_comm(trans_deps), dependencies)
    return remove_trans_deps(new_deps[0]) + remove_trans_deps(new_deps[1])


def find_most_comm(deps):
    """
    Given a list of dependency relations, finds the most common set of
    LHS attributes. If more than one LHS set occurs the same amount of
    times, chooses the set with the least number of attributes.

    Arguments:
    deps ((string Set*string) list): list of tuples representing relations
    where the lhs is a set of attribute names, and the rhs is an attribute.

    Returns:
    most_comm (string Set): the most common lhs set of attributes
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
    max_lhs = priority_lst[0][1]
    scr = priority_lst[0][0]
    i = 1
    while i < len(priority_lst) and priority_lst[i][0] == scr:
        if len(priority_lst[i][1]) < len(max_lhs):
            max_lhs = priority_lst[i][1]
        i += 1
    return max_lhs


def split_on_dep(lhs_dep, dependencies):
    """
    Given the LHS attributes of a dependency, breaks up the dependency
    relations in dependencies into two groups so that the LHS given is
    the primary key of the new group. The old group keeps the same
    primary key.

    Arguments:
    lhs_dep (string list): set of attributes to be the new group's
    primary key
    dependencies (Dependencies object): dependency relations to be
    split up

    Returns:
    new_groups (Dependencies object * Dependencies object): the new groups
    """
    new_deps = {}
    old_deps = dependencies.serialize()

    new_rhs = set()

    # new primary key
    for attr in lhs_dep:
        new_deps[attr] = old_deps[attr][:]

    for rhs in list(old_deps.keys()):
        if lhs_dep in old_deps[rhs]:
            new_deps[rhs] = old_deps[rhs]
            old_deps.pop(rhs)
            new_rhs.add(rhs)

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

    return (Dependencies.deserialize(old_deps), Dependencies.deserialize(new_deps))


def drop_primary_dups(df, deps):

    df_lst = []

    # new_df = pd.DataFrame(columns=df.columns)

    # find primary key
    # the ones with nothing pointing toward them?????
    prim_key = list(sorted(deps.find_candidate_keys(), key=len)[0])

    if df.drop_duplicates(prim_key).shape[0] == df.shape[0]:
        return df

    groups = df.groupby(prim_key)

    for name, group in groups:
        df_lst.append(group.mode().iloc[0])
        # new_df = new_df.append(group.mode().iloc[0], ignore_index=True)

    return (pd.DataFrame(df_lst, columns=df.columns)).reset_index(drop=True)
