#!/usr/bin/env python3

from pandas import merge, read_csv, to_numeric

import numpy as np
import pandas as pd


# state population info from
# http://www.census.gov/data/tables/2016/demo/popest/state-total.html

# electoral votes info from
# https://www.archives.gov/federal-register/electoral-college/allocation.html


statePopDF = read_csv('statePopulations.csv')
# Puerto Rico would be the 30th largest state
# Washington DC has more inhabitants than Vermont & Wyoming

electoralDF = read_csv('electoralVotes.csv')
# electoralDF = electoralDF.fillna(value=0)


df = merge(
    electoralDF, 
    statePopDF, 
    how='outer',
    left_on='State', 
    right_on='Geographic Area')

