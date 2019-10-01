from wordcloud import WordCloud, STOPWORDS
import os
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import ptitprince as pt

from loguru import logger
from GEN_Utils import FileHandling
from GEN_Utils.HDF5_Utils import hdf_to_dict

logger.info('Import OK')

input_path = 'analysis_results/scival_test/ten_year_metrics_summary.xlsx'
output_folder = 'images/'

if not os.path.exists(output_folder):
    os.mkdir(output_folder)

# Print all lone variables during execution
from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = 'all'
# Set plotting backgrounds to white
matplotlib.rcParams.update(_VSCode_defaultMatplotlib_Params)
matplotlib.rcParams.update({'figure.facecolor': (1,1,1,1)})

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

for_plotting = metrics.copy().reset_index()
numeric_cols = ['Year', 'type_cat']
for_plotting[numeric_cols] = for_plotting[numeric_cols].astype(float)
year_dict = {2015: 0, 2016: 1, 2017: 2, 2018: 3, 2019: 4}
for_plotting['Year_num'] = for_plotting['Year'].map(year_dict)


# col_pal = [sns.color_palette('Blues')[x] for x in [2, 3, 5]]
# colors = {1.0: ['#89bedc'], 2.0: ['#539ecd'], 3.0: ['#0b559f']}
colors = {1.0: ['#0b559f'], 2.0: ['#0b559f'], 3.0: ['#0b559f']}
labels = ['ECF/EL1', 'CDF/EL2', 'RF/L']

# Test histogram for years
fig, ax = plt.subplots(figsize=(12, 5))
for year, test_df in for_plotting.groupby('Year'):
    test_df
    sns.distplot(test_df['pubs_awarded'].dropna(), ax=ax, hist=False, kde=True, label=year)

# Plot all together
fig, ax = plt.subplots(figsize=(12, 12))
pt.RainCloud(x='Year', y='pubs_awarded', hue='type_cat', data=for_plotting, palette=col_pal, width_viol=.6, ax=ax, orient='h', move=.25, alpha=0.5, dodge=True)
plt.xlabel('Number of publications in ten years prior to award.')
plt.ylabel('Year of award.')
plt.title(f'Level {level}')

# Test raincloud plots for each level
for level, df in for_plotting.groupby('type_cat'):
    level
    fig, ax = plt.subplots(figsize=(12, 5))
    pt.RainCloud(x=df['Year'], y=df['pubs_awarded'],
                 palette=sns.color_palette(colors[level]), width_viol=.6, ax=ax, orient='h', move=.25)
    plt.xlabel('Number of publications in ten years prior to award')
    plt.ylabel('Year of award')
    ax.set_yticklabels([2015, 2016, 2017, 2018, 2019])
    ax.axvline(df[df['Year'] == 2015.0]['pubs_awarded'].median(), color='firebrick', linestyle='--', alpha=0.5)
    ax.set_axisbelow(True)
    plt.title(f'Ten-year publication record of successful awardees at level {int(level)}.', loc='left', fontdict={'fontsize': 15, 'fontweight': 'bold'}, pad=20)
    plt.savefig(f'{output_folder}publications_level_{level}.png')

# Repeat for FWCI
for level, df in for_plotting.groupby('type_cat'):
    level
    fig, ax = plt.subplots(figsize=(12, 5))
    pt.RainCloud(x=df['Year'], y=df['fwci_awarded'],
                 palette=sns.color_palette(colors[level]), width_viol=.6, ax=ax, orient='h', move=.25)
    plt.xlabel('Average FWCI in ten years prior to award')
    plt.ylabel('Year of award')
    plt.xlim(-2.5, 25)
    ax.set_yticklabels([2015, 2016, 2017, 2018, 2019])
    ax.axvline(df[df['Year'] == 2015.0]['fwci_awarded'].median(),
               color='firebrick', linestyle='--', alpha=0.5)
    ax.set_axisbelow(True)
    plt.title(f'Average FWCI of successful awardees at level {int(level)}.', loc='left', fontdict={
              'fontsize': 15, 'fontweight': 'bold'}, pad=20)
    plt.savefig(f'{output_folder}fwci_level_{level}.png')
