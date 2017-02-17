#!/usr/bin/env python3

import pandas as pd

df = pd.read_csv('unemployment.csv')

MONTH_COLUMNS = [
    'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
]

# We're only using minimum wage data from 1978 onward 
df = df[df.Year >= 1978]
.
# slice out Year and a month column
yearAndJanuary = df[['Year', 'Jan']]


