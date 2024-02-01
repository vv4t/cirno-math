
class Scope:
  def __init__(self, parent):
    self.parent = parent
    self.child = []
    self.var = {}
    
    if self.parent:
      self.parent.child.append(self)
  
  def insert(self, name, node):
    self.var[name] = node
  
  def find(self, name):
    if name not in self.var:
      if self.parent:
        return self.parent.find(name)
      else:
        return None
    
    return self.var[name]

class TypeSpecifier:
  def __init__(self, specifier, token=None):
    self.token = token
    self.specifier = specifier
  
  def __repr__(self):
    return f'{self.specifier}'

class TypeArray:
  def __init__(self, base, size):
    self.base = base
    self.size = size
  
  def __repr__(self):
    return f'{self.base}[{self.size}]'

class AstConstant:
  def __init__(self, value, token, var_type=None):
    self.token = token
    self.value = value
    self.var_type = var_type
  
  def __repr__(self):
    return self.token.__repr__()

class AstIdentifier:
  def __init__(self, name, token=None, var_type=None):
    self.token = token
    self.name = name
    self.var_type = var_type
  
  def __repr__(self):
    return self.token.__repr__()

class AstIndex:
  def __init__(self, base, pos, var_type=None):
    self.base = base
    self.pos = pos
    self.var_type = var_type
  
  def __repr__(self):
    return f'{self.base}[{self.pos}]'

class AstUnaryOp:
  def __init__(self, op, body, var_type=None):
    self.op = op
    self.body = body
    self.var_type = var_type
  
  def __repr__(self):
    return f'{self.op}{self.body}'

class AstBinop:
  def __init__(self, lhs, op, rhs, var_type=None):
    self.lhs = lhs
    self.op = op
    self.rhs = rhs
    self.var_type = var_type
  
  def __repr__(self):
    return f'{self.lhs} {self.op} {self.rhs}'

class AstExpr:
  def __init__(self, body, bracket=False, var_type=None):
    self.body = body
    self.bracket = bracket
    
    if not var_type:
      self.var_type = body.var_type
  
  def __repr__(self):
    if self.bracket:
      return f'({self.body})'
    else:
      return f'{self.body}'

class AstVar:
  def __init__(self, var_type, name, value):
    self.var_type = var_type
    self.name = name
    self.value = value
    self.loc = 0
  
  def __repr__(self):
    if self.value:
      return f'{self.var_type} {self.name} = {self.value}'
    else:
      return f'{self.var_type} {self.name}'

class AstPrintStmt:
  def __init__(self, token, body):
    self.token = token
    self.body = body
  
  def __repr__(self):
    return f'{self.token} {self.body};'

class AstIfStmt:
  def __init__(self, cond, body):
    self.cond = cond
    self.body = body
  
  def __repr__(self, pad=0):
    return ' ' * pad + f'if ({self.cond})\n{self.body.__repr__(pad=pad+2)};'

class AstWhileStmt:
  def __init__(self, cond, body):
    self.cond = cond
    self.body = body
  
  def __repr__(self, pad=0):
    return ' ' * pad + f'while ({self.cond})\n{self.body.__repr__(pad=pad+2)};'

class AstForStmt:
  def __init__(self, init, cond, step, body):
    self.init = init
    self.cond = cond
    self.step = step
    self.body = body
  
  def __repr__(self, pad=0):
    return ' ' * pad + f'for ({self.init}; {self.cond}; {self.step})\n{self.body.__repr__(pad=pad+2)};'

class AstStmt:
  def __init__(self, body):
    self.body = body
  
  def __repr__(self):
    return f'{self.body};'

class AstBody:
  def __init__(self, body):
    self.body = body
    self.scope = Scope(None)
  
  def __repr__(self, pad=0):
    return (' ' * pad + '\n').join([ str(stmt) for stmt in self.body ])

class Ast:
  def __init__(self, body):
    self.body = body
  
  def __repr__(self):
    return f'{self.body}'

def ast_src(node):
  if isinstance(node, Ast):
    return ast_src(node.body)
  elif isinstance(node, AstBody):
    return ast_src(node.body[0])
  elif isinstance(node, AstStmt):
    return ast_src(node.body)
  elif isinstance(node, AstPrintStmt):
    return (node.token.line, node.token.src)
  
  if isinstance(node, AstVar):
    return ast_src(node.var_type)
  elif isinstance(node, TypeArray):
    return ast_src(node.base)
  elif isinstance(node, TypeSpecifier):
    return (node.token.line, node.token.src)
  
  if isinstance(node, AstExpr):
    return ast_src(node.body)
  elif isinstance(node, AstBinop):
    return ast_src(node.lhs)
  elif isinstance(node, AstUnaryOp):
    return (node.op.line, node.op.src)
  elif isinstance(node, AstIndex):
    return ast_src(node.base)
  elif isinstance(node, AstConstant):
    return (node.token.line, node.token.src)
  elif isinstance(node, AstIdentifier):
    return (node.token.line, node.token.src)
  
  raise Exception("I DONT KNOW THIS ONE !!!!!")
