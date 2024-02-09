
class Scope:
  def __init__(self, parent, ret_type=None, attach_parent=True, size=0, parent_class=None):
    self.parent = parent
    self.ret_type = ret_type
    self.child = []
    self.class_type = {}
    self.parent_class = parent_class
    self.var = {}
    self.size = size
    
    if self.parent and attach_parent:
      self.ret_type = self.parent.ret_type
      self.parent_class = self.parent.parent_class
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
  def __init__(self, specifier, class_type=None, token=None):
    self.token = token
    self.specifier = specifier
    self.class_type = class_type
  
  def __repr__(self):
    if self.specifier == "class":
      return f'{self.specifier} {self.class_type.name.text}'
    else:
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

class AstThis:
  def __init__(self, token, var_type=None):
    self.token = token
    self.var_type = var_type
  
  def __repr__(self):
    return self.token.__repr__()

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

class AstAccess:
  def __init__(self, base, name, direct=True, var_type=None):
    self.direct = direct
    self.base = base
    self.name = name
    self.var_type = var_type
  
  def __repr__(self):
    if self.direct:
      return f'{self.base}.{self.name}'
    else:
      return f'{self.base}->{self.name}'

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
  def __init__(self, lhs, op, rhs, token=None, var_type=None):
    self.lhs = lhs
    self.op = op
    self.rhs = rhs
    self.token = token
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

class AstClass:
  def __init__(self, name, members, methods, scope=None, size=0):
    self.name = name
    self.members = members
    self.methods = methods
    self.scope = scope
    self.size = size
  
  def __repr__(self, pad=0):
    str_pad = "\n" + " " * (pad + 2)
    members = str_pad + ("\n" + " " * (pad + 2)).join(map(str, self.members)) + "\n"
    methods = str_pad + "\n".join([ method.__repr__(pad=pad+2) for method in self.methods ]) + "\n"
    return f'class {self.name} {{{members}{methods}}}'

class AstFunc:
  def __init__(self, name, params, var_type, body):
    self.var_type = var_type
    self.name = name
    self.params = params
    self.body = body
    self.label = None
  
  def __repr__(self, pad=0):
    return f'fn {self.name}({", ".join(map(str, self.params))}) {self.body.__repr__(pad=pad)}'

class AstPrintStmt:
  def __init__(self, token, body):
    self.token = token
    self.body = body
  
  def __repr__(self, pad=0):
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
  
  def __repr__(self, pad=0):
    return ' ' * pad + f'{self.body};'

class AstBody:
  def __init__(self, body):
    self.body = body
    self.scope = Scope(None)
  
  def __repr__(self, pad=0):
    return '{\n' + '\n'.join([ stmt.__repr__(pad=pad+2) for stmt in self.body ]) + '\n' + ' ' * pad + '}'

class Ast:
  def __init__(self, body):
    self.body = body
  
  def __repr__(self):
    return f'{self.body}'

def ast_lvalue(node):
  return (
    isinstance(node, AstIdentifier) or \
    isinstance(node, AstIndex) or \
    (isinstance(node, AstUnaryOp) and node.op == '*') or \
    isinstance(node, AstUnaryOp) and node.op == '*' or \
    isinstance(node, AstAccess)
  )

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
  elif isinstance(node, AstThis):
    return (node.token.line, node.token.src)
  elif isinstance(node, AstAccess):
    return ast_src(node.base)
  
  print(type(node))
  raise Exception("I DONT KNOW THIS ONE !!!!!")
