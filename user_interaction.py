import dfd
from classes import Dependencies
import normalize


def find_dependencies(df, accuracy=0.98, rep_percent=0.85):
    """
    Finds dependencies within dataframe df with DFD search algorithm.
    Returns the dependencies as a Dependencies object.

    optional arguments to add:
        - approximated accuracy of table
        - known dependencies
        - threshold for repeating data?
    """
    return Dependencies(dfd.dfd(df, accuracy, rep_percent))


def normalization(df, dependencies):
    """
    Breaks up dataframe df into new normalized dataframes based on the
    dependency relations represented in dependencies.
    Returns a list of the new dataframes.
    """
    new_groups = normalize.normalize(dependencies)
    new_dfs = []
    for group in new_groups:
        all_attrs = group.all_attrs()
        new_df = df.copy()
        drops = set(new_df.columns).difference(all_attrs)
        new_df.drop(columns=list(drops), inplace=True)
        new_df.drop_duplicates(inplace=True)
        new_dfs.append(new_df)
    return new_dfs


def auto_normalize(df):
    """
    Finds dependencies and then normalizes. Direct pipeline from
    find_dependencies(df) to normalization(df, dependencies)
    """
    return normalization(df, find_dependencies(df))
