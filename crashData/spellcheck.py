#!/usr/bin/env python3

from cmd import Cmd
from collections import Counter
from csv import DictReader, DictWriter
from re import compile as re_compile
from sqlite3 import connect
from statistics import mean
from string import ascii_lowercase, punctuation
from sys import stderr

# from nltk import word_tokenize

from dictionary import Dictionary
from tokenizer import Tokenizer
from subsequence_group import subsequence_group


PUNCTUATION = set(punctuation)


def validate_word(word):
    if word is None:
        raise ValueError("Word cannot be None")
        
    word = word.strip()
    if word == '':
        raise ValueError("Word cannot be empty string or all whitespace")


def contains_digits(text):
    if not text:
        return False
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
            return False
        for i, candidate in enumerate(self.candidates):
            print("{:>4}. {}".format(i+1, candidate))
        selection = input("select value or press enter: ")
        if not selection:
            return False # stay in command loop
        try:
            selection = int(selection)
        except ValueError:
            print("invalid selection")
            return False
        self.word_out = " ".join([w for w in self.candidates[1:] if w])
        return True
        
            
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
    roman_numeral_characters = set('MCLXVI')

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
        self.skip_next = False

    @staticmethod
    def one_edit_away(word):
        """yields a tuple of two words or a word"""
        for word_tuple in split_generator(word):
            yield
        # splits = list(split_generator(word))
        # splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        # #print('{} splits: {}'.format(word, splits))ts))
        
    def is_roman_numeral(self, word):
        return not bool(set(word) - self.roman_numeral_characters)
        
    def find_candidates(self, word, number_candidates=1):
        """yields a tuple of probability, word1, word2"""        
        for candidate in inserts_generator(word, self.alphabet):
            if candidate not in self.dictionary:
                continue
            print("insert", candidate)
            probability = self.dictionary.probability(candidate)
            yield probability, candidate, None        
        
        if len(word) <= 1:
            raise StopIteration()
            
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
                
    def check(self, word, next_word=None):
        
        if self.skip_next:
            self.skip_next = False
            return None
            
        if not word:
            return word
            
        new_characters = set(word.lower()) - self.alphabet
        if new_characters:
            self.alphabet |= new_characters
            
        if word in PUNCTUATION:
            return word
            
        if word in self.dictionary:
            self.dictionary.add_occurance(word)
            return word
        
        if next_word is not None:
            combined = word + next_word
            if combined in self.dictionary:
                self.dictionary.add_occurance(combined)
                return combined
            
        if self.is_roman_numeral(word):
            return word
            
        if self.interactive:
            if self.dictionary.in_skips(word):
                return word
            return self.interactive_replace(word)
            
        return self.automatic_replace(word)

    def check_text(self, text_in, tokenizer):
        word_buffer = []
        for token in tokenizer.tokenize(text_in):
            if not token.isalpha():
                yield token
                continue
                
            if len(word_buffer) < 2:
                word_buffer.append(token)
                
                # at this point there are either 1 or 2 words in the buffer
                if len(word_buffer) < 2:
                    continue
                
            word, next_word = word_buffer
            word_buffer.pop(0)
        
            word = self.check(word, next_word)
            if word is not None:
                yield word

        # process the last word in the buffer
        word = self.check(word_buffer[0])
        if word is not None:
            yield word
            
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



