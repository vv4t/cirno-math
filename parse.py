from helper import find_match

class NumberNode:
  def __init__(self, token):
    self.token = token
    self.number = int(self.token.text)
  
  def __repr__(self):
    return self.token.__repr__()

class IdentifierNode:
  def __init__(self, token):
    self.token = token
    self.identifier = token.text
  
  def __repr__(self):
    return self.token.__repr__()

class BinopNode:
  def __init__(self, lhs, op, rhs):
    self.lhs = lhs
    self.op = op
    self.rhs = rhs
  
  def __repr__(self):
    return f'{self.lhs.__repr__()} {self.op.__repr__()} {self.rhs.__repr__()}'

def parse(lex):
  return parse_expr(lex)

def parse_expr(lex):
  return find_match([
    parse_binop(lex),
    parse_primitive(lex)
  ])

def parse_binop(lex):
  return parse_binop_level(lex, 0)

def parse_binop_level(lex, level):
  op_set = [
    [ "+", "-" ],
    [ "*", "/" ]
  ]
  
  if level == len(op_set):
    return parse_primitive(lex)
  
  lhs = parse_binop_level(lex, level + 1)
  
  op = find_match([ lex.accept(op) for op in op_set[level] ])
  
  if not op:
    return lhs
  
  rhs = parse_binop_level(lex, level)
  
  return BinopNode(lhs, op, rhs)

def parse_primitive(lex):
  if lex.match("Number"):
    return NumberNode(lex.pop())
  
  if lex.match("Identifier"):
    return IdentifierNode(lex.pop())
  
  if lex.accept("("):
    expr = parse_expr(lex)
    lex.expect(")")
    return expr
  
  return None
