#!/usr/bin/env python3

from csv import DictReader

ALL_WORDS = set()
WORDS_BY_LINE = []

with open('TypesAlphabetically.csv', 'r') as inFile:
    reader = DictReader(inFile)
    for i, row in enumerate(reader):
        wordsOnLine = list(
                filter(
                    lambda x: len(x)>0,
                    row['type'].split(' ')))
        print(wordsOnLine)
        if i > 200:
            break
