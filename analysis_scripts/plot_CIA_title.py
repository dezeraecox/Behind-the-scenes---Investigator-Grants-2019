import matplotlib.colors as colors
import os
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from loguru import logger
from GEN_Utils import FileHandling
from GEN_Utils.HDF5_Utils import hdf_to_dict

logger.info('Import OK')

input_path = 'analysis_results/summary_stats/summary_stats.xlsx'
output_folder = 'images/'

if not os.path.exists(output_folder):
    os.mkdir(output_folder)

# Print all lone variables during execution
from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = 'all'
# Set plotting backgrounds to white
matplotlib.rcParams.update(_VSCode_defaultMatplotlib_Params)
matplotlib.rcParams.update({'figure.facecolor': (1,1,1,1)})

# Retrieve cleaned data from HDF5
raw_data = pd.read_excel(input_path, sheetname=None)
raw_data.keys()

title_summary = raw_data['CIA_title']
title_summary = title_summary.drop(
    [col for col in title_summary.columns.tolist() if 'Unnamed' in col], axis=1)

# Generate data for plotting
level_map = {'A/Pr': 2, 'Dr': 1, 'E/Pr': 4,
             'Miss': 0, 'Mr': 0, 'Mrs': 0, 'Ms': 0, 'Prof': 3}
title_summary['level'] = title_summary['CIA_title'].map(level_map)
for_plotting = title_summary.copy().reset_index(drop=True)
numeric_cols = ['Year', 'type_cat', 'level']
for_plotting[numeric_cols] = for_plotting[numeric_cols].astype(float)
year_dict = {2015: 0, 2016: 1, 2017: 2, 2018: 3, 2019: 4}
for_plotting['Year_num'] = for_plotting['Year'].map(year_dict)

total_funded = for_plotting.groupby(['Year_num', 'type_cat']).count()[
    'Year'].to_dict()
for_plotting = for_plotting.groupby(
    ['Year', 'Year_num', 'type_cat', 'level']).count()['CIA_name'].reset_index()
for_plotting['mapper'] = tuple(zip(for_plotting['Year_num'], for_plotting['type_cat']))
for_plotting['total_funded'] = for_plotting['mapper'].map(total_funded)

for_plotting['proportion_total_funded'] = for_plotting['CIA_name'] / \
    for_plotting['total_funded'] * 100

# Generate plot 1
fig, ax = plt.subplots()
sns.lineplot(x='Year_num',  y='proportion_total_funded', data=for_plotting,
             hue='level', marker='o', markersize=10, color='red', ci=None)
# Fix all the adjusted elements
plt.legend()
ax.set_ylim(-5, 105)
ax.set_xlabel('Year of funding')
ax.set_ylabel('Proportion of successful applications (%)')
plt.xticks(np.arange(0, 5, 1), labels=list(year_dict.keys()))
plt.title(f'Pre-nominal of successful applicants', loc='left', fontdict={
          'fontsize': 15, 'fontweight': 'bold'}, pad=30)
plt.tight_layout()
plt.savefig(f'{output_folder}title_proportion_level.png', dpi=300)
plt.show()

# Generate plot 2
for_plotting['size'] = for_plotting['proportion_total_funded'].astype(int)
x_mapper = {0.0: -0.5, 1.0: -0.25, 2.0: 0, 3.0: 0.25, 4.0: 0.5}
for_plotting['x_adjustment'] = for_plotting['level'].map(x_mapper)
for_plotting['x'] = for_plotting['Year_num'] + for_plotting['x_adjustment']
for_plotting['type_cat'] = for_plotting['type_cat'].astype(int)

levels = {0.25:'Miss/Ms/\nMrs/Mr', 1:'Dr', 2:'A/Pr', 3:'Prof', 4:'E/Pr'}

def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=100):
    new_cmap = colors.LinearSegmentedColormap.from_list(
        'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name, a=minval, b=maxval),
        cmap(np.linspace(minval, maxval, n)))
    return new_cmap

sns.palplot(sns.light_palette('darkred', 10))
col_pal = [sns.color_palette('Reds', 10)[x] for x in [2, 4, 6, 8, 9]]
sns.palplot(col_pal)

col_map = truncate_colormap(plt.get_cmap('Reds'), 0.2, 1.0, n=100)

fig, ax = plt.subplots(figsize=(10, 1.5))
# points = plt.scatter(x=for_plotting["x"], y=for_plotting["type_cat"],
#                       c=for_plotting["level"], s=for_plotting['size'], cmap='Reds')
points = sns.scatterplot(x='x', y='type_cat', data=for_plotting, hue='level', size='size',
                palette=col_map, sizes=(100, 500))
plt.ylim(0, 4)
ax.legend().remove()
# Fix all the adjusted elements

# Create colorbar as a legend, add labels
sm = plt.cm.ScalarMappable(cmap=col_map, norm=plt.Normalize(
    vmin=np.min(for_plotting['level']), vmax=np.max(for_plotting['level'])))
sm._A = []
cbar = fig.colorbar(sm, pad=0.12)
cbar.ax.get_yaxis().set_ticks([])
for level, name in levels.items():
    cbar.ax.text(5, level, name, ha='left', va='top', fontsize=6)
# add the colorbar to the figure
cbar.set_label('Prenominal title',
               rotation=90, labelpad=-16, fontsize=8)

# Generate legend entry for size
h, l = plt.gca().get_legend_handles_labels()
# plt.legend(h[5:], l[5:], labelspacing=1.2, title="popdensity", borderpad=1,
#            frameon=True, framealpha=0.9, loc=4, numpoints=1)
for handle in h:
    handle.set_color('grey')
plt.legend(reversed(h[6:]), ['', '', '', ''], labelspacing=1.2,  bbox_to_anchor=(1.045, 1), ncol=1, loc=1, borderaxespad=0.3, mode="expand", frameon=False)
ax.text(4.8, 2.65, 'Proportion of\nawardees (%)', rotation=90, fontsize=8)

plt.xticks(np.arange(0, 5, 1), labels=list(year_dict.keys()), fontsize=8)
plt.yticks(np.arange(0, 4, 1), labels=['', 'ECF/EL1', 'CDF/EL2', 'RF/L', ''], fontsize=8)
ax.set_xlabel('Year of funding', fontsize=8)
ax.set_ylabel('Category', fontsize=8)

plt.title('Prenominal title of awardees', loc='left',
          fontdict={'fontsize': 12, 'fontweight': 'bold'}, pad=10)

plt.savefig(f'{output_folder}CIA_title.svg')
plt.show()
