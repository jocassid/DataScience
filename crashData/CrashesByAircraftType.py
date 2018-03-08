#!/usr/bin/env python3

from csv import DictReader, writer, QUOTE_NONNUMERIC
from collections import Counter, namedtuple

TypeCrashes = namedtuple('TypeCrashes', ['type', 'crashes'])

def getAircraftTypes():
    with open('cleansedCrashData.csv', 'r') as csvFile:
        reader = DictReader(csvFile)
        for row in reader:
            yield row['Type']
            
def writeSortedListToCSV(sortable, key, filename, reverse=False): 
    sortedBy = sorted(sortable, key=key, reverse=reverse)
    with open(filename, 'w') as outCsv:
        csvWriter = writer(outCsv, quoting=QUOTE_NONNUMERIC)
        csvWriter.writerow(['type', 'crashes'])
        for row in sortedBy:
            csvWriter.writerow(row)
            
def main():
    
    crashesByType = Counter(getAircraftTypes())
    
    sortable = [TypeCrashes(key, crashesByType[key]) for key in crashesByType]
    
    writeSortedListToCSV(
        sortable, 
        lambda x: x.crashes,
        'TypesByNumberOfCrashes.csv',
        True)
    
    writeSortedListToCSV(
        sortable,
        lambda x: x.type,
        'TypesAlphabetically.csv')

    
                                                                 

if __name__ == '__main__':
    main()
