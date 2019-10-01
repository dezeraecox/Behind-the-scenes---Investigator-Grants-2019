import os, re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from loguru import logger
from GEN_Utils import FileHandling
from GEN_Utils.HDF5_Utils import hdf_to_dict

logger.info('Import OK')

input_path = 'analysis_results/initial_cleanup/cleaned_data.h5'
output_folder = 'analysis_results/summary_stats/'
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
raw_data = pd.HDFStore(input_path)
clean_data = hdf_to_dict(raw_data, path='/')
raw_data.close()

# Check out what was loaded
clean_data.keys()
clean_data['2019'].keys()
clean_data['2019']['Investigator Grants'].keys()
clean_data['2019']['Investigator Grants']['Leadership_levels']
clean_data['2016'].keys()


"""
Question 1: Overall number of awards and amount of research funds per year

- sum all Investigator for 2019
- sum all ECF, CDF and Research Fellowships for previous years
- gather info from states summary - take total awarded and $$ amount

"""

overall_awarded = {}
row_count = 0
# Collecting all but 2019
for year in clean_data.keys():
    if year != '2019':
        fellowships = ['ECF', 'CDF', 'RF']
        for fellowship_type in fellowships:
            test_data = clean_data[year][fellowship_type]['state']
            details = list(test_data.set_index('State and Territory').loc['Total for Competitive grants'])
            overall_awarded[row_count] = [year, fellowship_type] + details
            row_count += 1

overall_awarded = pd.DataFrame.from_dict(overall_awarded).T
overall_awarded.columns = ['Year', 'Type', 'Applications', 'Funded', 'Funded Rate', 'Amount']

# Adding in 2019 info
invest_mapper = {'Leadership ':'L',	'Emerging Leadership Level 2':'EL2', 'Emerging Leadership Level 1': 'EL1'}
investigators = clean_data['2019']['Investigator Grants']['Leadership_levels']
investigators['Type'] = investigators['Competitive grants'].map(invest_mapper)
investigators['Year'] = '2019'
investigators = investigators.set_index('Competitive grants').drop('Total').reset_index(drop=True)
investigators.columns.tolist()
investigators = investigators[['Year', 'Type', 'Applications', ' Funded', 'Funded Rate', 'Amount']]
investigators.columns = ['Year', 'Type', 'Applications', 'Funded', 'Funded Rate', 'Amount']

# Generate summary df, and map awards to categories
awarded_summary = pd.concat([overall_awarded, investigators])
type_mapper = {'ECF': 1, 'CDF': 2, 'RF': 3, 'L': 3, 'EL2': 2, 'EL1': 1}
awarded_summary['type_cat'] = awarded_summary['Type'].map(type_mapper)

# Check out a few parameters
# for_plotting = awarded_summary.groupby('Year').sum().drop('Type', axis=1)
# rate = for_plotting['Funded']/for_plotting['Applications']
# rate.plot()
# sns.barplot(x='Year', y='Amount', data=awarded_summary, hue='type_cat')





"""
Question 2+3: Overall number of awards, success rate and amount of research funds per year according to gender

- sum all Investigator for 2019
- sum all ECF, CDF and Research Fellowships for previous years
- gather info from Gender summary

"""

gender_summary = {}
row_count = 0
# Collect all but 2019
for year in clean_data.keys():
    if year != '2019':
        test_data = clean_data[year]['gender'].copy()
        fellowships = ['Early Career Fellowships', 'Career Development Fellowships', 'Research Fellowships']
        for fellowship_type in fellowships:
            details = list(test_data.loc[fellowship_type])
            gender_summary[row_count] = [year, fellowship_type] + details
            row_count += 1

gender_award = pd.DataFrame.from_dict(
    dict([(k, pd.Series(v)) for k, v in gender_summary.items()])).T
gender_cols = ['f_Applications',	'f_Funded',	'f_Rate',	'f_Amount',	'm_Applications',
               'm_Funded',	'm_Rate',	'm_Amount',	'ns_Applications',	'ns_Funded',	'ns_Rate',	'ns_Amount']

gender_award.columns = ['Year', 'Type'] + gender_cols


# Adding in 2019 info
clean_data['2019'].keys()
investigators = clean_data['2019']['gender'].reset_index()
investigators = investigators[investigators['Scheme'].str.contains('Leadership')]
investigators['Type'] = [value.lstrip() for value in investigators['Scheme'] ]
investigators['Year'] = '2019'
investigators = investigators.set_index('Scheme').reset_index(drop=True)
investigators = investigators[['Year', 'Type']+gender_cols]

# Generate summary df, and map awards to categories
gender_summary = pd.concat([gender_award, investigators])

name_mapper = {'Leadership': 'L',	'Emerging Leadership Level 2': 'EL2', 'Emerging Leadership Level 1': 'EL1', 'Early Career Fellowships': 'ECF', 'Career Development Fellowships': 'CDF', 'Research Fellowships': 'RF', 'Early Career Fellowships (Overseas)': 'ECF', 'Early Career Fellowships (Australia)': 'ECF', 'Leadership Level 1': 'L', 'Leadership Level 2': 'L', 'Leadership Level 3': 'L'}

gender_summary['abb_type'] = gender_summary['Type'].map(name_mapper)

type_mapper = {'ECF': 1, 'CDF': 2, 'RF': 3, 'L': 3, 'EL2': 2, 'EL1': 1}
gender_summary['type_cat'] = gender_summary['abb_type'].map(type_mapper)


"""
Question 4: Breakdown of title (Dr/Prof) of awardees

- Classify according to grant subtype
- Strip title information from grant summary

"""

title_summary = []
grant_cols = ['Grant Type', 'Sub Type']

name_mapper = {'Leadership': 'L',	'Emerging Leadership Level 2': 'EL2',
               'Emerging Leadership Level 1': 'EL1', 'Early Career Fellowships': 'ECF', 'Career Development Fellowships': 'CDF', 'Research Fellowships': 'RF', 'Early Career Fellowships (Overseas)': 'ECF', 'Early Career Fellowships (Australia)': 'ECF'}

# Collect all but 2019
for year in clean_data.keys():
    # name of the CIA col changes each year...
    name_col = [key for key in clean_data[year]['grant_summary'].keys() if 'Name' in key][0]
    year
    
    if year != '2019':
        fellowships = ['Early Career Fellowships',
                       'Career Development Fellowships', 'Research Fellowships', 'Early Career Fellowships (Overseas)', 'Early Career Fellowships (Australia)']
        test_data = clean_data[year]['grant_summary'][[name_col] + grant_cols].copy()
        test_data = test_data[test_data['Grant Type'].isin(fellowships)]
        test_data['Type'] = test_data['Grant Type'].map(name_mapper)
        test_data['CIA_title'] = test_data[name_col].str.split(' ').str[0]

    elif year == '2019':
        fellowships = ['Leadership', 'Emerging Leadership Level 2', 'Emerging Leadership Level 1']
        test_data = clean_data[year]['grant_summary'][[name_col] + grant_cols].copy()

        test_data = test_data[test_data['Sub Type'].isin(fellowships)]
        test_data['Type'] = test_data['Sub Type'].map(name_mapper)
        test_data['CIA_title'] = test_data[name_col].str.split(' ').str[0]

    test_data['Year'] = year
    test_data.drop(grant_cols, axis=1, inplace=True)
    test_data.rename(columns={name_col: 'CIA_name'}, inplace=True)

    title_summary.append(test_data)

title_summary = pd.concat(title_summary).reset_index(drop=True)

type_mapper = {'ECF': 1, 'CDF': 2, 'RF': 3, 'L': 3, 'EL2': 2, 'EL1': 1}
title_summary['type_cat'] = title_summary['Type'].map(type_mapper)

# Calculate proportion with each title, assign levels
level_map = {'A/Pr': 2, 'Dr': 1, 'E/Pr': 4, 'Miss': 0, 'Mr': 0, 'Mrs': 0, 'Ms': 0, 'Prof': 3}
title_proportions = title_summary.groupby(['Year', 'CIA_title']).count()['Type'].reset_index()
total_maps = title_summary.groupby(['Year']).count()['Type'].to_dict()
title_proportions['total_awardees'] = title_proportions['Year'].map(total_maps)
title_proportions['proportion'] = round((title_proportions['Type'] / title_proportions['total_awardees'].astype(int) * 100), 2)
title_proportions['level'] = title_proportions['CIA_title'].map(level_map)

# # Checking out a few parameters
# for_plotting = title_summary.groupby(['Year', 'CIA_title']).count().reset_index()
# sns.barplot(x='Year', y='Type', data=for_plotting, hue='CIA_title')
# plt.legend(bbox_to_anchor=(1.5, 1.0))

# sns.barplot(data=title_proportions, x='Year', y='proportion', hue='level')
# plt.legend(bbox_to_anchor=(1.2, 1.0))


"""
Question 5: Type and discipline of funded projects

- Classify according to research area (Basic, Clinical etc)
- Collect Field of Research and attempt to match to FOR codes

"""
clean_data['2019']['grant_summary'].head()
research_area = []
research_cols = ['Broad Research Area', 'Field of Research', 'Total']

name_mapper = {'Leadership': 'L',	'Emerging Leadership Level 2': 'EL2',
               'Emerging Leadership Level 1': 'EL1', 'Early Career Fellowships': 'ECF', 'Career Development Fellowships': 'CDF', 'Research Fellowships': 'RF', 'Early Career Fellowships (Overseas)': 'ECF', 'Early Career Fellowships (Australia)': 'ECF'}

for year in clean_data.keys():
    if year != '2019':
        fellowships = ['Early Career Fellowships',
                       'Career Development Fellowships', 'Research Fellowships', 'Early Career Fellowships (Overseas)', 'Early Career Fellowships (Australia)']
        test_data = clean_data[year]['grant_summary'][['Grant Type'] + research_cols].copy()

        test_data = test_data[test_data['Grant Type'].isin(fellowships)]
        test_data['Type'] = test_data['Grant Type'].map(name_mapper)
        test_data.drop(['Grant Type'], axis=1, inplace=True)


    elif year == '2019':
        fellowships = ['Leadership', 'Emerging Leadership Level 2',
                       'Emerging Leadership Level 1']
        test_data = clean_data[year]['grant_summary'][['Sub Type'] + research_cols].copy()

        test_data = test_data[test_data['Sub Type'].isin(fellowships)]
        test_data['Type'] = test_data['Sub Type'].map(name_mapper)
        test_data.drop(['Sub Type'], axis=1, inplace=True)

    test_data['Year'] = year

    research_area.append(test_data)

research_summary = pd.concat(research_area).reset_index(drop=True)

type_mapper = {'ECF': 1, 'CDF': 2, 'RF': 3, 'L': 3, 'EL2': 2, 'EL1': 1}
research_summary['type_cat'] = research_summary['Type'].map(type_mapper)
research_summary[research_summary['Type'] == 'ECF']
## Checking out a few parameters
# for_plotting = research_summary.groupby(['Year','Broad Research Area']).count()
# sns.barplot(x='Year', y='Type', data=research_summary.groupby(
#     ['Year', 'Broad Research Area']).count().reset_index(), hue='Broad Research Area')
# plt.legend(bbox_to_anchor=(1.75, 1.0))

# sns.barplot(x='Year', y='Total', data=research_summary.groupby(['Year', 'Broad Research Area']).sum().reset_index(), hue='Broad Research Area')
# plt.legend(bbox_to_anchor=(1.75, 1.0))


# Calculate proportion with each broad field, assign levels
research_proportions = research_summary.groupby(['Year', 'Broad Research Area']).count()['Type'].reset_index()
total_maps = research_summary.groupby(['Year']).count()['Type'].to_dict()
research_proportions['total_awardees'] = research_proportions['Year'].map(total_maps)
research_proportions['proportion'] = round(
    (research_proportions['Type'] / research_proportions['total_awardees'].astype(int) * 100), 2)

sns.barplot(data=research_proportions, x='Year', y='proportion', hue='Broad Research Area')
plt.legend(bbox_to_anchor=(1.75, 1.0))

# Read in FOR map

for_codes = pd.read_excel('analysis_results/for_codes/for_summary.xlsx')
for_codes = pd.read_csv('analysis_results/for_codes/for_summary.csv', dtype=object)
# Generate dictionaries mapping different levels 
code_map = dict(zip(for_codes['label'].str.lower(), for_codes['code']))
group_map = dict(zip(for_codes['code'], for_codes['parent_group_code']))
field_map = dict(zip(for_codes['code'], for_codes['parent_field_code']))
label_map = dict(zip(for_codes['code'], for_codes['label']))

research_summary['code'] = research_summary['Field of Research'].str.lower().map(code_map)
research_summary['parent_field_code'] = research_summary['code'].map(field_map)
research_summary['parent_field_label'] = research_summary['parent_field_code'].map(label_map)

#check out what the mapped table looks like
research_summary.head(50)
research_summary.groupby(['parent_field_label', 'Year']).count()


"""
Question 7: State breakdown

- Collect Proportion awarded to each state, and % success rate from states
- Collect success rate at institutes, plot line-graph over time

"""
clean_data['2019']['Investigator Grants']['state'].keys()


state_awarded = []
# Collecting all but 2019
for year in clean_data.keys():
    if year != '2019':
        fellowships = ['ECF', 'CDF', 'RF']
        for fellowship_type in fellowships:
            test_data = clean_data[year][fellowship_type]['state']
            test_data = test_data.set_index('State and Territory').drop(
                'Total for Competitive grants')
            test_data['Year'] = year
            test_data['Type'] = fellowship_type
            state_awarded.append(test_data.reset_index())

# As 2019 does not have per-scheme breakdown, sum all other schemes per year for comparison and ignore Type
state_summary = pd.concat(state_awarded).groupby(['Year', 'State and Territory']).sum().drop('Type', axis=1)
state_summary.rename(columns={' Funded': 'Funded'}, inplace=True)
# fix funded rate (which is ruined by summing)
state_summary['Funded Rate'] = state_summary['Funded'] / state_summary['Applications']

# Adding in 2019 info
investigators = clean_data['2019']['Investigator Grants']['state']
investigators = investigators.set_index('State and Territory').drop(
    'Total for Competitive grants')
investigators['Year'] = '2019'
investigators.rename(columns={' Funded': 'Funded'}, inplace=True)

state_summary = pd.concat([state_summary.reset_index(), investigators.reset_index()])

# Check out a few parameters
# sns.lineplot(x=state_summary['Year'], y=state_summary['Funded Rate'].astype(float), hue=state_summary['State and Territory'])
# plt.legend(bbox_to_anchor=(1.75, 1.0))

# sns.lineplot(x=state_summary['Year'], y=state_summary['Applications'].astype(float), hue=state_summary['State and Territory'])
# plt.legend(bbox_to_anchor=(1.75, 1.0))

"""
Question 8: Institute breakdown

- Collect Proportion awarded to each Insititute, and % success rate
- Collect success rate at institutes, plot line-graph over time

"""
clean_data['2019']['Investigator Grants']['Administering_Institutions'].keys()


institute_awarded = []
# Collecting all but 2019
for year in clean_data.keys():
    if year != '2019':
        fellowships = ['ECF', 'CDF', 'RF']
        for fellowship_type in fellowships:
            test_data = clean_data[year][fellowship_type]['Administering_Institutions']
            test_data = test_data.set_index('Administering Institution')
            test_data['Year'] = year
            test_data['Type'] = fellowship_type
            institute_awarded.append(test_data.reset_index())

# As 2019 does not have per-scheme breakdown, sum all other schemes per year for comparison and ignore Type
institute_summary = pd.concat(institute_awarded).groupby(
    ['Year', 'Administering Institution']).sum().drop('Type', axis=1)
institute_summary.rename(columns={' Funded': 'Funded'}, inplace=True)
# fix funded rate (which is ruined by summing)
institute_summary['Funded Rate'] = institute_summary['Funded'] / \
    institute_summary['Applications']

# Adding in 2019 info
investigators = clean_data['2019']['Investigator Grants']['Administering_Institutions']
investigators = investigators.set_index('Administering Institution')
investigators['Year'] = '2019'
investigators.rename(columns={' Funded': 'Funded'}, inplace=True)

institute_summary = pd.concat(
    [institute_summary.reset_index(), investigators.reset_index()])

# # Check out a few parameters - this is hard with this dataset as (a) there are so many varibale, and (b) there is a LOT of variability
# sns.lineplot(x=institute_summary['Year'], y=institute_summary['Funded Rate'].astype(float), hue=institute_summary['Administering Institution'])
# plt.legend(bbox_to_anchor=(1.75, 1.0))

# sns.lineplot(x=institute_summary['Year'], y=institute_summary['Funded'].astype(float), hue=institute_summary['Administering Institution'])
# plt.legend(bbox_to_anchor=(1.75, 1.0))

"""
Question 9: What were the most common topics/keywords?

- Collect total keywords from successful apps in each year
- This could be visualised using a wordcloud

"""
kw_data = []

for year in clean_data.keys():
    test_data = clean_data[year]['grant_summary'].copy()
    # name of the CIA col changes each year...
    grant_cols = ['Grant Type', 'Sub Type']
    kw_cols = [col for col in test_data.columns.tolist() if 'KW' in col]
    test_data = test_data[grant_cols + kw_cols]

    if year != '2019':
        fellowships = ['Early Career Fellowships',
                       'Career Development Fellowships', 'Research Fellowships', 'Early Career Fellowships (Overseas)', 'Early Career Fellowships (Australia)']
        test_data = test_data[test_data['Grant Type'].isin(fellowships)]
        test_data['Type'] = test_data['Grant Type'].map(name_mapper)

    elif year == '2019':
        fellowships = ['Leadership', 'Emerging Leadership Level 2',
                       'Emerging Leadership Level 1']
        test_data = test_data[test_data['Sub Type'].isin(fellowships)]
        test_data['Type'] = test_data['Sub Type'].map(name_mapper)

    test_data['Year'] = year
    test_data.drop(grant_cols, axis=1, inplace=True)

    kw_data.append(test_data)

kw_summary = pd.concat(kw_data).reset_index(drop=True)

# Test a word cloud for this
# text = kw_summary[kw_summary['Year'] == '2017'][kw_cols].values
# wordcloud = WordCloud(
#     width=3000,
#     height=2000,
#     background_color='white').generate(str(text))
# fig = plt.figure(
#     figsize=(40, 30),
#     facecolor='k',
#     edgecolor='k')
# plt.imshow(wordcloud, interpolation='bilinear')
# plt.axis('off')
# plt.tight_layout(pad=0)
# plt.show()

"""
Question 10: Publication record of each level awardee for 2019

- Collect names of successful applicants in each level awarded 2019
- store as first, last, title and award type to then be able to search Scopus

"""


name_summary = []
grant_cols = ['Grant Type', 'Sub Type']

name_mapper = {'Leadership': 'L',	'Emerging Leadership Level 2': 'EL2',
               'Emerging Leadership Level 1': 'EL1', 'Early Career Fellowships': 'ECF', 'Career Development Fellowships': 'CDF', 'Research Fellowships': 'RF', 'Early Career Fellowships (Overseas)': 'ECF', 'Early Career Fellowships (Australia)': 'ECF'}

# Collect all but 2019
for year in clean_data.keys():
    # name of the CIA col changes each year...
    name_col = [key for key in clean_data[year]
                ['grant_summary'].keys() if 'Name' in key][0]

    if year != '2019':
        fellowships = ['Early Career Fellowships',
                       'Career Development Fellowships', 'Research Fellowships', 'Early Career Fellowships (Overseas)', 'Early Career Fellowships (Australia)']
        test_data = clean_data[year]['grant_summary'][[
            name_col] + grant_cols].copy()

        test_data = test_data[test_data['Grant Type'].isin(fellowships)]
        test_data['Type'] = test_data['Grant Type'].map(name_mapper)
        test_data['CIA_title'] = test_data[name_col].str.split(' ').str[0]

    elif year == '2019':
        fellowships = ['Leadership', 'Emerging Leadership Level 2',
                       'Emerging Leadership Level 1']
        test_data = clean_data[year]['grant_summary'][[
            name_col] + grant_cols].copy()

        test_data = test_data[test_data['Sub Type'].isin(fellowships)]
        test_data['Type'] = test_data['Sub Type'].map(name_mapper)
        test_data['CIA_title'] = test_data[name_col].str.split(' ').str[0]

    test_data['Year'] = year
    test_data.drop(grant_cols, axis=1, inplace=True)
    test_data.rename(columns={name_col: 'CIA_name'}, inplace=True)

    name_summary.append(test_data)

name_summary = pd.concat(name_summary).reset_index(drop=True)

name_summary['name'] = name_summary['CIA_name'].str.split(' ').str[1:].str.join(' ')

type_mapper = {'ECF': 1, 'CDF': 2, 'RF': 3, 'L': 3, 'EL2': 2, 'EL1': 1}
name_summary['type_cat'] = name_summary['Type'].map(type_mapper)

# Save all to excel
data_frames = [awarded_summary, gender_summary, title_summary, title_proportions, research_summary, research_proportions, state_summary, institute_summary, kw_summary, name_summary]
sheetnames= ['total_rates', 'per_gender', 'CIA_title', 'title_proportion_per_year', 'field_of_research', 'broad_research_proportions', 'state_summary', 'institute_summary', 'key_word_summary', 'name_summary']

FileHandling.df_to_excel(data_frames=data_frames, sheetnames=sheetnames, output_path=f'{output_folder}summary_stats.xlsx')
