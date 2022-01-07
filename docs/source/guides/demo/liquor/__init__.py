from demo import PWD
from pandas import read_csv
from os.path import join

PWD = join(PWD, 'liquor')

def load_sample():
    df = read_csv(join(PWD, "Iowa_Liquor_Sales.csv"))
    # How to reproduce the sample from https://www.kaggle.com/residentmario/iowa-liquor-sales
    # df = df.drop(columns=df.columns[12:])
    # df = df.drop(range(1500000, 12591077))
    # df = df.dropna()
    # df = df.drop_duplicates()
    # df = df.head(1000)
    return df