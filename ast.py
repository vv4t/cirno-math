
class Scope:
  def __init__(self, parent, ret_type=None, attach_parent=True):
    self.parent = parent
    self.ret_type = ret_type
    self.child = []
    self.var = {}
    
    if self.parent and attach_parent:
      self.ret_type = self.parent.ret_type
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

class TypePointer:
  def __init__(self, base):
    self.base = base
  
  def __repr__(self):
    return f'{self.base}*'

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

class AstCall:
  def __init__(self, base, args, var_type=None):
    self.base = base
    self.args = args
    self.var_type = None
  
  def __repr__(self):
    return f'{self.base}({", ".join([str(x) for x in self.args])})'

class AstUnaryOp:
  def __init__(self, op, body, token=None, var_type=None):
    self.token = token
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

class AstFunc:
  def __init__(self, name, params, var_type, body):
    self.var_type = var_type
    self.name = name
    self.params = params
    self.body = body
    self.label = None
  
  def __repr__(self, pad=0):
    return f'fn {self.name}({", ".join(self.args)}) {self.body.__repr__(pad=pad+2)}'

class AstPrintStmt:
  def __init__(self, token, body):
    self.token = token
    self.body = body
  
  def __repr__(self):
    return ' ' * pad + f'{self.token} {self.body};'

class AstReturnStmt:
  def __init__(self, token, body):
    self.token = token
    self.body = body
  
  def __repr__(self, pad=0):
    return ' ' * pad + f'{self.token} {self.body};'

class AstIfStmt:
  def __init__(self, cond, body):
    self.cond = cond
    self.body = body
  
  def __repr__(self, pad=0):
    return ' ' * pad + f'if ({self.cond}) {self.body.__repr__(pad=pad+2)};'

class AstWhileStmt:
  def __init__(self, cond, body):
    self.cond = cond
    self.body = body
  
  def __repr__(self, pad=0):
    return ' ' * pad + f'while ({self.cond}) {self.body.__repr__(pad=pad+2)};'

class AstForStmt:
  def __init__(self, init, cond, step, body):
    self.init = init
    self.cond = cond
    self.step = step
    self.body = body
  
  def __repr__(self, pad=0):
    return ' ' * pad + f'for ({self.init}; {self.cond}; {self.step}) {self.body.__repr__(pad=pad+2)};'

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
    return '{\n' + '\n'.join([ ' ' * pad + str(stmt) for stmt in self.body ]) + ' ' * pad + '\n}'

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
  elif isinstance(node, AstFunc):
    return ast_src(node.name)
  elif isinstance(node, AstPrintStmt):
    return (node.token.line, node.token.src)
  elif isinstance(node, AstReturnStmt):
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
    return (node.token.line, node.token.src)
  elif isinstance(node, AstIndex):
    return ast_src(node.base)
  elif isinstance(node, AstCall):
    return ast_src(node.base)
  elif isinstance(node, AstConstant):
    return (node.token.line, node.token.src)
  elif isinstance(node, AstIdentifier):
    return (node.token.line, node.token.src)
  
  print(type(node))
  raise Exception("I DONT KNOW THIS ONE !!!!!")
