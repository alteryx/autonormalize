import os

import pandas as pd

import user_interaction
from classes import Dependencies

deps_dic = {
    'Unnamed: 0': [],
    'State Code': [['State'], ['Site Num', 'City'], ['County'],
                   ['Site Num', 'County Code'], ['Address'], ['City', 'County Code']],
    'County Code': [['Site Num', 'City'], ['County'], ['Address'], ['City', 'State Code'],
                    ['City', 'State']],
    'Site Num': [['Address']],
    'Address': [['Site Num', 'County Code'], ['Site Num', 'City'], ['Site Num', 'County']],
    'State': [['Site Num', 'City'], ['County'], ['Site Num', 'County Code'],
              ['Address'], ['City', 'County Code'], ['State Code']],
    'County': [['Site Num', 'City'], ['State', 'County Code'], ['Address'],
               ['Site Num', 'County Code'], ['City', 'County Code'],
               ['City', 'State Code'], ['City', 'State'], ['State Code', 'County Code']],
    'City': [['Site Num', 'County Code'], ['Address'], ['Site Num', 'County']]
}

pollution_df = pd.read_csv(os.path.join(os.getcwd(), 'downloads/pollution.csv'))
pollution_df = pollution_df.drop(columns=pollution_df.columns[9:])
pollution_df_small = pollution_df.drop(range(200000, 1746661))
pollution_df_small = pollution_df_small.drop(columns=['Date Local'])
pollution_df_small = pollution_df_small.drop_duplicates()

deps = Dependencies(deps_dic)

grps = user_interaction.normalize_dependencies(deps)

new_dfs = user_interaction.split_dataframe(pollution_df_small, grps)
