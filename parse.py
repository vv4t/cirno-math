from ast import *
from helper import find_match
from lex import LexError

class Parse:
  def __init__(self, lex):
    self.lex = lex
    self.class_types = {}
  
  def parse(self):
    body = self.parse_body()
    
    if not body:
      return None
    
    return Ast(body)
  
  def parse_body(self):
    stmt = find_match([
      lambda : self.parse_stmt(),
      lambda : self.parse_function(),
      lambda : self.parse_class()
    ])
    
    if not stmt:
      return None
    
    body = []
    
    while stmt:
      body.append(stmt)
      stmt = find_match([
        lambda : self.parse_stmt(),
        lambda : self.parse_function(),
        lambda : self.parse_class()
      ])
    
    return AstBody(body)

  def parse_class(self):
    if not self.lex.accept("class"):
      return None
    
    name = self.lex.expect("Identifier")
    
    members = []
    
    self.lex.expect("{")
    members = self.parse_member_list()
    self.lex.expect("}")
    
    self.class_types[name.text] = AstClass(name, members)
    
    return self.class_types[name.text]

  def parse_member_list(self):
    members = []
    
    member = self.parse_member()
    
    while member:
      members.append(member)
      member = self.parse_member()
    
    return members
        
  def parse_member(self):
    var_type = self.parse_var_type()
    
    if not var_type:
      return None
    
    name = self.lex.expect("Identifier")
    
    self.lex.expect(';')
    
    return AstVar(var_type, name, None)

  def parse_function(self):
    if not self.lex.accept("fn"):
      return None
    
    name = self.lex.expect("Identifier")
    
    self.lex.expect("(")
    params = self.parse_param_list()
    self.lex.expect(")")
    
    var_type = None
    
    if self.lex.accept(":"):
      var_type = self.parse_var_type()
      
      if not var_type:
        raise LexError(name, "function has no return type")
    
    body = self.parse_compound_stmt()
    
    return AstFunc(name, params, var_type, body)

  def parse_param_list(self):
    param = self.parse_param()
    
    if not param:
      return []
    
    params = [param]
    
    while self.lex.accept(','):
      param = self.parse_param()
      
      if not param:
        raise LexError(self.lex.token, f"expected parameter-declaration before '{self.lex.token}'")
      
      params.append(param)
    
    return params

  def parse_param(self):
    var_type = self.parse_var_type()
    
    if not var_type:
      return None
    
    name = self.lex.expect("Identifier")
    
    return AstVar(var_type, name, None)

  def parse_stmt(self):
    body = find_match([
      lambda : self.parse_print_stmt(),
      lambda : self.parse_return_stmt(),
      lambda : self.parse_if_stmt(),
      lambda : self.parse_while_stmt(),
      lambda : self.parse_for_stmt()
    ])
    
    if body:
      return body
    
    body = find_match([
      lambda : self.parse_var(),
      lambda : self.parse_expr()
    ])
    
    if not body:
      return None
    
    self.lex.expect(';')
    
    return AstStmt(body)

  def parse_if_stmt(self):
    if not self.lex.accept("if"):
      return None
    
    self.lex.expect("(")
    cond = parse_expr(self.lex)
    self.lex.expect(")")
    
    body = parse_compound_stmt(self.lex)
    
    return AstIfStmt(cond, body)

  def parse_while_stmt(self):
    if not self.lex.accept("while"):
      return None
    
    self.lex.expect("(")
    cond = self.parse_expr()
    self.lex.expect(")")
    
    body = self.parse_compound_stmt()
    
    return AstWhileStmt(cond, body)

  def parse_for_stmt(self):
    if not self.lex.accept("for"):
      return None
    
    self.lex.expect("(")
    
    init = find_match([
      lambda : self.parse_expr(),
      lambda : self.parse_var(),
    ])
    
    self.lex.expect(';')
    cond = slef.parse_expr()
    self.lex.expect(';')
    
    step = find_match([
      lambda : self.parse_expr(),
      lambda : self.parse_var(),
    ])
    
    self.lex.expect(")")
    
    body = self.parse_compound_stmt()
    
    return AstForStmt(AstStmt(init) if init else None, cond, step, body)

  def parse_print_stmt(self):
    token = self.lex.accept("print")
    
    if not token:
      return None
    
    body = self.parse_expr()
    
    self.lex.expect(';')
    
    return AstPrintStmt(token, body)

  def parse_return_stmt(self):
    token = self.lex.accept("return")
    
    if not token:
      return None
    
    body = self.parse_expr()
    
    self.lex.expect(';')
    
    return AstReturnStmt(token, body)

  def parse_compound_stmt(self):
    if not self.lex.match('{'):
      return AstBody([ parse_stmt(self.lex) ])
    
    self.lex.expect('{')
    
    stmt = self.parse_stmt()
    
    if not stmt:
      return None
    
    body = []
    
    while stmt:
      body.append(stmt)
      stmt = self.parse_stmt()
    
    self.lex.expect('}')
    
    return AstBody(body)

  def parse_var(self):
    var_type = self.parse_var_type()
    
    if not var_type:
      return None
    
    name = self.lex.expect("Identifier")
    
    value = None
    
    if self.lex.accept('='):
      value = self.parse_expr()
    
    return AstVar(var_type, name, value)

  def parse_var_type(self):
    specifier = find_match([
      lambda : self.lex.accept("int")
    ])
    
    if specifier:
      var_type = TypeSpecifier(specifier.text, token=specifier)
    elif self.lex.match("Identifier"):
      if self.lex.token.text in self.class_types:
        token = self.lex.pop()
        var_type = TypeSpecifier("class", class_type=self.class_types[token.text], token=token)
      else:
        return None
    else:
      return None
    
    while True:
      if self.lex.accept('['):
        size = self.lex.expect("Number")
        self.lex.expect(']')
        var_type = TypeArray(var_type, int(size.text))
      elif self.lex.accept('*'):
        var_type = TypePointer(var_type)
      else:
        break
    
    return var_type

  def parse_expr(self):
    body = find_match([
      lambda : self.parse_binop(),
      lambda : self.parse_postfix(),
      lambda : self.parse_primitive()
    ])
    
    if not body:
      return None
    
    return AstExpr(body)

  def parse_binop(self):
    return self.parse_binop_level(0)

  def parse_binop_level(self, level):
    op_set = [
      [ "=" ],
      [ "=" ],
      [ "==", "!=" ],
      [ ">=", "<=", "<", ">" ],
      [ "+", "-" ],
      [ "*", "/" ]
    ]
    
    if level == len(op_set):
      return self.parse_unary_op()
    
    lhs = self.parse_binop_level(level + 1)
    
    op = find_match([ (lambda y: (lambda : self.lex.accept(y)))(x) for x in op_set[level] ])
    
    if not op:
      return lhs
    
    rhs = self.parse_binop_level(level)
    
    if not rhs:
      raise LexError(op, f"expected 'Expression' after '{op}' but found {self.lex.token.text}")
    
    return AstBinop(lhs, op, rhs)

  def parse_unary_op(self):
    op = find_match([
      lambda : self.lex.accept('-'),
      lambda : self.lex.accept('+'),
      lambda : self.lex.accept('&'),
      lambda : self.lex.accept('*'),
    ])
    
    if op:
      return AstUnaryOp(op.text, self.parse_unary_op(), token=op)
    else:
      return self.parse_postfix()

  def parse_postfix(self):
    base = self.parse_primitive()
    
    while True:
      if self.lex.accept('['):
        pos = self.parse_expr()
        self.lex.expect(']')
        base = AstIndex(base, pos)
      elif self.lex.accept('('):
        args = self.parse_arg_list()
        self.lex.expect(')')
        base = AstCall(base, args)
      elif self.lex.accept('.'):
        name = self.lex.expect("Identifier")
        base = AstAccess(base, name, direct=True)
      elif self.lex.accept('->'):
        name = self.lex.expect("Identifier")
        base = AstAccess(base, name, direct=False)
      else:
        return base

  def parse_arg_list(self):
    arg = self.parse_expr()
    
    if not arg:
      return []
    
    args = [arg]
    
    while self.lex.accept(','):
      arg = self.parse_expr()
      
      if not arg:
        raise LexError(self.lex.token, f"expected argument-expression before '{self.lex.token}'")
      
      args.append(arg)
    
    return args

  def parse_primitive(self):
    if self.lex.match("Number"):
      token = self.lex.pop()
      return AstConstant(int(token.text), token)
    
    if self.lex.match("Identifier"):
      token = self.lex.pop()
      return AstIdentifier(token.text, token)
    
    if self.lex.accept("("):
      body = AstExpr(self.parse_expr(), bracket=True)
      self.lex.expect(")")
      return body
    
    return None
