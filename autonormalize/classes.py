import copy
from itertools import combinations


class LHSs(object):
    """
    Efficiently stores the Left-Hand-Sides for dependency relations for a
    single Right-Hand-Side.

    Attributes:
        _dic
        _attrs
    """

    def __init__(self, attrs):
        """
        Creates a LHSs.

        Args:
            attrs (list[str]) : list of names of attributes that will be in LHSs
        """
        self._dic = {}
        self._attrs = attrs
        for at in attrs:
            self._dic[at] = set()

    def add_dep(self, attr_set):
        """
        Adds attr_set as a LHS.

        Args:
            attr_set (frozenset[str]) : the set of attributes in the LHS to add
        """
        for attr in attr_set:
            self._dic[attr].add(attr_set)

    def all_sets(self):
        """
        Returns all LHSs stored in self.

        Returns:
            all_sets (set[frozenset]) : all the LHS sets.
        """
        result = set()
        for attr in self._attrs:
            for lhs in self._dic[attr]:
                result.add(lhs)
        return result

    def contains_subset(self, attr_set):
        """
        Returns True if self contains a subset of attr_set, False otherwise.

        Args:
            attr_set (set[str]) : set of attributes to look for subset of

        Returns:
            contains_subset (bool) : whether self contains subset of attr_set
        """
        for x in attr_set:
            for lhs in self._dic[x]:
                if lhs.issubset(attr_set):
                    return True
        return False

    def contains_superset(self, attr_set):
        """
        Returns True if self. contains a superset of attr_set, False otherwise.

        Args:
            attr_set (set[str]) : set of attributes to look for superset of

        Returns:
            contains_superset (bool) : whether self contains a superset of
            attr_set
        """
        for x in attr_set:
            for lhs in self._dic[x]:
                if attr_set.issubset(lhs):
                    return True
        return False


class DfdDependencies(object):
    """
    Maps each RHS to a set of LHSs.

    Attributes:
        _dic
    """

    def __init__(self, attrs):
        """
        Creates an empty DfdDependencies.

        Args:
            attrs (list[str]) : all the attributes in the dataset investigating
        """
        self._dic = {}
        for rhs in attrs:
            self._dic[rhs] = set()

    def add_unique_lhs(self, lhs_attr):
        """
        Adds lhs_attr as the lhs for every other attribute in set.

        Args:
            lhs_attr (str) : the unique attribute to add
        """
        for attr in self._dic:
            if lhs_attr != attr:
                self._dic[attr].add(frozenset([lhs_attr]))

    def add_LHSs(self, rhs, lhss):
        """
        Adds all the lhs sets in lhss for rhs.

        Args:
            rhs (str) : attribute to add lhss for
            lhss (LHSs) : lhss to add
        """
        for lhs in lhss.all_sets():
            self._dic[rhs].add(lhs)

    def serialize(self):
        ser = self._dic.copy()
        for rhs in ser:
            ser[rhs] = [list(lhs) for lhs in ser[rhs]]
        return ser


class Node(object):
    """
    Represents a node in the lattice graph of the DFD algorithmic functional
    dependency search.

    Attributes:
        attrs (frozenset[str]) : attributes in the node

        visited (bool) : True if the node has been visited, False otherwise

        cateogry (-3 <= int <= 3) : representing the classified category of the node
            0 = Unclassified
            1 = Dependency
            2 = Minimal Dependnecy
            3 = Candidate Minimal Dependency
            -1 = Non-dependency
            -2 = Maximal Non-dependency
            -3 = Candidate Maximal Non-dependency

        prev (set[Node]) : child nodes (subsets with one less element)

        next (set[Node]) : parent nodes (supersets with one more element)
    """

    def __init__(self, attr_set):
        """
        Creates a node.

        Args:
            attr_set (set[str]) : attributes that the node represents
        """
        assert attr_set is not None
        self.attrs = attr_set
        self.visited = False
        self.category = 0
        self.prev = set()
        self.next = set()

    def add_prev(self, prev):
        """
        Adds node prev to previous nodes.

        Args:
            prev (Node) : previous node
        """
        self.prev.add(prev)

    def add_next(self, next):
        """
        Adds node next to next nodes.

        Args:
            next (Node) : next node
        """
        self.next.add(next)

    def is_candidate(self):
        """
        Returns True if self is a candidate for dependency or non-dependency.
        False otherwise.

        Returns:
            is_candiate (bool) : whether self is a candidate
        """
        return abs(self.category) == 3

    def is_dependency(self):
        """
        Returns True if self is a dependency. False otherwise.

        Returns:
            is_dependency (bool) : whether self is a dependency
        """
        return self.category > 0

    def is_minimal(self):
        """
        Returns True if self is minimal. Node is minimal if all subsets in
        self.prev are classified as non-dependencies. If self is minimal,
        updates the self.category to minimal dependency.

        Returns:
            is_minimal (bool) : if self is minmal
        """
        for x in self.prev:
            if x.category >= 0:
                return False
        self.category = 2
        return True

    def is_maximal(self):
        """
        Returns True if self is maximal. Node is maximal if all supersets in
        self.next are classified as dependencies. If self is maximal, updates
        the self.catigory to maximal dependency.

        Returns:
            is_maximal (bool) : if self is maximal
        """
        for x in self.next:
            if x.category <= 0:
                return False
        self.category = -2
        return True

    def update_dependency_type(self, min_deps, max_non_deps):
        """
        Attempts to update node's category based off of the sets in min_deps
        and the sets in max_non_deps. If self.attrs are a subset of a set in
        max_non_deps, sets category to non-dependency. If self.attrs are a
        superset of a set in min_deps, sets category to dependency.

        Args:
            min_deps (LHSs) : the minimal dependencies discovered so far
            max_non_deps (LHSs) : the maximal dependencies discovered so far
        """
        if min_deps.contains_subset(self.attrs):
            self.category = 1
        if max_non_deps.contains_superset(self.attrs):
            self.category = -1

    def unchecked_subsets(self):
        """
        Returns all subset nodes with one less element that haven't been
        visited.

        Returns:
            unchecked_subsets (list[Node]) : unchecked subsets
        """
        return [x for x in self.prev if not x.visited]

    def unchecked_supersets(self):
        """
        Returns all superset nodes with one more element that hven't been
        visited.

        Returns:
            unchecked_supersets (list[Node]) : unchecked supersets
        """
        return [x for x in self.next if not x.visited]

    def infer_type(self):
        """
        Attempts to infer the category of self by checking if any subsets are a
        dependency, or if any supersets are a non-dependency.
        """
        # TO DO: optimize, this is inefficient (or it's helper functions are)
        if self._dep_subset():
            self.category = 1
        if self._non_dep_superset():
            self.category = -1

    def _dep_subset(self):
        stack = self.prev.copy()
        while len(stack) != 0:
            n = stack.pop()
            if n.category > 0:
                return True
            for x in n.prev:
                stack.add(x)
        return False

    def _non_dep_superset(self):
        stack = self.next.copy()
        while len(stack) != 0:
            n = stack.pop()
            if n.category < 0:
                return True
            for x in n.next:
                stack.add(x)
        return False

    def __hash__(self):
        return id(self)

    def __str__(self):
        return str({"attributes": str(self.attrs), "visited": self.visited,
                    "category": self.category, "prev": self.prev, "next": self.next, "loc": id(self)})


class Dependencies(object):
    """
    Represents the functional dependencies between a set of attributes.

    Attributes:
        _data
        _primkey
    """

    def __init__(self, dependencies, prim_key=None):
        """
        Creates a Dependencies from either a DfdDependencies object, or from a
        dictionary representing dependency relations.

        Args:
            dependencies (DfdDependencies or dict[str --> list[list[str]]]) :
            dependency relations to be represented
            prim_key (list[str], optional) : the primary key of the dependencies
        """
        assert prim_key is None or isinstance(prim_key, list)
        if isinstance(dependencies, dict):
            self._data = dependencies
        else:
            self._data = dependencies.serialize()
        self._primkey = prim_key

    def set_prim_key(self, prim_key):
        """
        Sets primary key to prim_key.

        Args:
            prim_key (list[str]) : primary key to set
        """
        assert prim_key is None or isinstance(prim_key, list)
        self._primkey = prim_key

    def get_prim_key(self):
        """
        Gets primary key.

        Returns:
            prim_key (list[str]) : the primary key
        """
        return self._primkey

    def add_dep(self, rhs, lhs):
        """
        Adds the dependency lhs --> rhs.

        Arguments:
            lhs (list[str]) : the attributes on the left hand side of dependency
            rhs (str) : the attribute on the right hand side
        """
        assert rhs in self._data
        self._data[rhs].append(lhs)

    def remove_dep(self, rhs, lhs):
        """
        Removes the dependency lhs --> rhs. Requires that this dependency exists.

        Arguments:
            lhs (list[str]) : the attributes on the left hand side of dependency
            rhs (str) : the attribute on the right hand side
        """
        assert rhs in self._data
        self._data[rhs].remove(lhs)

    def serialize(self):
        return copy.deepcopy(self._data)

    @classmethod
    def deserialize(cls, dic):
        return cls(dic)

    @classmethod
    def from_rels(cls, rels):
        """
        Returns a Dependencies from a list of relations.

        Arguments:
            rels (list[(list[str], str)]) : relations to create dependencies from

        Returns:
            dependencies (Dependencies) : created Dependencies object
        """
        dic = {}
        all_attrs_l = set()
        for lhs, rhs in rels:
            if rhs in dic:
                dic[rhs].append(lhs)
            else:
                dic[rhs] = [lhs]
            all_attrs_l.update(lhs)
        for attr in all_attrs_l:
            if attr not in dic:
                dic[attr] = []
        return cls(dic)

    def __str__(self):
        """
        For printing, visually displays dependency relations.
        """
        result = []
        for rhs in self._data:
            lhs_str = ""
            for lhs in self._data[rhs]:
                lhs_str = lhs_str + " {" + ",".join(lhs) + "} "
            lhs_str = lhs_str + " --> " + rhs
            result.append(lhs_str)
        return "\n".join(result)

    def __eq__(self, dep_2):
        """
        For object comparison.
        """
        return self._data == dep_2._data

    def all_attrs(self):
        """
        Returns all the attributes in self.

        Returns:
            all_attrs (set[str]) : all attributes
        """
        return set(self._data.keys())

    def tuple_relations(self):
        """
        Returns the relationships stored in self as a list.

        Returns:
            relations (list[(list[str], str)]) : relations stored in self
        """
        result = []
        for rhs in self._data:
            result = result + [(lhs, rhs) for lhs in self._data[rhs]]
        return result

    def remove_implied_extroneous(self):
        """
        Removes all implied extroneous attributes from relations in self.

        Example:
            A --> B
            AB --> C
            becomes
            A --> B
            A --> C
        """
        rels = self.tuple_relations()
        for lhs, rhs in rels[:]:
            y = lhs[:]
            for attr in lhs:
                y_ = y[:]
                y_.remove(attr)
                if rhs in find_closure(rels, y_):
                    y.remove(attr)
            rels.remove((lhs, rhs))
            rels.append((y, rhs))
            self._data[rhs].remove(lhs)
            self._data[rhs].append(y)

        # remove dups
        for rhs in self._data:

            i = 0
            while i < len(self._data[rhs]):
                if self._data[rhs][i] in self._data[rhs][i + 1:]:
                    self._data[rhs].pop(i)
                else:
                    i += 1

    def find_candidate_keys(self):
        """
        Returns all candidate keys in self. A candidate key is a minimal
        set of attributes whose closure is all attributes in the table.

        Returns:
            cand_keys (list[set[str]]) : list of candidate keys for self
        """

        rhs_attrs = set([rhs for rhs in self._data if len(self._data[rhs]) > 0])
        lhs_attrs = set()
        for rhs in self._data:
            for lhs in self._data[rhs]:
                lhs_attrs.update(set(lhs))

        lhs_only = lhs_attrs.difference(rhs_attrs)
        all_attrs = set(self._data.keys())
        rhs_only = rhs_attrs.difference(lhs_attrs)
        lhs_and_lhs = all_attrs.difference(lhs_only.union(rhs_only))
        rels = self.tuple_relations()

        if find_closure(rels, list(lhs_only)) == all_attrs:
            return [lhs_only]

        cand_keys = []

        for l in range(1, len(lhs_and_lhs) + 1):
            combos = combinations(lhs_and_lhs, l)
            for comb in combos:
                if find_closure(rels, list(lhs_only.union(comb))) == all_attrs:
                    cand_keys.append(lhs_only.union(comb))

        for x in cand_keys[:]:
            for y in cand_keys[:]:
                if x.issuperset(y) and x is not y:
                    cand_keys.remove(x)
                    break
        return cand_keys

    # def find_candidate_keys(self):
    #     """
    #     Returns all candidate keys as a list of sets of attributes.
    #     A candidate key is a minimal set of attributes whose closure is
    #     all attributes in the table.

    #     Returns:
    #     candidate_keys (string set list): candidate keys found

    #     example:
    #         TO DO
    #     """
    #     rhs_attrs = set([rhs for rhs in self._data if len(self._data[rhs]) > 0])
    #     lhs_attrs = set()
    #     for rhs in self._data:
    #         for lhs in self._data[rhs]:
    #             lhs_attrs.update(set(lhs))

    #     lhs_only = lhs_attrs.difference(rhs_attrs)
    #     all_attrs = set(self._data.keys())
    #     rhs_only = rhs_attrs.difference(lhs_attrs)
    #     lhs_and_lhs = all_attrs.difference(lhs_only.union(rhs_only))
    #     rels = self.tuple_relations()

    #     if find_closure(rels, list(lhs_only)) == all_attrs:
    #         return [lhs_only]

    #     def helper(base, options, all_attrs):
    #         print(base)
    #         if len(options) == 0:
    #             return [base]
    #         if base == all_attrs:
    #             return [base]
    #         result = []
    #         for x in options:
    #             combo = base.union(set([x]))
    #             if find_closure(rels, list(combo)) == all_attrs:
    #                 result.append(combo)
    #             else:
    #                 result = result + helper(combo, options.difference(set([x])), all_attrs)
    #         return result

    #     cand_keys = helper(lhs_only, lhs_and_lhs, all_attrs)

    #     for x in cand_keys[:]:
    #         for y in cand_keys[:]:
    #             if x.issuperset(y) and x is not y:
    #                 cand_keys.remove(x)
    #                 break
    #     return cand_keys

    def find_partial_deps(self):
        """
        Finds all partial dependencies within self.

        Returns:
            partial_deps (list[(list[str], str)]) : partial dependencies

        Example:
            A --> B
            C --> D
            DF --> E
            G --> F
            finds:
            A --> B
            C --> D
            G --> F
        """
        partial_deps = []
        cand_keys = [self.get_prim_key()]
        # cand_keys = self.find_candidate_keys()
        key_attrs = set()
        for key in cand_keys:
            key_attrs.update(key)
        rels = self.tuple_relations()
        for lhs, rhs in rels:
            if rhs not in key_attrs:
                for key in cand_keys:
                    if set(lhs).issubset(key) and len(lhs) < len(key):
                        partial_deps.append((lhs, rhs))
                        break
        return partial_deps

    def find_trans_deps(self):
        """
        Finds all transitive dependencies within self.

        Returns:
            trans_deps (list[(list[str], str)]) : transitive dependencies

        Example:
            A --> B
            C --> D
            DF --> E
            G --> F
            finds:
            DF --> E
        """
        trans_deps = []
        cand_keys = [self.get_prim_key()]
        # cand_keys = self.find_candidate_keys()
        key_attrs = set()
        for key in cand_keys:
            key_attrs.update(key)
        all_attrs = set(self._data.keys())
        rels = self.tuple_relations()

        for lhs, rhs in rels:
            if rhs not in key_attrs:
                if find_closure(rels, lhs) != all_attrs:
                    acc = False
                    for key in cand_keys:
                        if set(lhs).issubset(key):
                            acc = True
                            break
                    if not acc:
                        trans_deps.append((lhs, rhs))
        return trans_deps

    def equiv_attrs(self, one, two):
        """
        Returns True if one and two are equivalent attributes, or in another
        words have equivalent closures.

        Returns:
            is_equiv (bool) : True if equivalent, False otherwise
        """
        tups = self.tuple_relations()
        return find_closure(tups, [one]) == find_closure(tups, [two])


def find_closure(rel, attrs):
    """
    Finds the closure of attrs under the relations in rel.

    Arguments:
        rel (list[(list[str], str)]) : relationships to find closure under
        attrs (list[str]) : attributes to find the closure of

    Returns:
        closure (set[str]) : attrs' closure, aka the attributes that can be
        determined from the attributes in attrs
    """
    def helper(set_attr, rel):
        if rel == []:
            return set(set_attr)
        for dep_attrs, dep in rel:
            if set(dep_attrs).issubset(set_attr):
                rel_ = rel[:]
                rel_.remove((dep_attrs, dep))
                return helper(set_attr + [dep], rel_)
        return set_attr
    return set(helper(attrs[:], rel))


class Masks(object):
    """
    Stores the created masks of a dataframe.

    Attributes:
        _masks
    """

    def __init__(self, columns):
        """
        Creates a new Masks.

        Arguments:
            columns (list[str]) : the columns of the dataframe the masks are for
        """
        self._masks = {}
        for col in columns:
            self._masks[col] = {}

    def add_mask(self, col, val, mask):
        """
        Adds mask for column col and value val.

        Arguments:
            col (str) : name of column mask is for
            val (_) : value for that column mask is for
            mask (pandas.core.series.Series or numpy.ndarray) : mask for df[col] == val
        """
        self._masks[col][val] = mask

    def get_mask(self, col, val):
        """
        Gets mask for column col and value val.

        Arguments:
            col (str) : name of column mask is for
            val (_) : value for that column mask is for

        Returns:
            mask (pandas.core.series.Series or numpy.ndarray) : mask for df[col] == val
        """
        if val in self._masks[col]:
            return self._masks[col][val]
        return None

# class BitIndexSet(object):
#     """
#     A BitIndexSet represents a set where each of the elements are an integer.
#     The size of the set is the greatest element possible for the given situation.
#     """

#     def __init__(self, size, attr_set=set()):
#         self._data = 0
#         self._size = size
#         for attr in attr_set:
#             self._data += 1 << (attr)

#     def _get_bit(self, i):
#         return (self._data >> i) % 2

#     def _remove_bit(self, i):
#         if self._get_bit(i) == 0:
#             return
#         self._data -= 1 << i

#     def _add_bit(self, i):
#         if self._get_bit(i) == 1:
#             return
#         self._data += 1 << i

#     def get_size(self):
#         return self._size

#     def to_set(self):
#         """ Returns self as a Set object"""
#         bits = self._data
#         new_set = set()
#         for i in range(self._size):
#             if bits % 2 == 1:
#                 new_set.add(i)
#             bits = bits >> 1
#         return new_set

#     def is_subset(self, set2):
#         """ True if self is a subset of set2"""
#         for i in range(self._size):
#             if self._get_bit(i) == 1 and set2._get_bit(i) != 1:
#                 return False
#         return True

#     def is_superset(self, set2):
#         """ True if self is a superset of set2"""
#         for i in range(self._size):
#             if set2._get_bit(i) == 1 and self._get_bit(i) != 1:
#                 return False
#         return True

#     def get_compliment(self, rhs):
#         """
#         Returns the compliment of the current set, except for the
#         rhs which remains 0 (not in the set)
#         """
#         new_set = BitIndexSet(self._size)
#         for i in range(self._size):
#             if self._get_bit(i) == 0 and i != rhs:
#                 new_set._data += 1 << i
#         return new_set

#     def difference(self, set2):
#         """Removes all elements in set2, from self (if exists in self)"""
#         for i in range(set2._size):
#             if set2._get_bit(i) == 1:
#                 self._remove_bit(i)

#     def add_new(self, attrs):
#         """ Returns new set that contains all attributes of self, and all
#         in attrs--a Set() object"""
#         at = self.to_set()
#         return BitIndexSet(self._size, at.union(attrs))

#     def __eq__(self, set2):
#         if not isinstance(set2, BitIndexSet):
#             return False
#         return self._data == set2._data

#     def __hash__(self):
#         return hash(self._data)

#     def __iter__(self):
#         return iter(self.to_set())

#     def __str__(self):
#         return str(self.to_set())

#     def __len__(self):
#         return len(self.to_set())
