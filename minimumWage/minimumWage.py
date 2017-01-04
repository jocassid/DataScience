#!/usr/bin/env python3


# Standard library imports
from datetime import date
from dateutil.relativedelta import relativedelta
from csv import reader

from matplotlib.pyplot import show
from pandas import DataFrame, date_range, Series, Timestamp, concat


# Unemployment data from - http://data.bls.gov/pdq/SurveyOutputServlet
# MiniumWage data from - https://www.dol.gov/whd/minwage/chart.htm



MINIMUM_WAGE_HISTORY = [
    (Timestamp('1978-01-01'), 2.65),
    (Timestamp('1979-01-01'), 2.9),
    (Timestamp('1980-01-01'), 3.10),
    (Timestamp('1981-01-01'), 3.35),
    (Timestamp('1990-04-01'), 3.80), 
    (Timestamp('1991-04-01'), 4.25),
    (Timestamp('1996-10-01'), 4.75),
    (Timestamp('1997-09-01'), 5.15),
    (Timestamp('2007-07-24'), 5.85),
    (Timestamp('2008-07-24'), 6.55),
    (Timestamp('2009-07-24'), 7.25)
]


def loadMinimumWageData(dateIndex):
    
    minWageHistory = MINIMUM_WAGE_HISTORY.copy()
    minWageData = Series(name='minimumWage')
    histWage = None
    nextHistDate = None
    nextHistWage = None
    
    for indexDate in dateIndex:
        
        if nextHistDate is None:
            nextHistDate, nextHistWage = minWageHistory.pop(0)
            
        if indexDate >= nextHistDate:
            histWage = nextHistWage
            
            if len(minWageHistory) > 0:
                nextHistDate, nextHistWage = minWageHistory.pop(0)
        
        minWageData[indexDate] = histWage
        
    return minWageData


def loadUnemploymentData(csvFilename):
    
    unemploymentData = Series(name='unemployment')
    
    with open(csvFilename, 'r') as inFile:
        csvReader = reader(inFile)
        for i, row in enumerate(csvReader):
            
            # skip header row
            if i == 0:
                continue

            # skip rows with incorrect number of items
            if len(row) != 13:
                print('Invalid row %d' % i+1)
                continue
                
            year = int(row[0])
            if year < 1978:
                continue
            
            for j, field in enumerate(row[1:]):
                if field.strip() == '':
                    continue
                
                try:
                    unemploymentData[Timestamp(date(year, j+1, 1))] = \
                        float(field)
                except ValueError:
                    print("field was '%s'" % field)
                    
    return unemploymentData


def loadData():
                   
    dateIndex = date_range(start='1978-01-01', end='2016-01-01', freq='MS')

    minimumWageData = loadMinimumWageData(dateIndex)

    unemploymentData = loadUnemploymentData('unemployment.csv') 

    df = DataFrame(minimumWageData)
    df['unemployment'] = unemploymentData
    return df


def basicPlot():
    df = loadData()
    #print(df)
    df.plot()
    show()
    return df

def getCorrelation(dataframe):
    corr = dataframe.corr()
    return corr['minimumWage']['unemployment']

if __name__ == '__main__':
    
    df = basicPlot()
    print(
        'correlation of entire set'.ljust(30), 
        '% .3f' % getCorrelation(df))
    #df.to_csv('allData.csv')
    
    
    monthsBeforeAfter = 3
    for wageIncrDate, wage in MINIMUM_WAGE_HISTORY[1:]:
        startDate = wageIncrDate - relativedelta(months=monthsBeforeAfter)
        endDate = wageIncrDate + relativedelta(months=monthsBeforeAfter)
        
        temp = df.loc[startDate:endDate]
        print(wageIncrDate.strftime('%Y-%m-%d').ljust(30), 
            '% .3f' % getCorrelation(temp))

        



    
