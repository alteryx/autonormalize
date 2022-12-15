from demo import PWD
from pandas import read_csv
from os.path import join

PWD = join(PWD, "food")


def load_sample():
    food_df = read_csv(join(PWD, "FAO.csv"), encoding="latin1")
    food_df = food_df.drop(columns=food_df.columns[10:])
    return food_df
