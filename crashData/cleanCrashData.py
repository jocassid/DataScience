#!/usr/bin/env python3

from collections import Counter
from csv import DictReader, DictWriter
from re import compile
from string import ascii_letters
from sys import stderr

from nltk import word_tokenize

from HtmlOutput import HtmlOutput
from spellcheck import contains_digits, CrudeWordList, SpellChecker

# This isn't an exhaustive list
MANUFACTURERS = set([
    'Aerospatiale', 'Aerostar', 'Agusta',
    'Airbus', 'Airspeed', 'Armstrong-Whitworth',
    'Antonov', 'Arado', 'Arava',
    'Armstrong Whitworth', 'Avro', 'BAC',
    'Beech', 'Beechcraft', 'Bell',
    'Breguet', 'Boeing', 'Bristol',
    'British Aerospace', 'Britten-Norman', 'CASA',
    'Canadair', 'Cessna', 'Consolidated', 'Convair',
    'Curtiss', 'Curtiss-Wright', 'Dassault', 'De Havilland',
    'Dornier', 'Douglas', 'Embraer', 'Eurocopter',
    'Farman', 'Fairchild', 'Fokker', 'Ford', 'Grumman', 'Handley Page',
    'Hawker',
    'Hawker Siddeley', 'Junkers', 'Ilyushin', 'Latecoere', 'Learjet', 'Let',
    'Lockheed', 'McDonnell Douglas', 'North American', 'Piper', 'Rockwell',
    'Saab',
    'Savoia Marchetti', 'Short', 'Sikorsky', 'Sud Aviation',
    'Swearingen', 'Tupolev', 'Vickers', 'Yakovlev', 'Zeppelin'])


word_list = CrudeWordList()
word_list.load_from_file('word_list.txt')
spellChecker = SpellChecker(word_list)

class Row(object):
    def __init__(self):
        self.csv_row = None
        self.type = None
        self.manufacturer = None
        self.number = None
        self.summary = None
        self.collision_with = None
        self.operator = None
        self.military = False
        self.date = None
        self.time = None
        self.location = None

    def from_dict(self, a_dict):
        self.csv_row = a_dict
        self.type = a_dict['Type']
        self.summary = a_dict['Summary']
        self.operator = a_dict['Operator']
        self.military = a_dict.get('Military', False)
        self.date = a_dict['Date']
        self.collision_with = a_dict.get('collisionWith', None)
        self.time = a_dict['Time']
        self.location = a_dict['Location']

    def to_dict(self):
        return {
            'Number': self.number,
            'Type': self.type,
            'Summary': self.summary,
            'Operator': self.operator,
            'Military': self.military,
            'Date': self.date,
            'collisionWith': self.collision_with,
            'Time': self.time,
            'Location': self.location,
        }

    def __str__(self):
        return "{}: {}".format(self.number, self.to_dict())

    def is_collision(self):
        summary = self.summary.lower()
        if '/' not in self.type:
            return False
        if 'collision' in summary:
            return True
        if 'mid-air' in summary:
            return True
        return False

    @staticmethod
    def split_value(value):
        if str(value).count('/') == 1:
            pieces = value.split('/')
            return pieces[0], pieces[1]
        return value, value

    def split_collision_row(self):
        new_row = Row()

        new_row.csv_row = self.csv_row
        new_row.summary = self.summary

        new_row.type, self.type = Row.split_value(self.type)
        new_row.operator, self.operator = Row.split_value(self.operator)

        new_row.number = self.number + 1

        self.collision_with = new_row.number
        new_row.collision_with = self.number

        return new_row

    def clean(self):
        if self.operator.startswith('Military - '):
            self.military = True
            self.operator = self.operator.replace('Military - ', '')
        self.get_manufacturer_and_type()

    def get_words(self, text):
        for word in word_tokenize(text):
            if '/' not in word:
                yield word
            for i, piece in enumerate(word.split('/')):
                yield piece
                if i > 0:
                    yield '/'

    def get_manufacturer_and_type(self):

        aircraft_type = self.type.strip()
        if aircraft_type.endswith(' (airship)'):
            aircraft_type = aircraft_type[:-10]

        words = []
        for word in self.get_words(aircraft_type):
            if contains_digits(word):
                words.append(word)
                continue
            words.append(spellChecker.check_and_replace(word))
            break
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


def rows_from_csv(csv_path):
    """Generator returns Row objects from csv"""
    with open(csv_path, 'r') as csv_file:
        reader = DictReader(csv_file)
        for csv_row in reader:
            row = Row()
            row.from_dict(csv_row)
            yield row

def split_collision_rows(row_generator):
    """Determines if the Row is for a collision and splits the row in two"""
    i = -1
    for row in row_generator:
        i += 1
        row.number = i
        # print(row)

        if not row.is_collision():
            yield row
            continue

        new_row = row.split_collision_row()
        i += 1

        yield row
        yield new_row


def main():

    FIELD_ORDER = ['Number', 'collisionWith', 'Date', 'Time', 'Location',
        'Military', 'Operator', 'Manufacturer', 'Type', 'Variant',
        'category', 'Aboard', 'Fatalities', 'Ground', 'Route', 'Summary']

    with open('cleansedCrashData.html', 'w') as htmlOutFile, \
            open('cleansedCrashData.csv', 'w') as csvOutFile:

        csvWriter = DictWriter(
            csvOutFile,
            fieldnames=FIELD_ORDER + ['Registration', 'Flight #', 'cn/In'])
        csvWriter.writeheader()

        htmlOut = HtmlOutput(FIELD_ORDER)
        htmlOut.setFile(htmlOutFile)

    
        for i, row in enumerate(
                split_collision_rows(
                    rows_from_csv('crashData.csv'))):
            row.clean()
            if i > -1:
                break
            htmlOut.write(row.to_dict())
            csvWriter.writerow(row.to_dict())

        htmlOut.finish()

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





if __name__ == '__main__':
    main()
