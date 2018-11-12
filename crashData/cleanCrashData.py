#!/usr/bin/env python3

from argparse import ArgumentParser
from collections import Counter
from csv import DictReader, DictWriter
from re import compile as re_compile
from string import ascii_letters
from sys import stderr

from nltk import word_tokenize

from spellcheck import contains_digits, Dictionary, SpellChecker

class ModelNumberClassifier(object):
    pass

class CrashDataCleaner(object):

    FIELD_ORDER = ['Number', 'collisionWith', 'Date', 'Time', 'Location',
        'Military', 'Operator', 'Manufacturer', 'Type', 'Variant',
        'category', 'Aboard', 'Fatalities', 'Ground', 'Route', 'Summary']

    digit_regex = re_compile(r'\d')

    def __init__(
            self, 
            spellchecker):
        self.row_counter = 0
        self.spellchecker = spellchecker

    @staticmethod
    def is_collision(row):
        summary = row.get('Summary', '').lower()
        if '/' not in row.get('Type', ''):
            return False
        if 'collision' in summary:
            return True
        if 'mid-air' in summary:
            return True
        return False

    def split_collision_rows(self, row_generator):
        """Determines if the Row is for a collision and splits the row in two"""
        for row in row_generator:
            if self.is_collision(row):
                yield row
                yield self.split_collision_row(row)                           
            yield row

    @staticmethod
    def split_value(value):
        pieces = value.split('/')
        pieces_length = len(pieces)
        if pieces_length == 1:
            return value, value
        if pieces_length == 2:
            return pieces[0], pieces[1]
        
                    
            
            
            return value, value
        if str(value).count('/') == 1:
            pieces = value.split('/')
            
        return value, value

    def split_collision_row(self, row_in):
        
        type1, type2 = self.split_value(row_in['Type'])
        operator1, operator2 = self.split_value(row_in['Operator'])
        
        new_row_number = self.next_row_number() 
        new_row = {
            'Number': new_row_number,
            'summary': row_in['Summary'],
            'Type': type2,
            'Operator': operator2,
            'CollisionWith': row_in['Number']
        
        }
        
        row_in['Type'] = type1
        row_in['Operator'] = type2
        row_in['CollisionWith'] = new_row_number
        return new_row

    def clean(self, row):
        operator = row.get('Operator', '')
        if operator.startswith('Military - '):
            row['Military'] = True
            row['Operator'] = operator.replace('Military - ', '')
        row = self.get_manufacturer_and_type(row)
        return row

    def get_words(self, text):
        for word in word_tokenize(text):
            if '/' not in word:
                yield word
                continue
            for i, piece in enumerate(word.split('/')):
                yield piece
                if i > 0:
                    yield '/'

    def get_manufacturer_and_type(self, row_in):

        aircraft_type = row_in['Type'].strip()
        print('aircraft_type:', aircraft_type)
        if aircraft_type.endswith(' (airship)'):
            aircraft_type = aircraft_type[:-10]

        words = []
        for word_in in self.get_words(aircraft_type):
            if contains_digits(word_in):
                words.append(word_in)
                continue
            word_out = self.spellchecker.check(word_in)
            words.append(word_out)
            
        

            # words.append(spellChecker.check_and_replace(word))
            #print("words", words)

        # manufacturer = None
        # for mfr in MANUFACTURERS:
            # if aircraft_type.lower().startswith(mfr.lower()):
                # manufacturer = mfr
                # aircraft_type = aircraft_type[len(mfr):].strip()
                # break
        # if manufacturer is None:
            # # print('No manufacturer found in {}'.format(aircraft_type), file=stderr)
            # pass
            #
        # self.type = aircraft_type
        # self.manufacturer = manufacturer
        return row_in

    def next_row_number(self):
        next = self.row_counter
        self.row_counter += 1
        return next

    def rows_from_csv(self, csv_file):
        """Generator returns Row objects from csv"""
        reader = DictReader(csv_file)
        for csv_row in reader:
            csv_row['Number'] = self.next_row_number()
            yield csv_row

    def run(self, input_filepath, output_filepath):
        with open(input_filepath, 'r') as csv_in, \
                open(output_filepath, 'w') as csv_out:

            self.row_counter = 0
            fieldnames = self.FIELD_ORDER \
                + ['Registration', 'Flight #', 'cn/In']

            # Setup writer
            csvWriter = DictWriter(csv_out, fieldnames=fieldnames)
            csvWriter.writeheader()
            
            for i, row in enumerate(
                    self.split_collision_rows(
                        self.rows_from_csv(csv_in))):
                if i > 0:
                    print('=' * 80)
                print("IN  {0:> 4}: {1}".format(i, row))
                print('-' * 80)
                row = self.clean(row)
                print("OUT {0:> 4}: {1}".format(i, row))
                    


        #for i, row in enumerate(
                #CrashDataCleaner.split_collision_rows(
                    #rows_from_csv(csv_in)
                #)
            #):
            #print("row before:", row)
            #cleaner.clean(row)
            #print("row after:", row)
            #if i > -1:
                #break
            #csvWriter.writerow(row.to_dict())


        # word_freq = Counter()
        #
        # for row in split_collision_rows(reader):
            # words = []
            # for word in row.type.split(' '):
                # if not word:
                    # continue
                # if contains_digits(word):
                    # continue
                # words.append(word)
            # if not words:
                # continue
            # print(words)
            # word_freq.update(words)
        #
        # with open('word_freq.txt', 'w') as freq_file:
            # for word, freq in word_freq.items():
                # freq_file.write('{},{}\n'.format(freq, word))

def main(args):
    # with Dictionary('aircraft.sqlite') as dictionary:
        # print('dictionary is', dictionary)
        # spellchecker = SpellChecker(dictionary, True) 
        # cleaner = CrashDataCleaner(spellchecker)
        # cleaner.run(
            # 'crashData.csv',
            # 'cleansedCrashData.csv',
        # )

if __name__ == '__main__':
    parser = ArgumentParser(description='Clean aircraft crash data')
    parser.add_argument(
        "input_file",
        nargs='?',
        help="Input file.  If not specified data is read from stdin")
    parser.add_argument(
        "output_file",
        nargs='?',
        help="Output file.  If not specified data is writtend to stdout")
    main(parser.parse_args())

