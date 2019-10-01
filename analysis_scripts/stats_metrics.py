from IPython.core.interactiveshell import InteractiveShell
from wordcloud import WordCloud, STOPWORDS
import os
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pingouin as pg

from loguru import logger
from GEN_Utils import FileHandling
from GEN_Utils.HDF5_Utils import hdf_to_dict

logger.info('Import OK')

input_path = 'analysis_results/scival_test/ten_year_metrics_summary.xlsx'
output_folder = 'analysis_results/stats_metrics/'

if not os.path.exists(output_folder):
    os.mkdir(output_folder)

# Print all lone variables during execution
InteractiveShell.ast_node_interactivity = 'all'
# Set plotting backgrounds to white
matplotlib.rcParams.update(_VSCode_defaultMatplotlib_Params)
matplotlib.rcParams.update({'figure.facecolor': (1, 1, 1, 1)})

metrics = pd.read_excel(input_path)
metrics.head(100)

# in any case where values were not read properly, discard
def value_checker(value):
    try:
        return float(value)
    except:
        return np.nan

metrics['fwci_awarded'] = metrics['fwci_awarded'].apply(value_checker)
metrics['pubs_awarded'] = metrics['pubs_awarded'].apply(value_checker)

# Collect datapoints per year
pubs_list = {}
fwci_list = {}

for year, df in metrics.groupby(['Year']):
    for level, data in df.groupby('type_cat'):
        pubs_list[f'{year}_{level}'] = list(data['pubs_awarded'])
        fwci_list[f'{year}_{level}'] = list(data['fwci_awarded'])
# Generate separate dataframes
pubs = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in pubs_list.items()]))
fwci = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in fwci_list.items()]))

FileHandling.df_to_excel(data_frames=[pubs, fwci], sheetnames=['pubs', 'fwci'], output_path=f'{output_folder}metrics_per_year.xlsx')

# Collect cols for each level
levels = ['_1', '_2', '_3']

for level in levels:
    
    cols = [col for col in pubs.columns.tolist() if level in col]
    test_df = pubs[cols].melt(value_name='publications', var_name='Group')

    # Two-way ANOVA
    aov = pg.anova(data=test_df, dv='publications', between='Group',
                   export_filename=f'{output_folder}anova_pubs{level}.csv')
    pg.print_table(aov)

    # FDR-corrected post hocs with Hedges'g effect size
    posthoc = pg.pairwise_ttests(data=test_df, dv='publications', between='Group', within=None, parametric=True, alpha=.05, tail='two-sided', padjust='bonf', effsize='none', return_desc=False, export_filename=f'{output_folder}bonf_pubs{level}.csv')

    # Pretty printing of table
    pg.print_table(posthoc, floatfmt='.3f')

