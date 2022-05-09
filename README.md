# AutoNormalize

![Tests](https://github.com/FeatureLabs/autonormalize/workflows/Tests/badge.svg)

AutoNormalize is a Python library for automated datatable normalization. It allows you to build an `EntitySet` from a single denormalized table and generate features for machine learning using [Featuretools](https://github.com/FeatureLabs/featuretools).

<img src=https://github.com/FeatureLabs/autonormalize/blob/main/gif.gif>

## Getting Started

- [Install](#install)
- [Demos](#demos)
- [API Reference](#api-reference)

## Install

```shell
pip install featuretools[autonormalize]
```

#### Uninstall

```shell
pip uninstall autonormalize
```

## Demos

- [Blog Post](https://blog.featurelabs.com/automatic-dataset-normalization-for-feature-engineering-in-python/)
- [Machine Learning Demo with Featuretools](https://github.com/FeatureLabs/autonormalize/blob/master/autonormalize/demos/AutoNormalize%20%2B%20FeatureTools%20Demo.ipynb)
- [Kaggle Liquor Sales Dataset Demo](https://github.com/FeatureLabs/autonormalize/blob/master/autonormalize/demos/Kaggle%20Liquor%20Sales%20Dataset%20Demo.ipynb)
- [Demo with Editing Dependencies](https://github.com/FeatureLabs/autonormalize/blob/master/autonormalize/demos/Editing%20Dependnecies%20Demo.ipynb)
- [Kaggle Food Production Dataset Demo](https://github.com/FeatureLabs/autonormalize/blob/master/autonormalize/demos/Kaggle%20Food%20%20Dataset%20Demo.ipynb)

## API Reference

### `auto_entityset`

```shell
auto_entityset(df, accuracy=0.98, index=None, name=None, time_index=None)
```

Creates a normalized entityset from a dataframe.

**Arguments:**

- `df` (pd.Dataframe) : the dataframe containing data

- `accuracy` (0 < float <= 1.00; default = 0.98) : the accuracy threshold required in order to conclude a dependency (i.e. with accuracy = 0.98, 0.98 of the rows must hold true the dependency LHS --> RHS)

- `index` (str, optional) : name of column that is intended index of df

- `name` (str, optional) : the name of created EntitySet

- `time_index` (str, optional) : name of time column in the dataframe.

**Returns:**

- `entityset` (ft.EntitySet) : created entity set

### `find_dependencies`

```shell
find_dependencies(df, accuracy=0.98, index=None)
```

Finds dependencies within dataframe with the DFD search algorithm.

**Returns:**

- `dependencies` (Dependencies) : the dependencies found in the data within the contraints provided

### `normalize_dataframe`

```shell
normalize_dataframe(df, dependencies)
```

Normalizes dataframe based on the dependencies given. Keys for the newly created DataFrames can only be columns that are strings, ints, or categories. Keys are chosen according to the priority:

1. shortest lenghts
2. has "id" in some form in the name of an attribute
3. has attribute furthest to left in the table

**Returns:**

- `new_dfs` (list[pd.DataFrame]) : list of new dataframes

<br />

### `make_entityset`

```shell
make_entityset(df, dependencies, name=None, time_index=None)
```

Creates a normalized EntitySet from dataframe based on the dependencies given. Keys are chosen in the same fashion as for `normalize_dataframe`and a new index will be created if any key has more than a single attribute.

**Returns:**

- `entityset` (ft.EntitySet) : created EntitySet

<br />

### `normalize_entityset`

```shell
normalize_entityset(es, accuracy=0.98)
```

Returns a new normalized `EntitySet` from an `EntitySet` with a single entity.

**Arguments:**

- `es` (ft.EntitySet) : EntitySet with a single entity to normalize

**Returns:**

- `new_es` (ft.EntitySet) : new normalized EntitySet

<br />

## Built at Alteryx Innovation Labs

<a href="https://www.alteryx.com/innovation-labs">
    <img src="https://evalml-web-images.s3.amazonaws.com/alteryx_innovation_labs.png" alt="Alteryx Innovation Labs" />
</a>
