# Autonormalize

Imports:

```
import pandas as pd
import autonormalize
```

## Using:
Some input and interaction:

```
df = pd.read_csv('/path/to/datafile/data.csv')

dependencies = autonormalize.find_dependencies(df, provided_dependencies={})

dependencies.remove_dep('name', ['mother', 'age'])

dependencies.add_dep('length', ['weight'])

normalized_dfs = autonormalize.normalize(df, dependencies)
```
Completely automated option:

```
df = pd.read_csv('/path/to/datafile/data.csv')

normalized_dfs = autonormalize.auto_normalize(df)
```

### Interacting with Dependencies:

```
dependencies = Dependencies.deserialize({
	"name": [['id']], 
	"age": [['birth_day'], ['id']], 
	"birth_day": [['id']], 
	"id": [['name', 'birth_day']]
	})
	
#edit dependencies as dependencies object:
dependences.add_dep('name', ['birth_day'])
	
dependencies_dic = dependencies.serialize()

print(dependencies_dic)

#directly edit dependencies as dictionary:
dependencies_dic["name"].remove(['birth_day'])

```
output:

```
{"name": [['id'], ['birth_day'], 
"age": [['birth_day'],  ['id']], 
"birth_day": [['id']], 
"id": [['name', 'birth_day']]}
```



Ideas/Situations...

* circular dependencies
* discrete values shouldn't be primary keys
