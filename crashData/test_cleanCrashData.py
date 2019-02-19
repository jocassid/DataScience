
from pytest import fixture, raises

from dictionary import Dictionary, WordRecord
from spellcheck import delete_generator, inserts_generator, \
    replace_generator, SpellChecker, split_generator, transpose_generator, \
    validate_alphabet, validate_word
from tokenizer import Tokenizer


def test_validate_word():
    with raises(ValueError):
        validate_word(None)
        
    with raises(ValueError):
        validate_word('')
        
    with raises(ValueError):
        validate_word(' \t\n')
        
    try:
        validate_word('foo')
    except Exception:
        assert False, "No exception should have been thrown"
        
        
def test_validate_alphabet():
    
    expected_message = "alphabet can't be None" 
    with raises(ValueError, match=expected_message):
        validate_alphabet(None)
        
    expected_message = "alphabet must be a set"
    with raises(ValueError, match=expected_message):
        validate_alphabet('abc')
    
    expected_message = "alphabet can't be empty set"
    with raises(ValueError, match=expected_message):
        validate_alphabet(set())
    
    validate_alphabet({'a', 'b', 'c'})


def test_split_generator():
    
    # pass a bad word value to make sure word is being validated
    with raises(ValueError):
        list(split_generator(None))

    with raises(ValueError):
        list(split_generator('i'))
        
    assert [('a', 'm')] == list(split_generator('am'))
    assert [('c', 'an'), ('ca', 'n')] == list(split_generator('can'))


def test_delete_generator():
    
    # pass a bad word value to make sure word is being validated
    with raises(ValueError):
        list(delete_generator(None))
        
    assert set([]) == set(delete_generator('i'))
    assert {'a', 't'} == set(delete_generator('at'))
    assert {'at', 'mt', 'ma'} == set(delete_generator('mat'))


def test_transpose_generator():
    
    # pass a bad word value to make sure word is being validated
    with raises(ValueError):
        list(transpose_generator(None))

    assert {'i'} == set(transpose_generator('i'))
    assert {'ta'} == set(transpose_generator('at'))
    assert {'amt', 'mta'} == set(transpose_generator('mat'))


def test_replace_generator():
    
    # pass a bad word value to make sure word is being validated
    with raises(ValueError):
        list(replace_generator(None, set('abc')))
        
    with raises(ValueError):
        list(replace_generator('', set('abc')))
        
    with raises(ValueError):
        list(replace_generator('i', None))
        
    with raises(ValueError):
        list(replace_generator('i', set()))

    assert {'a', 'b', 'c'} == set(replace_generator('i', set('abc')))
    
    expected = {'bt', 'ct', 'aa', 'ab', 'ac'}
    assert expected == set(replace_generator('at', set('abc')))    


def test_inserts_generator():
    
    # pass a bad word value to make sure word is being validated
    with raises(ValueError):
        list(inserts_generator(None, set('abc')))

    # pass a bad alphabet to make sure alphabet is being validated
    with raises(ValueError):
        list(inserts_generator('i', None))

    expected = {
        'aX', 'bX', 'Xa', 'Xb'
    }
    actual = inserts_generator('X', set('ab'))
    assert expected == set(actual)
        

class TestDictionary(object):
    
    def test_contains(self):
        dictionary = Dictionary(':memory:')
        dictionary.add('alpha')
        assert 'alpha' in dictionary
        assert 'Alpha' not in dictionary
    
    def test_getitem(self):
        dictionary = Dictionary(':memory:')
        words = ['alpha', 'alpha', 'bravo', 'charlie']
        for word in words:
            dictionary.add(word)
               
        assert dictionary['alpha'] == WordRecord('alpha', 2)
        assert dictionary['bravo'] == WordRecord('bravo', 1)
        assert dictionary['charlie'] == WordRecord('charlie', 1)

 
 
@fixture
def dictionary():
    
    dictionary = Dictionary(':memory:')
    
    words = [
        ('to', 5),
        ('be', 2),
        ('is', 4),
        ('he', 1),
        ('we', 3), 
    ]
    
    for word, occurances in words:
        dictionary.add(word, occurances)
        
    dictionary.words_scanned = sum([c for w, c in words])      
    return dictionary

 
@fixture
def spell_checker(dictionary):
    return SpellChecker(dictionary)    
 
 
class TestSpellChecker(object):
    
    @staticmethod
    def get_candidates(spellchecker, word):
        candidate_count = 3
        candidates = []
        for prob, candidate1, candidate2 in spellchecker.find_candidates(
                word, 
                candidate_count):
            candidate = (round(prob, 4), candidate1, candidate2)
            candidates.append(candidate)
        return candidates
    
    def test_find_candidates(self, spell_checker):
        
        candidates = self.get_candidates(spell_checker, 'tobe')
        expected = {(0.2333, 'to', 'be')}
        assert expected == set(candidates)
        
        candidates = self.get_candidates(spell_checker, 'wet')
        expected = {(0.2, 'we', None)}
        assert expected == set(candidates)
        
        candidates = self.get_candidates(spell_checker, 'eb')
        expected = {(0.1333, 'be', None)}
        assert expected == set(candidates)
        
        candidates = self.get_candidates(spell_checker, 'it')
        expected = {(0.2667, 'is', None)}
        assert expected == set(candidates)
        
        candidates = self.get_candidates(spell_checker, 'e')
        expected = {
            (0.1333, 'be', None), 
            (0.0667, 'he', None),
            (0.2, 'we', None),
        }
        assert expected == set(candidates)
        
                
def test_tokenize():
    tokenizer = Tokenizer()
    text_in = "hello world!"
    tokens_out = list(tokenizer.tokenize(text_in))
    assert tokens_out == ['hello', ' ', 'world', '!']
    
    text_in = 'De Havilland DH-4'
    tokens_out = list(tokenizer.tokenize(text_in))
    assert tokens_out == ['De', ' ', 'Havilland', ' ', 'DH', '-', '4']
    



