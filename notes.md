# Draft_Investigating the Investigator Grants 2019 notes
 
## 2019-08-29

- Looking at some of the useful things on Twitter
  - https://twitter.com/GaetanBurgio/status/1164479350483197952
  - https://twitter.com/Nickii_dlm/status/1164736390229217281
  - https://twitter.com/whereisdaz/status/1166884014898040833
  - https://twitter.com/AliciaOshlack/status/1166894722679312384
  - https://twitter.com/GaetanBurgio/status/1166870461898088448
  - https://twitter.com/MVEG001/status/1166894827314696192
  - https://twitter.com/meghanbohren/status/1166875953026363392
  - https://twitter.com/K_Sheldrick/status/1166908265743015936
  - https://twitter.com/dj_keating/status/1166886599482724352
  - https://twitter.com/Gianina_Natoli/status/1166931285001949184/photo/1
  - https://twitter.com/DrAdrienneOneil/status/1164837886258057216
  - https://twitter.com/GaetanBurgio/status/1164479350483197952


## Python resources

- retrieve author information from Scopus (to profile num. papers, potentially authorship ranked list) see examples [here](https://pybliometrics.readthedocs.io/en/stable/examples/AuthorSearch.html) and [here](https://pybliometrics.readthedocs.io/en/stable/examples/AuthorRetrieval.html) using [Pybliometrics](https://github.com/pybliometrics-dev/pybliometrics)


### initial_cleanup

**Input**: raw data from NHMRC website
**Output**: cleaned datasets for each year
**Prerequisites**:  None
**Language/interpreter**  python

## 2019-09-04 Testing Scival

- Looking at the SciVal interface, it is possbile to manually upload a list of no more than 1000 researchers
- Format for upload file should be separated by ';' and contain at minimum "Author" and "Affiliation" columns.
- Can also add to heirarchy using 'Level 1', 'Level 2' etc - in this case, lets just define this as the year
- Generate test script to output this data in "scival_test.py"


## 2019-09-20 Writing

- Noticed some disparities in the total number of proposals and total funding amount between the gender stats and overall funding (theoretically the overall should be the sum of the gender breakdown)
- Level 3 gender split is missing for 2019 - issue here is that the Leadership levels were maintained separately (and therefore were not mapped to the right type_cat) - added this in the summary_stats workflow, then re-ran the plotting for gender

- Also looking at wordcloud generator - not sure if this is currently by frequency?
- Updated using code snippet from https://stackoverflow.com/questions/38465478/wordcloud-from-data-frame-with-frequency-python - also looked at the top 5 most common terms and this was consistently health, disease, cancer and biology


## 2019-09-25 updating plots with legend

- Need to add a way to distinguish the left and right axis (what is plotted on each) - this is tricky with the legend position as there is not enough room on the right for a second legend.
- Two ideas: (1) add "Barplot: " and "Lineplot: " to the axis titles, or (2) extend the y-axis to create space for a second legend

## 2019-10-01 Establish behind scenes post

- Copied notes, gitignore, raw_data and analysis_scripts from "Investigating the investigators" post (30/09/19)
- Also added new folders - analysis_results, notebooks, images
- Setup new script for testing panel functionality

### panel_gender

**Input**: summary_stats.xlsx
**Output**: notebook with panel figure
**Prerequisites**:  summary_stats.py
**Language/interpreter**  python

- Idea is to create a notebook with panel visualisation inbuilt to the be able to display gender proportion according to level
- This will require reworking some of the plotting elements from the original plot_gender script
- 