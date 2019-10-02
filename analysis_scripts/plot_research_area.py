from wordcloud import WordCloud, STOPWORDS
import os
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from bokeh.palettes import d3

from loguru import logger
from GEN_Utils import FileHandling
from GEN_Utils.HDF5_Utils import hdf_to_dict

logger.info('Import OK')

input_path = 'analysis_results/summary_stats/summary_stats.xlsx'
image_output = 'images/'

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

area_summary = raw_data['broad_research_proportions']
area_summary = area_summary.drop(
    [col for col in area_summary.columns.tolist() if 'Unnamed' in col], axis=1)

for_plotting = area_summary.copy()

numeric_cols = ['Year', 'total_awardees', 'Type', 'proportion']
for_plotting[numeric_cols] = for_plotting[numeric_cols].astype(float)
year_dict = {2015: 0, 2016: 1, 2017: 2, 2018: 3, 2019: 4}
for_plotting['Year_num'] = for_plotting['Year'].map(year_dict)

hue_order = {'Basic Science':1, 'Clinical Medicine and Science':2, 'Public Health':3, 'Health Services Research':4}

for_plotting['hue_order'] = for_plotting['Broad Research Area'].map(hue_order)

for_plotting.groupby(['Year']).sum() # Check 100% accounted for each year

sns.palplot(sns.color_palette("Paired"))
col_pal = [d3['Category20c'][20][x-1] for x in [1, 5, 9, 13]]
sns.palplot(col_pal)

col_pal = ['#4b6aab', '#b75b9e', '#d8774c', '#f1c75b']
col_pal = ['#286bf7', '#b00e84', '#d64809', '#edab00']


fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(x='Year_num',  y='proportion', data=for_plotting,
            hue='hue_order', ax=ax, palette=col_pal)
# Fix all the adjusted elements
handles, labels = ax.get_legend_handles_labels()
plt.legend(handles=handles, loc='upper right', labels=list(hue_order.keys()))
ax.set_xlabel('Year of funding')
ax.set_ylabel('Proportion of grants awarded to area (%)')
plt.xticks(np.arange(0, 5, 1), labels=list(year_dict.keys()))
plt.title('Grants awarded to Broad Research Areas', loc='left',
          fontdict={'fontsize': 15, 'fontweight': 'bold'}, pad=10)
plt.ylim(0, 55)
plt.tight_layout()
plt.savefig(f'{image_output}broad_research_area.png', dpi=300)
plt.show()
