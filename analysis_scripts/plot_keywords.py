from wordcloud import WordCloud, STOPWORDS
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

kw_summary = raw_data['key_word_summary']
kw_summary = kw_summary.drop(
    [col for col in kw_summary.columns.tolist() if 'Unnamed' in col], axis=1)

kw_cols = [col for col in kw_summary.columns.tolist() if 'Res KW' in col]

# sns.palplot(sns.color_palette(('Blues')))
col_single = sns.color_palette('Blues').as_hex()[5]

for year in kw_summary['Year'].unique():
    # Test a word cloud for this
    # text = kw_summary[kw_summary['Year'] == year][kw_cols].values
    text = kw_summary[kw_summary['Year'] == year][kw_cols].values
    text = pd.Series(text.flatten()).str.split(
        expand=True).stack().value_counts()
    year
    text[0:5]
    text = dict(text)
    wordcloud = WordCloud(
        width=1000,
        height=1000,
        background_color='white', color_func=lambda *args, **kwargs: (11, 85, 159)).generate_from_frequencies(text)
    fig = plt.figure(
        figsize=(40, 30),
        facecolor='k',
        edgecolor='k')
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.tight_layout(pad=0)
    plt.savefig(f'{output_folder}keywords_{year}.png')
    plt.show()
