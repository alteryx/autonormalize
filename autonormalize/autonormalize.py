import dfd
import normalize
from autonormalize.classes import Dependencies


def find_dependencies(df, accuracy=0.98, rep_percent=0.85):
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

    Returns:

    dependencies (Dependencies object): the dependencies found in the data
    within the contraints provided
    """
    return Dependencies(dfd.dfd(df, accuracy, rep_percent))


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


def split_dataframe(df, new_grps):
    """
    Splits up a dataframe dfb into new dataframes based off of dependency
    groups provided.

    Arguments:

    df (DataFrame): dataframe to split up

    new_grps (Dependencies list): list of groups of dependencies to base
    split off of

    Retunrs:

    new_dfs (DataFrame list): list of new dataframes
    """
    # this needs to accomodate for approximate dependencies....

    new_dfs = []

    for group in new_grps:

        all_attrs = group.all_attrs()
        new_df = df.copy()

        drops = set(new_df.columns).difference(all_attrs)
        new_df.drop(columns=list(drops), inplace=True)

        new_df = normalize.drop_primary_dups(new_df, group)

        new_dfs.append(new_df)

    return new_dfs


def normalize_dataframe(df, dependencies):
    """
    Normalizes a dataframe based on the dependencies given.

    Arguments:
    df (DataFrame): dataframe to split up
    dependencies (Dependencies object): the dependencies to be normalized

    Returns:
    new_dfs (DataFrame list): list of new dataframes
    """

    return split_dataframe(df, normalize_dependencies(dependencies))


def auto_normalize(df):
    """
    Normalizes dataframe via dependencies discovered in data.

    Arguments:
    df (DataFrame): dataframe to split up

    Returns:
    new_dfs (DataFrame list): list of new dataframes
    """
    return normalize_dataframe(df, find_dependencies(df))
