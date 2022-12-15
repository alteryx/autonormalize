=============
API Reference
=============

Autonormalize
=====================

.. currentmodule:: autonormalize
.. autosummary::
   :toctree: generated/
   :nosignatures:

   find_dependencies
   normalize_dependencies
   normalize_dataframe
   make_entityset
   auto_entityset
   auto_normalize
   normalize_entityset

Dependencies
======================

.. currentmodule:: autonormalize.classes
.. autosummary::
   :toctree: generated/

   Dependencies
   Dependencies.set_prim_key
   Dependencies.get_prim_key
   Dependencies.add_dep
   Dependencies.remove_dep
   Dependencies.serialize
   Dependencies.deserialize
   Dependencies.from_rels
   Dependencies.all_attrs
   Dependencies.tuple_relations
   Dependencies.remove_implied_extroneous
   Dependencies.find_candidate_keys
   Dependencies.find_partial_deps
   Dependencies.find_trans_deps
   Dependencies.equiv_attrs
