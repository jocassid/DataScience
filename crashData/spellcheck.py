#!/usr/bin/env python3

from cmd import Cmd
from collections import Counter
from csv import DictReader, DictWriter
from re import compile as re_compile
from sqlite3 import connect
from statistics import mean
from string import ascii_lowercase, punctuation
from sys import stderr

from nltk import word_tokenize

from dictionary import Dictionary


PUNCTUATION = set(punctuation)


def validate_word(word):
    if word is None:
        raise ValueError("Word cannot be None")
        
    word = word.strip()
    if word == '':
        raise ValueError("Word cannot be empty string or all whitespace")


def contains_digits(text):
    for c in text:
        if c.isdigit():
            return True
    return False

                            
def split_generator(word, validate=True):
    if validate:
        validate_word(word)
    if len(word) == 1:
        raise ValueError("Can't split a 1 character word")
    for i in range(len(word) - 1):
        yield (word[:i+1], word[i+1:])
        

def delete_generator(word, validate=True):
    if validate:
        validate_word(word)
    if len(word) == 1:
        raise StopIteration
    for i in range(len(word)):
        if i ==0:
            yield word[1:]
            continue
        yield word[:i] + word[i+1:] 
 
 
def transpose_generator(word, validate=True):
    if validate:
        validate_word(word)
        
    if len(word) == 1:
        yield word
        
    chars = [c for c in word]

    for i in range(len(word)-1):
        # swap 2 characters
        temp = chars[i]
        chars[i] = chars[i+1]
        chars[i+1] = temp
        
        # yield the result
        yield ''.join(chars)
        
        # swap the characters back
        temp = chars[i]
        chars[i] = chars[i+1]
        chars[i+1] = temp


def validate_alphabet(alphabet):
    if alphabet is None:
        raise ValueError("alphabet can't be None")
        
    if not isinstance(alphabet, set):
        raise ValueError("alphabet must be a set")
        
    if alphabet == set():
        raise ValueError("alphabet can't be empty set")    


def replace_generator(word, alphabet, validate=True):
    if validate:
        validate_word(word)
               
    validate_alphabet(alphabet)

    mutable_word = list(word)
    for i in range(len(mutable_word)):
        for c in alphabet:
            
            temp = mutable_word[i] 
            if temp == c:
                continue
                
            mutable_word[i] = c
            candidate = ''.join(mutable_word) 
            yield candidate
            mutable_word[i] = temp
        

def inserts_generator(word, alphabet, validate=True):
    if validate:
        validate_word(word)
    
    validate_alphabet(alphabet)
    
    mutable_word = list(word)
    for i in range(len(mutable_word) + 1):
        for c in alphabet:
            mutable_word.insert(i, c)
            candidate = ''.join(mutable_word)
            mutable_word.pop(i)
            yield candidate

# https://norvig.com/spell-correct.html

# aspell-python-py3
# CyHunspell (uses same library as LibreOffice)

class DictionaryError(RuntimeError):
    pass


class WordRecord(object):
    """represents a record in the words table of the dictionary"""
    def __init__(self, word, occurances=1):
        self.word = word
        self.occurances = occurances
        
    def __eq__(self, rhs):
        if type(self) != type(rhs):
            return False
        if self.word != rhs.word:
            return False
        return self.occurances == rhs.occurances

class Dictionary(object):
    """sqlite based dictionary"""
    
    # WORDS_WORD = 0 
    # WORDS_OCCURANCES = 1
    # 
    # STATS_WORDS_SCANNED = 0
    
    TABLE_DEFS = [
        """CREATE TABLE IF NOT EXISTS words(
                word TEXT NOT NULL UNIQUE,
                occurances INTEGER NOT NULL DEFAULT (1))""",
        """CREATE TABLE IF NOT EXISTS stats(
                words_scanned INTEGER NOT NULL DEFAULT(0))""",
        """CREATE TABLE IF NOT EXISTS skips(
                word TEXT NOT NULL UNIQUE)""",
    ]
    
    def __init__(self, db_file):
        self.conn = connect(db_file)
        self.cursor = self.conn.cursor()
        self.words_scanned = 0
        self.initialize()
        
    def initialize(self):
        for table_def in self.TABLE_DEFS:
            self.cursor.execute(table_def)
        self.conn.commit()
        self.initialize_stats()
        
    def initialize_stats(self):
        sql = "SELECT words_scanned FROM stats ORDER BY words_scanned DESC"
        self.cursor.execute(sql)
        records = self.cursor.fetchall()
        if len(records) == 1:
            record = records[0]
            self.words_scanned = record[0]
            return
            
        if len(records) == 0:
            sql = "INSERT INTO stats(words_scanned) VALUES (0)"
            self.cursor.execute(sql)
            self.conn.commit()
            return
            
        raise RuntimeError("more than 1 stats record")

    def __enter__(self):
        self.conn.__enter__()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.conn.__exit__(exc_type, exc_val, exc_tb)
    
    def add(self, word, occurances=1):
        if word in self:
            self.add_occurance(word)
            return False
        sql = "INSERT INTO words(word, occurances) VALUES(?, ?)"
        self.cursor.execute(sql, (word, occurances))
        self.conn.commit()
        return True
        
    def probability(self, word):
        word_record = self[word]
        if self.words_scanned <= 0:
            return 1
        return 1.0 * word_record.occurances / self.words_scanned 
            

    def __getitem__(self, word):
        if not isinstance(word, str):
            raise TypeError("key should be a string")
        sql = "SELECT word, occurances FROM words WHERE word = ?"
        self.cursor.execute(sql, (word,))
        record = self.cursor.fetchone()
        if record is None:
            raise KeyError("'{}' not found".format(word))
        return WordRecord(record[0], record[1])

    def __contains__(self, word):
        try:
            self[word]
        except KeyError:
            return False
        return True
        
    def add_occurance(self, word):
        sql = "UPDATE words SET occurances = occurances + 1 WHERE word = ?"
        self.cursor.execute(sql, (word.lower(),))
        self.conn.commit()
        
    def in_skips(self, word):
        sql = "SELECT * FROM skips WHERE word = ?"
        self.cursor.execute(sql, (word, ))
        return bool(self.cursor.fetchmany())
        
    def add_skip(self, word):
        sql = "INSERT INTO skips(word) VALUES (?)"
        self.cursor.execute(sql, (word,))
        self.conn.commit()
    
class InteractiveReplace(Cmd):     
    def __init__(self, word_in, spellchecker):
        super(InteractiveReplace, self).__init__()
        self.word_in = word_in
        self.prompt = "'{}': ".format(word_in)
        self.spellchecker = spellchecker
        self.candidates = []
        self.page = 0
        self.word_out = None
        self.action = None

    def do_add(self, arg):
        """Add word to dictionary"""
        if not self.spellchecker.dictionary.add(self.word_in):
            raise RuntimeError(
                "Unable to add {} to dictionary".format(self.word_in))
        self.word_out = self.word_in
        self.action = 'add'
        return True

    def do_list(self, arg):
        """List possible candidates"""
        self.candidates = list(
            self.spellchecker.find_candidates(self.word_in))
        if not self.candidates:
            print('No candidates found')
        for i, candidate in enumerate(self.candidates):
            print("{:>4}. {}".format(i, candidate))
            
    def do_skip(self, arg):
        self.spellchecker.dictionary.add_skip(self.word_in)
        self.word_out = None
        self.action = 'skip'
        return True
        
    def do_change(self, arg):
        while True:
            if arg and arg[0]:
                word_out = arg[0]
            else:
                word_out = input('Enter change: ')
            confirm = input("Change '{}' to '{}' (y/n): ".format(
                self.word_in, 
                word_out))
            if confirm.lower() == 'y':
                break
        self.spellchecker.dictionary.add(word_out)
        self.word_out = word_out
        self.action = 'correct'
        return True
        
    
        
            
        

class SpellChecker:
    
    default_alphabet = ascii_lowercase

    def __init__(
            self, 
            dictionary,
            interactive=False,
            alphabet=default_alphabet):
        
        self.dictionary = dictionary 
        self.interactive = interactive
        self.alphabet = set(alphabet)
        self.words_not_found = Counter()
        self.skips = set()

    @staticmethod
    def one_edit_away(word):
        """yields a tuple of two words or a word"""
        for word_tuple in split_generator(word):
            yield
        # splits = list(split_generator(word))
        # splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        # #print('{} splits: {}'.format(word, splits))ts))
        
    def find_candidates(self, word, number_candidates=1):
        if len(word) > 1:
            for candidate, candidate2 in split_generator(word):
                if candidate not in self.dictionary:
                    continue
                if candidate2 not in self.dictionary:
                    continue
                print("Split", candidate, candidate2)
                
                total = self.dictionary.probability(candidate)
                total += self.dictionary.probability(candidate2) 
                probability = total / 2.0
                yield probability, candidate, candidate2
                
            for candidate in delete_generator(word):
                if candidate not in self.dictionary:
                    continue
                print("delete", candidate)
                probability = self.dictionary.probability(candidate)
                yield probability, candidate, None
                
            for candidate in transpose_generator(word):
                if candidate not in self.dictionary:
                    continue
                print("transpose", candidate)
                probability = self.dictionary.probability(candidate)
                yield probability, candidate, None
                
            for candidate in replace_generator(word, self.alphabet):
                if candidate not in self.dictionary:
                    continue
                print("replace", candidate)
                probability = self.dictionary.probability(candidate)
                yield probability, candidate, None
                                            
        return "A suffusion of yellow"

    def check(self, word):
        new_characters = set(word.lower()) - self.alphabet
        if new_characters:
            self.alphabet |= new_characters
            
        if word in PUNCTUATION:
            return word
        if word in self.dictionary:
            self.dictionary.add_occurance(word)
            return word
        if self.interactive:
            if self.dictionary.in_skips(word):
                return word
            return self.interactive_replace(word)
        return self.automatic_replace(word)
            
    def interactive_replace(self, word):
        cmd = InteractiveReplace(word, self)
        cmd.cmdloop()
        if cmd.action == 'skip':
            self.skips.add(word)
        return cmd.word_out
    
    def automatic_replace(self, word):
        raise NotImplementedError("Implement automatic_replace")
        # print("{} not found".format(word))
        # self.words_not_found.update([word])
# 
        # for candidate in self.find_candidates(word):
            # print(candidate)
# 
        # "Most probable spelling correction for word."
        # return word



    # def dump_words_not_found



