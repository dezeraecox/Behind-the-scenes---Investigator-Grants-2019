import json
import os
import re
import time
import pandas as pd
import numpy as np

import pprint
from tqdm import tqdm

from pandas.io.json import json_normalize
from pymed import PubMed
from loguru import logger
from GEN_Utils import FileHandling
from GEN_Utils.HDF5_Utils import dict_to_hdf

logger.info('Import OK')

input_path = 'analysis_results/summary_stats/summary_stats.xlsx'
output_folder = 'analysis_results/pubmed_test/'

if not os.path.exists(output_folder):
    os.mkdir(output_folder)

# Define function to loop over the retrieved articles, count len (number of papers)

def author_lookup(author_list):
    author_journals = {}
    author_count = {}

    for author in author_list:
        article_journals = []
        article_count = []
        # Execute the query against the API
        query = f"{author}[Author]"
        results = pubmed.query(query, max_results=500)
        # Collect results and quantify
        try:
            for article in results:
                try:
                    # Collect a JSON representation of the object
                    article_journals.append(article.journal)
                    article_count.append(article.publication_date)
                except:
                    logger.info(f'{article.title} not processed.')
                    pass
            author_count[author] = article_count
            author_journals[author] = article_journals
        except:
            logger.info(f'{author} not processed.')
            pass

    return (author_count, author_journals)


def chunker(seq, chunk_size):
    return (seq[pos:pos + chunk_size] for pos in range(0, len(seq), chunk_size))


# Create a PubMed object that GraphQL can use to query requested by PubMed Central
pubmed = PubMed(tool="authorsearch", email="dezerae53@hotmail.com")

# Get list of authors
raw_authors = pd.read_excel(input_path, sheet_name='name_summary')
raw_authors = raw_authors.drop(
    [col for col in raw_authors.columns.tolist if 'Unnamed' in col], axis=1)
raw_authors.keys()

# Split by year awarded, and search in pubmed in chunks
year = 2019
year_dict = {}
df = raw_authors[raw_authors['Year'] == year]
author_list = list(df['name'])
# Collect count of papers
count_dict = {}
journal_dict = {}
author_chunks = [chunk for chunk in chunker(author_list, chunk_size=10)]
for i in tqdm(range(len(author_chunks))):
    count, journals = author_lookup(author_chunks[i])
    count_dict.update(count)
    journal_dict.update(journals)
    time.sleep(2) # Added this to try and keep pubmed happy
# Save to dict according to year
year_dict['count'] = pd.DataFrame.from_dict(count_dict, orient='index').T
year_dict['journals'] = pd.DataFrame.from_dict(journal_dict, orient='index').T


# Save outputs
# dict_to_hdf(papers_dict, output_path=f'{output_folder}2019_author_papers.h5', h5_group=' /')
FileHandling.df_to_excel(data_frames=list(year_dict.values()), sheetnames = list(year_dict.keys()), output_path=f'{output_folder}publications_summary_{year}.xlsx')

# check out the results
year_dict['journals'].head()
year_dict['journals'].dropna(axis=1, how='all').shape # of the 246 awardees, 245 have at least one pu listed

# Count number of pubs for each person
num_pubs = year_dict['count'].count().to_dict()

# Map onto original dataset
author_summary = raw_authors[raw_authors['Year'] == year]
author_summary['pub_count'] = author_summary['CIA_name'].map(num_pubs)

# Generate list of top journal papers
journal_names = ['Cell', 'Nature', 'Science']
num_journals = year_dict['journals'].copy()
num_journals = num_journals[num_journals.isin(journal_names)]

# TODO 2019 September 03: filter journals to count number of cell/science/nature papers per person

# Save outputs
# dict_to_hdf(papers_dict, output_path=f'{output_folder}2019_author_papers.h5', h5_group=' /')
FileHandling.df_to_excel(data_frames=list(year_dict.values()), sheetnames=list(
    year_dict.keys()), output_path=f'{output_folder}publications_summary_{year}.xlsx')

# Test individual authors
query = f"Danny Eckert[Author]"
results = pubmed.query(query, max_results=500)
# Collect results and quantify
for article in results:
    article
    try:
        # Collect a JSON representation of the object
        article_journals.append(article.journal)
        article_count.append(article.publication_date)
    except:
        pass
