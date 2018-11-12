#!/usr/bin/env python3

from sqlite3 import connect


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
    




