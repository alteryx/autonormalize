import os
import time

import pandas as pd

import dfd
import user_interaction

path = os.getcwd()

df = pd.read_csv(os.path.join(path, 'example_3'))

df_3 = pd.read_csv(os.path.join(path, 'example_4'))

df_acc = pd.read_csv(os.path.join(path, 'accredation.csv'))

df_acc = df_acc.drop(columns=df_acc.columns[10:])


dic_2 = {
    "id": [100, 101, 102, 103, 104, 105, 106, 107, 109],
    "age": [1, 2, 3, 4, 5, 6, 7, 5, 6],
    "height": [4, 5, 6, 7, 8, 9, 10, 8, 9],
    "less_than_5": [1, 1, 1, 1, 0, 0, 0, 0, 0]
}

dic_1 = {
    "id": [100, 101, 102, 103, 104, 105, 106, 107, 109],
    "age": [1, 2, 3, 4, 5, 6, 7, 5, 6],
    "height": [4, 5, 6, 7, 8, 9, 10, 8, 9]
}


df_1 = pd.DataFrame(dic_1)
df_2 = pd.DataFrame(dic_2)


def print_example(str_interp, df, dim=None):
    print("\n\n")
    print("dependencies for: \n" + str_interp)
    if dim is not None:
        print(str(dim[0]) + " rows and " + str(dim[1]) + " columns\n")
    print("\n")
    start_time = time.time()
    dep = dfd.dfd(df)
    end_time = time.time()
    print(dep.serialize())
    print("\nexecution time: " + str(end_time - start_time))
    print("\n\n")


print_example(str(dic_1), df_1)
print_example(str(dic_2), df_2)
print_example("A = index,   B = random,   C = random,   D = random,   " +
              "E = c != 1,   F = b < 10,   G = c + d", df, (100000, 7))

# print_example("see gen file", df_3, (400000, 12))

# print_example("see gen file", df_4, (400000, 14))

print(df_acc)

deps = user_interaction.find_dependencies(df_acc)

new_dfs = user_interaction.normalization(df_acc, deps)

print(deps)

for df in new_dfs:
    print(df)
