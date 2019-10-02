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

gender_summary = raw_data['per_gender']
gender_summary = gender_summary.drop(
    [col for col in gender_summary.columns.tolist() if 'Unnamed' in col], axis=1)

# As Leadership levels were maintained separately in this table, need to map these to level 3 for 2019


# Generate data for plotting
for_plotting = gender_summary.copy().reset_index(drop=True)

males = for_plotting[['Year', 'type_cat'] +
                     [col for col in for_plotting if 'm_' in col]]
males.columns = ['Year', 'type_cat',
                 'Applications', 'Funded', 'Rate', 'Amount']
males['gender'] = 'M'
females = for_plotting[['Year', 'type_cat'] +
                       [col for col in for_plotting if 'f_' in col]]
females.columns = ['Year', 'type_cat',
                   'Applications', 'Funded', 'Rate', 'Amount']
females['gender'] = 'F'

for_plotting = pd.concat([males, females]).reset_index(drop=True)
for_plotting = for_plotting.groupby(['Year', 'gender', 'type_cat']).sum().drop('Rate', axis=1).reset_index()

numeric_cols = ['Year', 'type_cat', 'Applications', 'Funded', 'Amount']
for_plotting[numeric_cols] = for_plotting[numeric_cols].astype(float)
year_dict = {2015: 0, 2016: 1, 2017: 2, 2018: 3, 2019: 4}
for_plotting['Year_num'] = for_plotting['Year'].map(year_dict)
for_plotting['Amount'] = for_plotting['Amount'] / 1000000
for_plotting['proportion_Funded'] = for_plotting['Funded'] / for_plotting['Applications'] *100
total_funded = for_plotting.groupby(['Year', 'type_cat']).sum()['Funded'].to_dict()
total_amounts = for_plotting.groupby(['Year', 'type_cat']).sum()[
    'Amount'].to_dict()

for_plotting['mapper'] = tuple(zip(for_plotting['Year'], for_plotting['type_cat']))
for_plotting['total_amount'] = for_plotting['mapper'].map(total_amounts)
for_plotting['total_funded'] = for_plotting['mapper'].map(total_funded)

for_plotting['proportion_amount'] = for_plotting['Amount'] / for_plotting['total_amount'] * 100
for_plotting['proportion_total_funded'] = for_plotting['Funded'] / \
    for_plotting['total_funded'] * 100




# Generate plot 1

# sns.palplot(sns.color_palette("Purples"))
# fem_colour = sns.color_palette("Purples")[4]
fem_colour = '#511751'
male_colour = sns.color_palette("Oranges")[4]

col_pal = [fem_colour, male_colour]
labels = ['Female', 'Male']

df = for_plotting.groupby(['Year_num', 'gender']).sum().reset_index()
fig, ax = plt.subplots(figsize=(12, 5))
sns.barplot(x='Year_num',  y='Amount', data=df, hue='gender', ax=ax, palette=col_pal)
legend_elements = [Patch(facecolor=col_pal[x], label=labels[x]) for x in range(0, len(labels))]
ax.legend(handles=legend_elements, loc='upper left', title='Funding Amount', ncol=3)
ax2 = ax.twinx()
sns.lineplot(x='Year_num',  y='Funded', data=df,
            hue='gender', marker='o', markersize=10, palette=col_pal, ax=ax2)
ax2.set_ylim(0, 200)
# Fix all the adjusted elements
plt.legend(labels, loc='upper left', title='Number funded', ncol=3, bbox_to_anchor=(0.67, 1.0))
ax.set_xlabel('Year of funding')
ax.set_ylabel('Total funding amount ($M AUD)')
ax2.set_ylabel('Number of successful applications', rotation=-90, labelpad=15)
plt.xticks(np.arange(0, 5, 1), labels=list(year_dict.keys()))
plt.title('Total funding awarded according to gender.', loc='left',
        fontdict={'fontsize': 15, 'fontweight': 'bold'}, pad=20)
plt.tight_layout()
plt.savefig(f'{output_folder}gender_total.png', dpi=300)
plt.show()


# Generate plot 2

for level, df in for_plotting.groupby('type_cat'):
    plotting = df[df['gender'] == 'F']
    fig, ax = plt.subplots(figsize=(10, 4))
    m = sns.barplot(orient='h', y=list(plotting['Year_num']), x=[100 for x in plotting['Year_num']], color=male_colour)
    f = sns.barplot(x=plotting['proportion_total_funded'],  y=plotting['Year_num'], color=fem_colour, orient='h')

    # Fix all the adjusted elements
    ax.set_ylabel('Year of funding')
    ax.set_xlabel('Proportion of funded applications (%)')
    ax2.set_ylabel('Success rate (%)', rotation=-90, labelpad=15)
    plt.yticks(np.arange(0, 5, 1), labels=list(year_dict.keys()))
    plt.title(f'Proportion of Fellowships awarded by gender at level {int(level)}.', loc='left',
              fontdict={'fontsize': 15, 'fontweight': 'bold'}, pad=20)
    ax.axvline(50, c='#636363', linestyle='--', linewidth=3)

    plt.tight_layout()
    plt.savefig(f'{output_folder}gender_proportion_level{level}.png', dpi=300)
    plt.show()
