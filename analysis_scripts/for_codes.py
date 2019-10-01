import os
import re
import pandas as pd
import numpy as np

from loguru import logger
from GEN_Utils import FileHandling

logger.info('Import OK')

# # Print all lone variables during execution
# from IPython.core.interactiveshell import InteractiveShell
# InteractiveShell.ast_node_interactivity = 'all'
# # Set plotting backgrounds to white
# matplotlib.rcParams.update(_VSCode_defaultMatplotlib_Params)
# matplotlib.rcParams.update({'figure.facecolor': (1,1,1,1)})

input_path = 'raw_data/FOR_codes.xlsx'
output_folder = 'analysis_results/for_codes/'

if not os.path.exists(output_folder):
    os.mkdir(output_folder)

# Read in raw data from 6-digit codes
raw_data = pd.read_excel(input_path, sheet_name='6-digit codes', header=None)
codes = raw_data.copy().rename(columns={0: 'raw_label', 1: 'description'})
codes = codes[['raw_label', 'description']]


test = codes

# Collect codes at each level
table_headers = test[test.isnull().any(axis=1)]
headers = table_headers.set_index('raw_label').T.columns.dropna()
fields = [col for col in headers if 'GROUP' not in col]
codes = [field.split(' ')[0] for field in fields]
labels = [(' ').join(field.split(' ')[1:]) for field in fields]
fields = dict(zip(codes, labels))

groups = [col for col in headers if 'GROUP' in col]
codes = [group.split(' ')[1] for group in groups]
labels = [(' ').join(group.split(' ')[2:]) for group in groups]
fields.update(dict(zip(codes, labels)))

themes = test.dropna(how='any', axis=0)
fields.update(dict(zip(themes['raw_label'], themes['description'])))

cleaned_codes = pd.DataFrame.from_dict(fields, orient='index').reset_index().rename(columns={'index':'code', 0:'label'})
cleaned_codes['length'] = cleaned_codes['code'].astype(str).apply(len)
level_map = {2: 1, 4: 2, 5: 3, 6: 3}
cleaned_codes['level'] = cleaned_codes['length'].map(level_map)
cleaned_codes['code'] = cleaned_codes['code'].astype(str)
cleaned_codes['code'] = ['0'+code if len(code) == 5 else code for code in cleaned_codes['code']]
cleaned_codes['parent_field_code'] = cleaned_codes['code'].str[0:2]
cleaned_codes['parent_group_code'] = [code if len(code) == 4 else np.nan for code in cleaned_codes['code'].str[0:4]]


FileHandling.df_to_excel(data_frames=[cleaned_codes.drop('length', axis=1)], sheetnames=['FOR_summary'], output_path=f'{output_folder}for_summary.xlsx')

cleaned_codes.tail(50)

cleaned_codes.to_csv(f'{output_folder}for_summary.csv')









# split on ' ' - any 6-digit codes will not be affected, whereas 4-digit codes will have two elements
# for all codes, keep element[0] and for four digit codes return map into 'description' column

# Generate mapped column for 2-digit and 4-digit codes (by splitting number, then collecting first two or first four digits?)

# Generate reverse dictionary mapping description to each set of codes (two, four or six-digit)

# Import summary data for field of research

# Collect relevant cols - year, level, FOR

# Map FOR to 2, 4, 6-digit codes

# Save summary to excel
