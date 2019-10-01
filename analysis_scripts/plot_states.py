from IPython.core.interactiveshell import InteractiveShell
from wordcloud import WordCloud, STOPWORDS
import os
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas
import functools
from bokeh.palettes import d3

from loguru import logger
from GEN_Utils import FileHandling
from GEN_Utils.HDF5_Utils import hdf_to_dict

logger.info('Import OK')

input_path = 'analysis_results/summary_stats/summary_stats.xlsx'
output_folder = 'images/'

if not os.path.exists(output_folder):
    os.mkdir(output_folder)

# Print all lone variables during execution
InteractiveShell.ast_node_interactivity = 'all'
# Set plotting backgrounds to white
matplotlib.rcParams.update(_VSCode_defaultMatplotlib_Params)
matplotlib.rcParams.update({'figure.facecolor': (1, 1, 1, 1)})

# Retrieve cleaned data from HDF5
raw_data = pd.read_excel(input_path, sheetname=None)
raw_data.keys()

state_summary = raw_data['state_summary']
state_summary = state_summary.drop(
    [col for col in state_summary.columns.tolist() if 'Unnamed' in col], axis=1)

# import spatial data
# set the filepath and load in a shapefile
input_path = 'raw_data/australian_states.geo.json'
map_df = geopandas.read_file(input_path)
# check data type so we can see that this is not a normal dataframe, but a GEOdataframe
map_df.head()
# map_df.plot()

# Clean map df for plotting funding rate
state_mapper = {'Australian Capital Territory': 'ACT', 'New South Wales': 'NSW', 'Northern Territory': 'NT', 'Queensland': 'QLD', 'South Australia': 'SA', 'Tasmania': 'TAS', 'Victoria': 'VIC', 'Western Australia': 'WA'}

for_plotting = map_df.copy()
for_plotting['state'] = for_plotting['STATE_NAME'].map(state_mapper)

# Add columns for each year funded rate
year_dict = {}
for year, df in state_summary.groupby('Year'):
    small_df = df[['State and Territory', 'Funded Rate', 'Funded']]
    small_df['Funded Rate'] = small_df['Funded Rate'] * 100
    small_df.columns = ['state', f'{year}_rate', f'{year}_funded']
    year_dict[year] = small_df

merged_df = functools.reduce(lambda left, right: pd.merge(left, right, on='state', how='outer'), list(year_dict.values()))

for_plotting = pd.merge(for_plotting, merged_df, on='state', how='outer')

for_plotting['coords'] = for_plotting['geometry'].apply(lambda x: x.representative_point().coords[:])
for_plotting['coords'] = [coords[0] for coords in for_plotting['coords']]
for_plotting.reset_index(inplace=True)

optimised_coords = for_plotting[['state', 'coords']].copy()
optimised_coords[['x', 'y']] = pd.DataFrame(optimised_coords['coords'].tolist(), index=optimised_coords.index)
optimised_coords = optimised_coords.set_index('state').drop('coords', axis=1).T

optimised_coords['VIC'] = optimised_coords['VIC'] + [-1, -1]
optimised_coords['TAS'] = optimised_coords['TAS'] + [-0.5, -0.5]
optimised_coords['SA'] = optimised_coords['SA'] + [-3, 2]
optimised_coords['QLD'] = optimised_coords['QLD'] + [0, -2]
optimised_coords = optimised_coords.T


# set the range for the choropleth
vmin, vmax = 0, 50
# Set up the plot
# year = '2016'
sns.palplot(sns.light_palette('darkblue'))
cmap = sns.light_palette('darkblue', as_cmap=True)
cmap='BuGn'

years = state_summary['Year'].unique()
for year in years:
    year
    # create figure and axes for Matplotlib
    fig, ax = plt.subplots(1, figsize=(10, 6))
    for_plotting.plot(column=f'{year}_rate', cmap=cmap, linewidth=0.8, ax=ax, edgecolor='0.8')
    # remove the axis
    ax.axis('off')
    # add a title
    ax.set_title(f'Number of funded applications per state - {year}', loc='left',
                fontdict={'fontsize': 15, 'fontweight': 'bold'})
    # Add annotation for number funded
    for state, row in for_plotting.set_index('state').iterrows():
        plt.annotate(for_plotting.set_index('state').loc[state, f'{year}_funded'], xy=(
            optimised_coords.loc[state, 'x'], optimised_coords.loc[state, 'y']), fontsize=15, fontweight='bold')

    # create an annotation for the data source
    # ax.annotate('Source: NHMRC, 2019', xy=(0.1, .08),  xycoords='figure fraction',
    #             horizontalalignment='left', verticalalignment='top', fontsize=12, color='#555555')
    # ax.annotate(year, xy=(0.15, 0.8),  xycoords='figure fraction',
    #             horizontalalignment='left', verticalalignment='top', fontsize=15, color='black', style='italic', fontweight='bold')

    # Create colorbar as a legend
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=vmin, vmax=vmax))
    # empty array for the data range
    sm._A = []
    # add the colorbar to the figure
    cbar = fig.colorbar(sm)
    cbar.set_label('Proportion of applications funded (%)',
                   rotation=270, labelpad=20, fontsize=12)
    fig.savefig(f'{output_folder}{year}_per_state.png', dpi=300)
