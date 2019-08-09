from functools import partial
from itertools import combinations

import numpy
from tqdm import tqdm

from .classes import DfdDependencies, LHSs, Masks, Node

# see https://hpi.de/fileadmin/user_upload/fachgebiete/naumann/publications/2014/DFD_CIKM2014_p949_CRC.pdf for DFD paper
# run script.py  to see a couple examples


def dfd(df, accuracy, index=None):
    """
    Main loop of DFD algorithm. It returns all the dependencies represented
    in the data in dataframe df. Refer to section 3.2 of paper for literature.
    Checks each column to see if it's unique. If it is unique, it is added
    as the LHS of a dependency for every other element. It then loops through
    all the other non-unique columns and determines all the LHS that the
    column depends on. (LHS --> column)

    Arguments:

        df (pd.Dataframe) : the dataframe containing the data to find the
        dependencies from

        accuracy (0 < float <= 1.00) : the accuracy threshold required in order
        to conclude a dependency (i.e. with accuracy = 0.98, 0.98 of the rows
        must hold true the dependency LHS --> RHS)

    Returns:

        minimal_dependencies (DfdDependencies) : the minimal dependencies
        represented by the data in df
    """
    partitions = {}
    masks = Masks(df.columns)
    non_uniq = set(df.columns)
    unique_attrs = set()
    dependencies = DfdDependencies(df.columns)
    for i in non_uniq.copy():
        if df[i].is_unique or i == index:
            unique_attrs.add(i)
            non_uniq.remove(i)
            dependencies.add_unique_lhs(i)
    for i in tqdm(non_uniq):
        lhss = find_LHSs(i, non_uniq, df, partitions, accuracy, masks)
        dependencies.add_LHSs(i, lhss)
    return dependencies


def find_LHSs(rhs, attrs, df, partitions, accuracy, masks):
    """
    Finds all LHS sets of attributes that satisfy a dependency relation for the
    RHS attribute i. This is such that LHS --> RHS.

    Arguments:

        rhs (str) : name of column for which we are investigating dependencies
        for attrs (Set object containing strings): the columns to consider as
        LHS attributes

        df (Dataframe) : dataframe containing data to look at

        partitions (dict[frozenset[str] --> int]) : dictionary containing past
        calculated partition sizes for column combinations

        accuracy (0 < float <= 1.00) : the accuracy threshold required in order
        to conclude a dependency (i.e. with accuracy = 0.98, 0.98 of the rows must
        hold true the dependency LHS --> RHS)

        masks (Masks) : contains past calculated masks

    Returns:
        lhss (LHSs) : all the LHS that determine rhs
    """
    lhs_attrs = attrs.difference(set([rhs]))
    seeds = nodes_from_seeds(sorted(list(lhs_attrs)))
    min_deps = LHSs(lhs_attrs)
    max_non_deps = LHSs(lhs_attrs)
    trace = []
    while seeds != []:
        node = seeds[0]  # should this actually be random?
        while node is not None:

            if node.visited:
                if node.is_candidate():
                    if node.is_dependency():
                        if node.is_minimal():
                            min_deps.add_dep(node.attrs)
                    else:
                        if node.is_maximal():
                            max_non_deps.add_dep(node.attrs)
                    node.update_dependency_type(min_deps, max_non_deps)

            else:
                node.infer_type()
                if node.category == 0:
                    if compute_partitions(df, rhs, node.attrs, partitions, accuracy, masks):
                        if node.is_minimal():
                            min_deps.add_dep(node.attrs)
                            node.category = 2
                        else:
                            node.category = 3
                    else:
                        if node.is_maximal():
                            max_non_deps.add_dep(node.attrs)
                            node.category = -2
                        else:
                            node.category = -3
                node.visited = True

            node = pick_next_node(node, trace, min_deps, max_non_deps, df.columns)

        seeds = nodes_from_seeds(sorted(generate_next_seeds(max_non_deps, min_deps, lhs_attrs)))
    return min_deps


def nodes_from_seeds(seeds):
    """
    Returns nodes from a list of seeds. Creates nodes for each seed,
    and calls make_lattice which connexts them forming the rest of the
    lattice graph.

    Arguments:
        seeds (set[str]) : set of column names of seeds

    Returns:
        nodes (list[Node]) : list of base nodes for lattice graph
    """
    base_nodes = [Node(frozenset([attr])) for attr in seeds]
    make_lattice(base_nodes, seeds)
    return base_nodes


def make_lattice(nodes, attrs):
    """
    Builds the rest of the lattice graph given a list of nodes,
    creating nodes for all possible subsets of the nodes given,
    and connecting them to each other.

    Arguments:
        nodes (list[Node]) : list of nodes to connect upward from
        attrs (set[str]): set of column names present in the lattice
    """
    if len(nodes) < 2:
        return
    # TO DO: inefficient, but straight forward --> OPTIMIZE THIS
    this_level_size = len(nodes[0].attrs)
    next_level = []
    combos = combinations(attrs, this_level_size + 1)
    for new_attrs in combos:
        new_node = Node(frozenset(new_attrs))
        for n in nodes:
            if n.attrs.issubset(new_attrs):
                new_node.add_prev(n)
                n.add_next(new_node)
        next_level.append(new_node)
    make_lattice(next_level, attrs)
    # for i in range(len(nodes)-1):
    #     for j in range(i+1, len(nodes)):
    #         new_attrs = (nodes[i].attrs).union(nodes[j].attrs)
    #         prev = [nodes[i], nodes[j]]
    #         for n in nodes[j+1:]:
    #             if n.attrs.issubset(new_attrs):
    #                 prev.append(n)
    #         new_node = Node(new_attrs, prev, [])
    #         next_level.append(new_node)\


def sort_key(attrs, node):
    """
    Sort key for sorting lists of nodes.
    """
    acc = 0
    for i in range(len(attrs)):
        if attrs[i] in node.attrs:
            acc += 10**i
    return acc


def pick_next_node(node, trace, min_deps, max_non_deps, attrs):
    """
    Picks the next node to look at. If current node is a candidate minimum
    dependency looks for unchecked subsets. If no unchecked subsets that could
    be a dependency, current node must be a minimum dependency. Otherwise,
    check an unchecked subset.
    If current node is a candidate maximal dependnecy, look for unchecked
    supersets. If no unchecked supersets that could be a non-dependency,
    it must be a maximum non-dependency. Otherwise, check an unchecked superset.
    If not a candidate, return last node on trace (go back down in graph)

    Arguments:
        node (Node) : current node just visited
        trace (list[Node]) : stack of past nodes visited
        min_deps (LHSs) : discovered minimum dependencies
        max_non_deps (LHSs) : discovered maximum non-dependencies

    Returns:
        next_node (Node or None) : next node to look at, None if none left
        to check in currrent part of graph
    """
    srt_key = partial(sort_key, sorted(attrs))
    if node.category == 3:
        s = node.unchecked_subsets()
        remove_pruned_subsets(s, min_deps)
        if s == []:
            min_deps.add_dep(node.attrs)
            node.cateogry = 2
        else:
            trace.append(node)
            return sorted(s, key=srt_key)[0]
    elif node.category == -3:
        s = node.unchecked_supersets()
        remove_pruned_supersets(s, max_non_deps)
        if s == []:
            max_non_deps.add_dep(node.attrs)
            node.category = -2
        else:
            trace.append(node)
            return sorted(s, key=srt_key)[0]
    else:
        if trace == []:
            return None
        return trace.pop()


def remove_pruned_subsets(subsets, min_deps):
    """
    Removes all pruned subsets. A subset can be pruned when it is a
    subset of an existing discovered minimum dependency (because we
    thus know it is a non-dependency)

    Arguments:
        subsets (list[Node]) : list of subset nodes
        min_deps (LHSs) : discovered minimal dependencies
    """
    for n in subsets[:]:
        if min_deps.contains_superset(n.attrs):
            subsets.remove(n)


def remove_pruned_supersets(supersets, max_non_deps):
    """
    Removes all pruned supersets. A superset can be pruned when it is
    a superset of an existing discovered maximal non-dependency (because
    we thus know it is a dependency)

    Arguments:
        supersets (list[Node]) : list of superset nodes
        max_non_deps (LHSs) : discovered maximal non-dependencies
    """
    for n in supersets[:]:
        if max_non_deps.contains_subset(n.attrs):
            supersets.remove(n)


def generate_next_seeds(max_non_deps, min_deps, lhs_attrs):
    """
    Generates seeds for the nodes that are still unchecked due to pruning.
    This is done based off of the knowledge that once every possibility has
    been considered, the compliment of hte maximal non-dependencies, minus
    the existing minimum dependencies is 0 (the two are equal). Thus, if this
    is not satisfied, the new seeds are the remaining elements.

    Arguments:
        max_non_deps (LHSs) : discovered maximal non-dependencies
        min_deps (LHSs) : discovered minimal dependencies
        lhs_attrs (set[str]) : attributes being considered as parts of LHSs

    Returns:
        seed_attributes (list[str]) : list of seeds that need to be visited
    """
    seeds = set()
    if max_non_deps.all_sets() == set():
        seeds = lhs_attrs.difference(min_deps.all_sets().pop())
    else:
        for nfd in max_non_deps.all_sets():
            nfd_compliment = lhs_attrs.difference(nfd)
            if len(seeds) == 0:
                seeds = nfd_compliment
            else:
                seeds = seeds.intersection(nfd_compliment)
    for x in min_deps.all_sets():
        seeds = seeds.difference(x)
    return list(seeds)


def compute_partitions(df, rhs, lhs_set, partitions, accuracy, masks):
    """
    Returns true if lhs_set --> rhs for dataframe df.

    Arguments:

        df (pd.DataFrame) : dataframe containing data to look at

        rhs (str) : name of column for which we are investigating dependencies for
        attrs (Set object containing strings): the columns to consider as LHS attributes

        lhs_set (set[str]) : set containing column names of LHS set

        partitions (dict[frozenset[str] --> int]) : dictionary containing past
        calculated partition sizes for column combinations

        accuracy (0 < float <= 1.00) : the accuracy threshold required in order
        to conclude a dependency (i.e. with accuracy = 0.98, 0.98 of the rows must
        hold true the dependency LHS --> RHS)

        masks (Masks) : contains past calculated masks

    Returns:
        is_dependency (bool) : True if is a dependency, false otherwise
    """
    # for approximate dependencies see TANE section 2.3s
    if accuracy < 1:
        return approximate_dependencies(list(lhs_set), rhs, df, accuracy, masks)
    part_rhs = partition(lhs_set.union(set([rhs])), df, partitions)
    # if part_rhs > df.shape[0] * rep_percent:
    #     return False
    return part_rhs == partition(lhs_set, df, partitions)


def partition(attrs, df, partitions):
    """
    Returns the number of equivilence classes for the columns represented
    in attrs for dataframe df.
    """
    if attrs in partitions:
        return partitions[attrs]
    shape = df.drop_duplicates(attrs).shape[0]
    partitions[attrs] = shape
    return shape


def approximate_dependencies(lhs_set, rhs, df, accuracy, masks):
    """
    Checks whether the columns represented in lhs_set functionally determines the column rhs
    for the dataframe df.
    If lhs_set --> rhs, returns True. Otherwise returns False.

    *in order to be a dependency:
        - the number of equivalence classes for tuples in columns in lhs_set, is equal to the number of equivalence
        classes for tuples in columns in lhs_set+rhs
        - this holds in data for at least accuracy % of rows
        - at least 15% of values are repeating (*to be added as custom argument*)
    """
    df_lhs_rhs = df.drop_duplicates(lhs_set + [rhs])
    df_lhs = df_lhs_rhs.drop_duplicates(lhs_set)
    # if df_lhs.shape[0] > df.shape[0] * rep_percent:
    #     return False

    limit = df.shape[0] * (1 - accuracy)
    if df_lhs_rhs.shape[0] - df_lhs.shape[0] > limit:
        return False

    merged = df_lhs.merge(df_lhs_rhs, indicator=True, how='outer')  # create new df that is the merge of df_one and df_two
    indicator = merged[merged['_merge'] == 'right_only']  # filter out the rows that were only on the right side (the rows that are preventing the two dataframes from being equal)
    indicator = indicator.drop_duplicates(lhs_set)  # find unique combinations of columns in LHS_set that characterize the disrepencies (have 2+ different values in rhs column)
    acc = 0

    for index, row in indicator.iterrows():

        mask = None
        for attr in lhs_set:

            m = masks.get_mask(attr, row[attr])
            if m is None:
                if df[attr].dtypes.name == 'datetime64[ns]':
                    m = df[attr] == row[attr]
                else:
                    m = df[attr].values == row[attr]
                masks.add_mask(attr, row[attr], m)
            if mask is None:
                mask = m
            else:
                mask = mask & m
        options = df[mask]
        _, unique_counts = numpy.unique(options[rhs].to_numpy(), return_counts=True)
        acc += unique_counts.sum() - unique_counts.max()
        if acc > limit:
            return False
    # idea: try using numpy arrays and taking intersections of sets for each column????
    return True
