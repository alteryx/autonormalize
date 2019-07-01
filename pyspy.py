import os
import user_interaction
import pandas as pd


pollution_df = pd.read_csv(os.path.join(os.getcwd(), 'pollution.csv'))
pollution_df = pollution_df.drop(columns=pollution_df.columns[9:])
pollution_df_small = pollution_df.drop(range(300000, 1746661))

deps = user_interaction.find_dependencies(pollution_df_small, .97)

print(deps)