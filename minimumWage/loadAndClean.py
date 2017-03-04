#!/usr/bin/env python3

from datetime import date

import pandas as pd

def dateConverter(month):
    def buildDateFromYear(year):
        return date(year, month, 1)
    return buildDateFromYear


df = pd.read_csv('unemployment.csv')

columns={
    'Jan':'1', 
    'Feb':'2', 
    'Mar':'3', 
    'Apr':'4', 
    'May':'5', 
    'Jun':'6',
    'Jul':'7', 
    'Aug':'8', 
    'Sep':'9', 
    'Oct':'10', 
    'Nov':'11', 
    'Dec':'12'
}

df.rename(
    inplace=True,
    columns=columns
)


# We're only using minimum wage data from 1978 onward 
df = df[df.Year >= 1978]

dataFrames = []
for month in columns.values():
    df2 = pd.DataFrame(df[['Year', month]])
    df2.rename(inplace=True, columns={month:'Unemployment'})
    df2['Date'] = df2['Year'].apply(dateConverter(int(month)))
    df2 = df2[['Date', 'Unemployment']]
    df2 = df2.set_index('Date')
    dataFrames.append(df2)
    



