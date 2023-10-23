import re
from helper import find_match

class Token:
  def __init__(self, token_type, text):
    self.token_type = token_type
    self.text = text
  
  def __repr__(self):
    return self.text

class Lex:
  def __init__(self, text):
    self.text = text
    self.token = None
    self.next()
  
  def next(self):
    self.skip_whitespace()
    
    if len(self.text) == 0:
      return None
    
    self.token = find_match([
      self.match_number(),
      self.match_identifier(),
      self.match_symbol(),
      self.match_unknown()
    ])
    
    self.text = self.text[len(self.token.text):]
    
    return self.token
  
  def match(self, token_type):
    if self.token == None:
      return None
    
    if self.token.token_type == token_type:
      return self.token
    
    return None
  
  def accept(self, token_type):
    if self.token == None:
      return None
    
    if self.match(token_type):
      return self.pop()
    
    return None
  
  def expect(self, token_type):
    if self.token == None or self.token.token_type != token_type:
      print(f'expected \'{token_type}\' but found \'{self.token.token_type}\'')
    
    return self.accept(token_type)
  
  def pop(self):
    token = self.token
    self.next()
    return token
  
  def skip_whitespace(self):
    while re.search("^[ \t\n]", self.text):
      self.text = self.text[1:]
  
  def match_unknown(self):
    return Token("Unknown", self.text[0])
  
  def match_identifier(self):
    match = re.search("^[a-zA-Z_][a-zA-Z0-9_]*", self.text)
    
    if match:
      return Token("Identifier", match.group())
    
    return None
  
  def match_symbol(self):
    symbols = [
      "(", ")",
      "+", "-", "*", "/"
    ]
    
    for symbol in symbols:
      if self.text.startswith(symbol):
        return Token(symbol, symbol)
    
    return None
  
  def match_number(self):
    match = re.search("^[0-9]+", self.text)
    
    if match:
      return Token("Number", match.group())
    
    return None
