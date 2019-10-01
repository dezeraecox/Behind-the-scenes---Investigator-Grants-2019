import json
import os, re, time, random
import pandas as pd
import numpy as np

import pprint
from tqdm import tqdm


from fuzzywuzzy import process
from pandas.io.json import json_normalize
from pymed import PubMed
from loguru import logger
from GEN_Utils import FileHandling
from GEN_Utils.HDF5_Utils import dict_to_hdf

logger.info('Import OK')

input_path = 'analysis_results/summary_stats/summary_stats.xlsx'
output_folder = 'analysis_results/scival_test/'

if not os.path.exists(output_folder):
    os.mkdir(output_folder)

# Get list of authors
raw_authors = pd.read_excel(input_path, sheet_name='name_summary')
raw_authors = raw_authors.drop([col for col in raw_authors.columns.tolist() if 'Unnamed' in col], axis=1)
raw_authors.keys()

scival_import = raw_authors[['name', 'Year']].copy()
scival_import.columns = ['Author', 'Level 1']

def chunker(seq, chunk_size):
    return (seq[pos:pos + chunk_size] for pos in range(0, len(seq), chunk_size))


indexes = scival_import.index.tolist()
chunk_indexes = chunker(indexes, 100)

for x, indexes in enumerate(chunk_indexes):
    min_index = np.min(indexes)
    max_index = np.max(indexes) + 1
    scival_import.iloc[min_index:max_index].to_csv(f'{output_folder}name_year_{x}.csv', sep=',', index=False)

scival_import.to_csv(f'{output_folder}name_year_summary.csv', sep=',', index=False)

# imported exported files into scival using web interface
# Accepted 'best match' profiles for any non-mapped researchers (approx 5-10% not found)
# Added all matched researchers to single panel, then exported year versus (1) FWCI and (2) number of pubs

# FWCI at time of award
# copy CIA_name summary df
awardees = raw_authors.copy()
awardees['surname'] = awardees['name'].str.split(' ').str[1]

# Import raw data for fwci
input_folder = 'raw_data/scival/'
file_list = [filename for filename in os.listdir(input_folder) if 'Citation_Impact' in filename]

fwci_raw = []
for filename in file_list:
    fwci_raw.append(pd.read_excel(f'{input_folder}{filename}', skiprows=12))
fwci_raw = pd.concat(fwci_raw)

fwci_clean = fwci_raw.rename(columns={'Unnamed: 0': 'Author'}).drop(
    'Unnamed: 1', axis=1)
fwci_clean['surname'] = fwci_clean['Author'].str.split(',').str[0]
fwci_clean = fwci_clean.set_index('Author')
fwci_clean.drop([col for col in fwci_clean.columns.tolist() if 'Unnamed' in str(col)], axis=1, inplace=True)
fwci_clean.dropna(axis=0, how='all', inplace=True)
fwci_clean.replace('-', np.nan, inplace=True)

retrieved_authors = fwci_clean.index.tolist()
surname_mapper = {}
for index in awardees.index.tolist():
    author = awardees.loc[index, 'name']
    author_surname = awardees.loc[index, 'surname']
    # process.extract(author, retrieved_authors)
    result, match = process.extractOne(author, retrieved_authors)
    result_surname = result.split(',')[0]
    if result_surname.lower() == author_surname.lower():
        surname_mapper[author] = result
    else:
        logger.info(f'No match found for {author}')

awardees['match_name'] = awardees['name'].map(surname_mapper)
len(awardees['match_name'].dropna()) # approximately 88% of awardees had matched names!

# use matched name to find FWCI in the year of award from the fwci df
search_dict = dict(zip(awardees.dropna(how='any', subset=['match_name'])[
                   'match_name'], awardees.dropna(how='any', subset=['match_name'])['Year']))
fwcis = {}
for name, year in search_dict.items():
    past_range = np.arange(year-10, year+1, 1)
    fwcis[name] = fwci_clean.loc[name, past_range].mean()

awardees['fwci_awarded'] = awardees['match_name'].map(fwcis)

# Number of publications in 10 years pre-award
file_list = [filename for filename in os.listdir(
    input_folder) if 'Scholarly_Output' in filename]

# Read in raw scival info, clean
pubs_raw = []
for filename in file_list:
    pubs_raw.append(pd.read_excel(f'{input_folder}{filename}', skiprows=12))
pubs_raw = pd.concat(pubs_raw)
pubs_clean = pubs_raw.rename(columns={'Unnamed: 0': 'name'})
pubs_clean = pubs_clean.drop([col for col in pubs_clean if 'Unnamed' in str(col)], axis=1)
pubs_clean.set_index('name', inplace=True)
pubs_clean.head(20)

pubs_clean.loc['Jenkins, Misty R.']

# count number of pubs 10 years before award
pubs = {}
# test_dict = {k: v for k, v in random.sample(search_dict.items(), 10)}
for name, year in search_dict.items():
    past_range = np.arange(year-10, year+1, 1)
    pubs[name] = pubs_clean.loc[name, past_range].sum()

awardees['pubs_awarded'] = awardees['match_name'].map(pubs)

# Save completed mapping to excel
FileHandling.df_to_excel(data_frames=[awardees], sheetnames=['fwci_pubs'], output_path=f'{output_folder}ten_year_metrics_summary.xlsx')