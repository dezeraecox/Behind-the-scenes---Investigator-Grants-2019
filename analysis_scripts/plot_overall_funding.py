from wordcloud import WordCloud, STOPWORDS
import os
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from matplotlib.patches import Patch
from loguru import logger
from GEN_Utils import FileHandling
from GEN_Utils.HDF5_Utils import hdf_to_dict

logger.info('Import OK')

input_path = 'analysis_results/summary_stats/summary_stats.xlsx'
image_output = 'images/'

if not os.path.exists(output_folder):
    os.mkdir(output_folder)

# # Print all lone variables during execution
# from IPython.core.interactiveshell import InteractiveShell
# InteractiveShell.ast_node_interactivity = 'all'
# # Set plotting backgrounds to white
# matplotlib.rcParams.update(_VSCode_defaultMatplotlib_Params)
# matplotlib.rcParams.update({'figure.facecolor': (1,1,1,1)})

# Retrieve cleaned data from HDF5
raw_data = pd.read_excel(input_path, sheetname=None)
raw_data.keys()

awarded_summary = raw_data['total_rates']
awarded_summary = awarded_summary.drop([col for col in awarded_summary.columns.tolist() if 'Unnamed' in col], axis=1)

# Generate blog plot

for_plotting = awarded_summary.copy().reset_index()
numeric_cols = ['Year', 'Applications', 'Funded',
                'Funded Rate', 'Amount', 'type_cat']
for_plotting[numeric_cols] = for_plotting[numeric_cols].astype(float)
year_dict = {2015: 0, 2016: 1, 2017: 2, 2018: 3, 2019: 4}
for_plotting['Year_num'] = for_plotting['Year'].map(year_dict)
for_plotting['Funded Rate'] = for_plotting['Funded Rate'] * 100
for_plotting['Amount'] = for_plotting['Amount'] / 1000000

# sns.palplot()

sns.palplot(sns.light_palette('darkblue'), 12)
col_pal = [sns.color_palette('Blues')[x] for x in [2, 3, 5]]
labels = ['ECF/EL1', 'CDF/EL2', 'RF/L']


# col_pal = ['#a8d0e6', '#374785', '#24305e']

fig, ax = plt.subplots(figsize=(12, 5))
sns.barplot(x='Year_num',  y='Amount', data=for_plotting,
            hue='type_cat', ax=ax, palette=col_pal)
legend_elements = [Patch(facecolor=col_pal[x], label=labels[x]) for x in range(0, len(labels))]
ax.legend(handles=legend_elements, loc='upper left', title='Funding Amount', ncol=3)
ax2 = ax.twinx()
sns.lineplot(x='Year_num',  y='Funded', data=for_plotting,
             hue='type_cat', marker='o', markersize=10, palette=col_pal, ax=ax2)
ax2.set_ylim(0, 150)
# Fix all the adjusted elements
plt.legend(labels, loc='upper center', title='Number funded',
           ncol=3, bbox_to_anchor=(0.73, 1.0))
ax.set_xlabel('Year of funding')
ax.set_ylabel('Total funding amount ($M AUD)')
ax2.set_ylabel('Number of proposals funded', rotation=-90, labelpad=15)
plt.xticks(np.arange(0, 5, 1), labels=list(year_dict.keys()))
plt.title('Total funding awarded  in Fellowship Schemes.', loc='left',
          fontdict={'fontsize': 15, 'fontweight': 'bold'}, pad=20)
plt.tight_layout()
plt.savefig(f'{image_output}overall_funding.png', dpi=300)
plt.show()
