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
  elif isinstance(node, AstStmt):
    if isinstance(node.body, AstVar):
      return ast_var(scope, node.body)
    elif isinstance(node.body, AstExpr):
      return [AstStmt(AstExpr(ast_expr(scope, node.body)))]
  else:
    raise Exception("NOT DONE BAKA!!!")

def ast_func(scope, node):
  if scope.find(node.name):
    raise SemanticError(node, f"name '{node.name.text}' has already been declared")
  
  scope.insert(node.name.text, node)
  
  new_scope = Scope(scope, ret_type=node.var_type, attach_parent=False)
  
  for param in node.params:
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
  if scope.find(node.name):
    raise SemanticError(node, f"name '{node.name.text}' has already been declared")
  
  scope.insert(node.name.text, node)
  
  if node.value:
    lhs = AstIdentifier(node.name.text, node.name)
    op = Token('=', '=')
    rhs = node.value
    
    body = ast_expr(scope, AstBinop(lhs, op, rhs))
    
    return [AstStmt(AstExpr(body))]
  
  return []

def ast_expr(scope, expr):
  if isinstance(expr, AstExpr):
    return ast_expr(scope, expr.body)
  elif isinstance(expr, AstBinop):
    return ast_binop(scope, expr)
  elif isinstance(expr, AstConstant):
    return ast_constant(scope, expr)
  elif isinstance(expr, AstIdentifier):
    return ast_identifier(scope, expr)
  elif isinstance(expr, AstUnaryOp):
    return ast_unary_op(scope, expr)
  elif isinstance(expr, AstCall):
    return ast_call(scope, expr)
  elif isinstance(expr, AstIndex):
    return ast_index(scope, expr)
  else:
    raise Exception(f"NOT DONE BAKA!!!")

def ast_call(scope, node):
  if not isinstance(node.base, AstIdentifier):
    raise SemanticError(node, f"cannot call non-function '{node.base}'")
  
  fn = scope.find(node.base.name)
  
  if not fn:
    raise SemanticError(node, f"function '{node.base}' is not defined")
  
  fn_str = f"{fn.name}({', '.join([ str(x) for x in fn.params])})"
  
  if len(node.args) != len(fn.params):
    raise SemanticError(node, f"'{node}' incorrect number of arguments for '{fn_str}'")
  
  args = []
  for arg in node.args:
    args.append(ast_expr(scope, arg))
  node.args = args
  
  for arg, param in zip(node.args, fn.params):
    if not var_type_cmp(arg.var_type, param.var_type):
      raise SemanticError(node, f"incorrect argument supplied '{arg}' of type '{arg.var_type}' for '{param.name}' in '{fn_str}'")
  
  node.var_type = fn.var_type
  
  return node

def ast_index(scope, node):
  node.base = ast_expr(scope, node.base)
  node.pos = ast_expr(scope, node.pos)
  node.var_type = node.base.var_type.base
  return node

def ast_unary_op(scope, node):
  node.body = ast_expr(scope, node.body)
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
  node.lhs = ast_expr(scope, node.lhs)
  node.rhs = ast_expr(scope, node.rhs)
  
  if binop_type_cmp(node, (TypeSpecifier("int"), TypeSpecifier("int"))):
    node.var_type = TypeSpecifier("int")
  else:
    raise SemanticError(node, f"unsupported operand type(s) for '{node.op}': '{node.lhs.var_type}' and '{node.rhs.var_type}'")
  
  return node 

def binop_type_cmp(node, cmp_type):
  lhs, rhs = cmp_type
  return var_type_cmp(node.lhs.var_type, lhs) and var_type_cmp(node.rhs.var_type, rhs)

def var_type_cmp(a, b):
  if type(a) != type(b):
    return False
  elif isinstance(a, TypeSpecifier):
    return a.specifier == b.specifier
  elif isinstance(a, TypeArray):
    return var_type_cmp(a.base, b.base) and a.size == b.size
  else:
    raise Exception("I DONT KNOW THIS ONE!!!")

class SemanticError(Exception):
  def __init__(self, node, message):
    line, src = ast_src(node)
    super().__init__(f'{src}:{line}:{message}')
