import os

import pandas as pd

liquor_df = pd.read_csv(os.path.join(os.getcwd(), 'autonormalize/downloads/liquor.csv'))
liquor_df = liquor_df.drop(columns=liquor_df.columns[12:])
liquor_df = liquor_df.drop(range(3000000, 12591077))
liquor_df = liquor_df.dropna()
liquor_df = liquor_df.drop_duplicates()
