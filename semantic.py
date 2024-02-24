from ast import *
from lex import Token

def semantic_pass(node):
  return Ast(ast_body(node.body))

def ast_body(node):
  body = []
  
  for stmt in node.body:
    body += ast_stmt(node.scope, stmt)
  
  node.body = body
  
  return node

def ast_stmt(scope, node):
  if isinstance(node, AstPrintStmt):
    return [ast_print_stmt(scope, node)]
  if isinstance(node, AstReturnStmt):
    return [ast_return_stmt(scope, node)]
  elif isinstance(node, AstIfStmt):
    return [ast_if_stmt(scope, node)]
  elif isinstance(node, AstWhileStmt):
    return [ast_while_stmt(scope, node)]
  elif isinstance(node, AstForStmt):
    return [ast_for_stmt(scope, node)]
  elif isinstance(node, AstFunc):
    return ast_func(scope, node)
  elif isinstance(node, AstStruct):
    return ast_struct(scope, node)
  elif isinstance(node, AstStmt):
    if isinstance(node.body, AstVar):
      return ast_var(scope, node.body)
    elif isinstance(node.body, AstExpr):
      return [AstStmt(AstExpr(ast_expr(scope, node.body)))]
  else:
    raise Exception("NOT DONE BAKA!!!")

def ast_struct(scope, node):
  node.scope = Scope(None)
  
  for member in node.members:
    node.scope.insert(member.name.text, member)
  
  scope.struct_type[node.name.text] = node
  
  return []

def ast_func(scope, node):
  if scope.find(node.name):
    raise SemanticError(node, f"name '{node.name.text}' has already been declared")
  
  scope.insert(node.name.text, node)
  
  new_scope = Scope(scope, ret_type=node.var_type, attach_parent=False)
  
  for param in node.params:
    if isinstance(param.var_type, TypeArray):
      param.var_type = TypePointer(param.var_type.base)
    
    new_scope.insert(param.name.text, param)
  
  node.body = ast_compound_stmt(new_scope, node.body)
  
  return []

def ast_compound_stmt(scope, node):
  body = []
  node.scope = scope 
  
  for stmt in node.body:
    body += ast_stmt(node.scope, stmt)
  
  node.body = body
  
  return node

def ast_if_stmt(scope, node):
  node.cond = ast_expr(scope, node.cond)
  node.body = ast_compound_stmt(Scope(scope), node.body)
  return node

def ast_while_stmt(scope, node):
  node.cond = ast_expr(scope, node.cond)
  node.body = ast_compound_stmt(Scope(scope), node.body)
  return node

def ast_for_stmt(scope, node):
  new_scope = Scope(scope)
  
  node.init = ast_stmt(new_scope, node.init)
  node.cond = ast_expr(new_scope, node.cond)
  node.step = ast_expr(new_scope, node.step)
  node.body = ast_compound_stmt(new_scope, node.body)
  
  return node

def ast_print_stmt(scope, node):
  node.body = ast_expr(scope, node.body)
  return node

def ast_return_stmt(scope, node):
  if node.body:
    if not scope.ret_type:
      raise SemanticError(node, f"returning '{node.body}' but function has no return")
    
    node.body = ast_expr(scope, node.body)
    
    if not var_type_cmp(node.body.var_type, scope.ret_type):
      raise SemanticError(node, f"returning '{node.body}' of type '{node.body.var_type}' but expected '{scope.ret_type}'")
  else:
    if scope.ret_type:
      raise SemanticError(node, f"no return value but function returns '{scope.ret_type}'")
  
  return node

def ast_var(scope, node):
  if scope.find(node.name.text):
    raise SemanticError(node, f"name '{node.name.text}' has already been declared")
  
  scope.insert(node.name.text, node)
  
  if node.value:
    lhs = AstIdentifier(node.name.text, node.name)
    rhs = node.value
    
    body = ast_expr(scope, AstBinop(lhs, '=', rhs))
    
    return [AstStmt(AstExpr(body))]
  
  return []

def ast_expr(scope, expr):
  if isinstance(expr, AstExpr):
    return ast_expr(scope, expr.body)
  elif isinstance(expr, AstBinop):
    return ast_binop(scope, expr)
  elif isinstance(expr, AstUnaryOp):
    return ast_unary_op(scope, expr)
  elif isinstance(expr, AstConstant):
    return ast_constant(scope, expr)
  elif isinstance(expr, AstIdentifier):
    return ast_identifier(scope, expr)
  elif isinstance(expr, AstCall):
    return ast_call(scope, expr)
  elif isinstance(expr, AstIndex):
    return ast_index(scope, expr)
  elif isinstance(expr, AstAccess):
    return ast_access(scope, expr)
  else:
    raise Exception(f"NOT DONE BAKA!!!")

def ast_access(scope, node):
  node.base = ast_expr(scope, node.base)
  
  base_type = node.base.var_type
  
  if isinstance(base_type, TypePointer):
    base_type = node.base.var_type.base
  
  if not isinstance(base_type, TypeSpecifier) or base_type.specifier != "struct":
    raise SemanticError(node, f"request for member '{node.name.text}' for something not a struct.")
  
  if isinstance(node.base.var_type, TypePointer):
    if node.direct:
      raise SemanticError(node, f"direct request for member '{node.name.text}' from pointer.")
  else:
    if not node.direct:
      raise SemanticError(node, f"indirect request for member '{node.name.text}' from non-pointer.")
  
  member = base_type.struct_type.scope.find(node.name.text)
  
  if not member:
    raise SemanticError(node, f"'{node.base.var_type}' has no attribute '{node.name.text}'")
  
  if isinstance(member.var_type, TypeArray):
    node = AstUnaryOp('&', node, var_type=TypePointer(member.var_type.base))
  else:
    node.var_type = member.var_type
  
  return node

def ast_call(scope, node):
  node.base = ast_expr(scope, node.base)
  
  if isinstance(node.base, AstIdentifier):
    fn = scope.find(node.base.name)
  else:
    raise SemanticError(node, f"cannot call non-function '{node.base}'")
  
  if not fn:
    raise SemanticError(node, f"function '{node.base}' is not defined")
  
  fn_str = f"{fn.name}({', '.join([ str(x) for x in fn.params])})"
  
  args = []
  
  for arg in node.args:
    args.append(ast_expr(scope, arg))
  
  node.args = args
  
  if len(args) != len(fn.params):
    raise SemanticError(node, f"'{node}' incorrect number of arguments for '{fn_str}'")
  
  for arg, param in zip(node.args, fn.params):
    if not var_type_cmp(arg.var_type, param.var_type):
      raise SemanticError(node, f"incorrect argument supplied '{arg}' of type '{arg.var_type}' for '{param.name}' in '{fn_str}'")
  
  node.var_type = fn.var_type
  
  return node

def ast_index(scope, node):
  node.base = ast_expr(scope, node.base)
  node.pos = ast_expr(scope, node.pos)
  
  if not isinstance(node.base.var_type, TypeArray) and not isinstance(node.base.var_type, TypePointer):
    raise SemanticError(node.base, f"subscripted value '{node.base}' is neither array nor pointer.");
  
  node.var_type = node.base.var_type.base
  
  return node

def ast_unary_op(scope, node):
  node.body = ast_expr(scope, node.body)
  
  if node.op == "+":
    return ast_expr(scope, node.body)
  elif node.op == "&":
    node.var_type = TypePointer(node.body.var_type)
  elif node.op == "*":
    if not isinstance(node.body.var_type, TypePointer):
      raise SemanticError(node, f"invalid type argument of unary '*' (have '{node.body.var_type}')")
    
    node.var_type = node.body.var_type.base
  else:
    node.var_type = node.body.var_type
  
  return node

def ast_constant(scope, node):
  node.var_type = TypeSpecifier("int")
  return node

def ast_identifier(scope, node):
  var = scope.find(node.name)
  
  if not var:
    raise SemanticError(node, f"name '{node.name}' is not defined")
  
  node.var_type = var.var_type
  
  return node

def ast_binop(scope, node):
  if node.op in [ "+=", "-=", "*=", "/=" ]:
    op = node.op.split("=")[0]
    return ast_binop(scope, AstBinop(node.lhs, '=', AstBinop(node.lhs, op, node.rhs))) 
  
  node.lhs = ast_expr(scope, node.lhs)
  node.rhs = ast_expr(scope, node.rhs)
  
  if (
    var_type_cmp(node.lhs.var_type, TypeSpecifier("int")) and
    var_type_cmp(node.rhs.var_type, TypeSpecifier("int"))
  ):
    node.var_type = TypeSpecifier("int")
  elif (
    isinstance(node.lhs.var_type, TypePointer) and
    isinstance(node.rhs.var_type, TypePointer) and
    var_type_cmp(node.lhs.var_type.base, node.rhs.var_type.base)
  ):
    node.var_type = node.lhs.var_type
  elif (
    isinstance(node.lhs.var_type, TypeSpecifier) and
    isinstance(node.rhs.var_type, TypeSpecifier) and
    node.lhs.var_type.specifier == "struct" and node.rhs.var_type.specifier == "struct" and
    node.lhs.var_type.struct_type.name == node.rhs.var_type.struct_type.name
  ):
    node.var_type = node.lhs.var_type
  else:
    raise SemanticError(node, f"unsupported operand type(s) for '{node.op}': '{node.lhs.var_type}' and '{node.rhs.var_type}'")
  
  return node 

def var_type_cmp(a, b):
  if type(a) != type(b):
    return False
  elif isinstance(a, TypeSpecifier):
    if a.specifier == b.specifier:
      if a.specifier == "struct":
        return a.struct_type.name.text == b.struct_type.name.text
      return True
    else:
      return False
  elif isinstance(a, TypeArray):
    return var_type_cmp(a.base, b.base) and a.size == b.size
  elif isinstance(a, TypePointer) and isinstance(b, TypePointer):
    return var_type_cmp(a.base, b.base)
  else:
    print(type(a), type(b))
    raise Exception("I DONT KNOW THIS ONE!!!")

class SemanticError(Exception):
  def __init__(self, node, message):
    line, src = ast_src(node)
    super().__init__(f'{src}:{line}:{message}')
