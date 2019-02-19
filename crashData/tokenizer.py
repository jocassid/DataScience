

class Tokenizer(object):
    
    MODE_ALPHANUMERIC = 1
    MODE_WHITESPACE = 2
    MODE_PRINTABLE = 3
    
    def __init__(
            self, 
            hyphen_continues_word=False):
        self.char_buffer = []
        self.mode = None
        self.hyphen_continues_word = hyphen_continues_word
        
        self.handlers = [
            self.handle_alphanumeric,
            self.handle_whitespace,
            self.handle_other,
        ]

    def mode_none(self, next_mode, c):
        self.mode = next_mode
        self.char_buffer.append(c)
        
    def mode_change(self, next_mode, c):
        token = "".join(self.char_buffer)
        self.mode = next_mode
        self.char_buffer = [c]
        return token

    def run_handlers(self, c):
        for handler in self.handlers:
            value = handler(c)
            if value is None:
                # Not this handler's job
                continue
            if value == '':
                # Handled, but no token at this point
                return None
            # we have a token
            return value
        return None

    def handle_alphanumeric(self, c):
        if not c.isalnum():
            if not self.hyphen_continues_word:
                return None
            if c != '-':
                return None

        if self.mode is None:
            self.mode_none(self.MODE_ALPHANUMERIC, c)
            return ""
            
        if self.mode == self.MODE_ALPHANUMERIC:
            self.char_buffer.append(c)
            return ""

        return self.mode_change(self.MODE_ALPHANUMERIC, c)

    def handle_whitespace(self, c):
        if not c.isspace():
            return None
            
        if self.mode is None:
            self.mode_none(self.MODE_WHITESPACE, c)
            return ""
            
        if self.mode == self.MODE_WHITESPACE:
            self.char_buffer.append(c)
            return ""
            
        return self.mode_change(self.MODE_WHITESPACE, c)

    def handle_other(self, c):
        if not c.isprintable():
            return None
            
        if self.mode is None:
            self.mode_none(self.MODE_PRINTABLE, c)
            return ""
            
        if self.mode == self.MODE_PRINTABLE:
            self.char_buffer.append(c)
            return ""
            
        return self.mode_change(self.MODE_PRINTABLE, c)

    def tokenize(self, text_in):
        self.char_buffer = []
        self.mode = None
        
        for c in text_in:
            token = self.run_handlers(c)
            if token is not None:
                yield token
            
        yield "".join(self.char_buffer)
            
