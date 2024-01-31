from ast import *
from lex import Token

def semantic_pass(node):
  return Ast(ast_body(node.body))

def ast_body(scope):
  body = []
  
  for stmt in scope.body:
    body += ast_stmt(scope, stmt)
  
  scope.body = body
  
  return scope

def ast_stmt(scope, node):
  if isinstance(node, AstPrintStmt):
    return [ast_print_stmt(scope, node)]
  elif isinstance(node, AstIfStmt):
    return [ast_if_stmt(scope, node)]
  elif isinstance(node, AstStmt):
    if isinstance(node.body, AstVar):
      ast_var(scope, node.body)
      return []
    elif isinstance(node.body, AstExpr):
      return [AstExpr(ast_expr(scope, node.body))]
  else:
    raise Exception("NOT DONE BAKA!!!")

def ast_compound_stmt(scope, node):
  body = []
  
  for stmt in node.body:
    body += ast_stmt(scope, stmt)
  
  node.body = body
  
  return node

def ast_if_stmt(scope, node):
  node.cond = ast_expr(scope, node.cond)
  node.body = ast_compound_stmt(scope, node.body)
  return node

def ast_print_stmt(scope, node):
  node.body = ast_expr(scope, node.body)
  return node

def ast_var(scope, node):
  scope.var[node.name.text] = node

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
  elif isinstance(expr, AstIndex):
    return ast_index(scope, expr)
  else:
    raise Exception(f"NOT DONE BAKA!!!")

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
  node.var_type = TypeSpecifier(Token("int", "int", 0, "builtin"))
  return node

def ast_identifier(scope, node):
  if node.identifier not in scope.var:
    raise SemanticError(node, f"name '{node.identifier}' is not defined")
  
  node.var_type = scope.var[node.identifier].var_type
  
  return node

def ast_binop(scope, node):
  lhs = ast_expr(scope, node.lhs)
  
  if node.op.text == "=":
    rhs = AstExpr(ast_expr(scope, node.rhs))
    
    if not var_type_cmp(lhs.var_type, rhs.var_type):
      raise SemanticError(node, f"unsupported operand type(s) for '=': '{lhs.var_type}' and '{rhs.var_type}'")
    
    return AstAssign(lhs, rhs, lhs.var_type)
  
  rhs = ast_expr(scope, node.rhs)
  
  if not var_type_cmp(lhs.var_type, rhs.var_type):
    raise SemanticError(node, f"unsupported operand type(s) for '{node.op}': '{lhs.var_type}' and '{rhs.var_type}")
  
  return AstBinop(lhs, node.op, rhs, var_type=lhs.var_type)

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
