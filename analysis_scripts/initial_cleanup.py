import os, re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from loguru import logger
from GEN_Utils import FileHandling
from GEN_Utils.HDF5_Utils import dict_to_hdf

logger.info('Import OK')

# # Print all lone variables during execution
# from IPython.core.interactiveshell import InteractiveShell
# InteractiveShell.ast_node_interactivity = 'all'
# # Set plotting backgrounds to white
# matplotlib.rcParams.update(_VSCode_defaultMatplotlib_Params)
# matplotlib.rcParams.update({'figure.facecolor': (1,1,1,1)})

input_folder = 'raw_data/nhmrc_grant_outcomes/'
output_folder = 'analysis_results/initial_cleanup/'

if not os.path.exists(output_folder):
    os.mkdir(output_folder)

# Generate list of raw data files
file_list = [filename for filename in os.listdir(input_folder)]

# Look through files and find sheet names, preview raw data and load into dictionary
raw_results = {}
for filename in file_list:
    # to handle 2018/2019 results
    if len(filename.split('-')) == 1:
        year = filename.split('_')[3]
    elif len(filename.split('-')) == 3:
        year = filename.split('-')[0]
    else:
        logger.info(f'Unknown filename registered.')
        break
    # to handle <2017 results
    raw_results[year] = pd.read_excel(f'{input_folder}{filename}', sheet_name=None)

# Check results were loaded under correct name
raw_results.keys()

# Check structure of each document
for key, collection in raw_results.items():
    key
    raw_results[key].keys()

# most appear to have a similar sheet layout, and to get all the info I need will have to unpack at least four of the sheets.. Also the names of the sheets are slightly different in all years :/


def table_cleanup_age_gender(test_data):

    table_test = test_data.T.reset_index().T.reset_index(drop=True)
    table_test = table_test.dropna(how='all').reset_index()
    table_test['table_header'] = table_test[0].dropna().str.contains('outcome')
    table_labels = list(table_test[table_test['table_header'] == True][0].index.values.astype(int))
    table_labels.append(np.max(table_test.index.values))
    tables = {}
    for x in range(0, len(table_labels)-1):
        mini_table = table_test.iloc[table_labels[x]:table_labels[x+1]].reset_index(drop=True).drop(['index', 'table_header'], axis=1)
        mini_table_name = mini_table.loc[0, 0]
        mini_table.drop(0, inplace=True)
        mini_table = mini_table.dropna(axis=1, how='all')
        if 'scheme' in mini_table_name:
            if 'age' in mini_table_name:
                mini_table.columns = mini_table.iloc[0]
                tables['age'] = mini_table.drop(1).set_index('Scheme')
            elif 'gender' in mini_table_name:
                col_names = ['Applications', 'Funded', 'Rate',	'Amount']
                new_cols = ['Scheme'] + [f'{gender}{col}' for gender in ['f_', 'm_', 'ns_'] for col in col_names]
                mini_table.columns = new_cols[0:len(mini_table.columns.tolist())]
                mini_table.drop([1, 2], inplace=True)
                tables['gender'] = mini_table.set_index('Scheme')
        else:
            logger.info(f'{mini_table_name} not saved.')

    return tables


def table_cleanup_state_institute(test_data):

    table_test = test_data.T.reset_index().T.reset_index(drop=True)
    table_test = table_test.dropna(how='all').reset_index()
    table_test['table_header'] = table_test[0].dropna().str.contains('outcome')
    table_labels = list(
        table_test[table_test['table_header'] == True][0].index.values.astype(int))
    table_labels.append(np.max(table_test.index.values))
    tables = {}
    for x in range(0, len(table_labels)-1):
        mini_table = table_test.iloc[table_labels[x]:table_labels[x+1]
                                     ].reset_index(drop=True).drop(['index', 'table_header'], axis=1)
        mini_table_name = mini_table.loc[0, 0]
        mini_table.drop(0, inplace=True)
        mini_table = mini_table.dropna(axis=1, how='all')
        if 'State' in mini_table_name:
            mini_table.columns = mini_table.iloc[0]
            tables['state'] = mini_table.drop(1)
        elif 'Administering Institutions' in mini_table_name:
            mini_table.columns = mini_table.iloc[0]
            tables['Administering_Institutions'] = mini_table.drop(
                1)
        elif 'Leadership Level' in mini_table_name:
            mini_table.columns = mini_table.iloc[0]
            tables['Leadership_levels'] = mini_table.drop(
                1)
        else:
            logger.info(f'{mini_table_name} not saved.')

    return tables


def table_cleanup_state_institute_2016(test_data):

    table_test = test_data.T.reset_index().T.reset_index(drop=True)
    table_test = table_test.dropna(how='all').reset_index()
    table_test['table_header'] = table_test[0].dropna().str.contains('outcome')
    table_labels = list(
        table_test[table_test['table_header'] == True][0].index.values.astype(int))
    table_labels.append(np.max(table_test.index.values))
    tables = {}
    for x in range(0, len(table_labels)-1):
        mini_table = table_test.iloc[table_labels[x]:table_labels[x+1]
                                     ].reset_index(drop=True).drop(['index', 'table_header'], axis=1)
        mini_table_name = mini_table.loc[1, 0]
        mini_table.drop(0, inplace=True)
        mini_table = mini_table.dropna(axis=1, how='all')
        if 'State' in mini_table_name:
            mini_table.columns = mini_table.iloc[0]
            tables['state'] = mini_table.drop(1)
        elif 'Administering Institution' in mini_table_name:
            mini_table.columns = mini_table.iloc[0]
            tables['Administering_Institutions'] = mini_table.drop(
                1)
        else:
            logger.info(f'{mini_table_name} not saved.')

    return tables

# Collect gender and age tables
cleaned_data = {}
for key, year_dict in raw_results.items():
    sheet_name = [name for name in list(year_dict.keys()) if 'Age' in name][0]
    cleaned_data[key] = table_cleanup_age_gender(test_data=year_dict[sheet_name].copy())

# Collect grant summary table
for year, year_dict in raw_results.items():
    cleaned_data[year]['grant_summary'] = year_dict['GRANTS DATA']

# Collect scheme-specific state/institute breakdown
for year, year_dict in raw_results.items():
    year
    year_dict.keys()
    if year == '2019':
        fellowships = ['Investigator Grants']
        for fellowship_type in fellowships:
            cleaned_data[year][fellowship_type] = table_cleanup_state_institute(year_dict[fellowship_type])
    elif year == '2016':
        old_fellowships = ['ECF', 'CDF', 'Research Fellowships']
        new_fellowships = ['ECF', 'CDF', 'RF']
        for x, fellowship_type in enumerate(old_fellowships):
            cleaned_data[year][new_fellowships[x]] = table_cleanup_state_institute_2016(
                year_dict[fellowship_type])
    
    elif year in ['2015', '2017', '2018']:
        old_fellowships = ['Early Career Fellowships', 'Career Development Fellowships', 'Research Fellowships']
        new_fellowships = ['ECF', 'CDF', 'RF']
        for x, fellowship_type in enumerate(old_fellowships):
            cleaned_data[year][new_fellowships[x]] = table_cleanup_state_institute(year_dict[fellowship_type])


# save to HDF5 for safe keeping
output_path = f'{output_folder}cleaned_data.h5'
dict_to_hdf(cleaned_data, output_path, h5_group='/')

