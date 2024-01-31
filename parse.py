from ast import *
from helper import find_match
from lex import LexError

def parse(lex):
  body = parse_body(lex)
  
  if not body:
    return None
  
  return Ast(body)

def parse_body(lex):
  stmt = parse_stmt(lex)
  
  if not stmt:
    return None
  
  body = []
  
  while stmt:
    body.append(stmt)
    stmt = parse_stmt(lex)
  
  return AstBody(body)

def parse_stmt(lex):
  body = find_match([
    parse_print_stmt(lex),
    parse_if_stmt(lex),
    parse_while_stmt(lex)
  ])
  
  if body:
    return body
  
  body = find_match([
    parse_expr(lex),
    parse_var(lex),
  ])
  
  if not body:
    return None
  
  lex.expect(';')
  
  return AstStmt(body)

def parse_if_stmt(lex):
  if not lex.accept("if"):
    return None
  
  lex.expect("(")
  cond = parse_expr(lex)
  lex.expect(")")
  
  body = parse_compound_stmt(lex)
  
  return AstIfStmt(cond, body)

def parse_while_stmt(lex):
  if not lex.accept("while"):
    return None
  
  lex.expect("(")
  cond = parse_expr(lex)
  lex.expect(")")
  
  body = parse_compound_stmt(lex)
  
  return AstWhileStmt(cond, body)

def parse_print_stmt(lex):
  token = lex.accept("print")
  
  if not token:
    return None
  
  body = parse_expr(lex)
  
  lex.expect(';')
  
  return AstPrintStmt(token, body)

def parse_compound_stmt(lex):
  if not lex.match('{'):
    return AstCompoundStmt([ parse_stmt(lex) ])
  
  lex.expect('{')
  
  stmt = parse_stmt(lex)
  
  if not stmt:
    return None
  
  body = []
  
  while stmt:
    body.append(stmt)
    stmt = parse_stmt(lex)
  
  lex.expect('}')
  
  return AstCompoundStmt(body)

def parse_var(lex):
  var_type = parse_var_type(lex)
  
  if not var_type:
    return None
  
  name = lex.expect("Identifier")
  
  if not name:
    return None
  
  return AstVar(var_type, name)

def parse_var_type(lex):
  specifier = find_match([ lex.accept("int") ])
  
  if not specifier:
    return None
  
  var_type = TypeSpecifier(specifier)
  
  if lex.accept('['):
    size = lex.expect("Number")
    lex.expect(']')
    var_type = TypeArray(var_type, int(size.text))
  
  return var_type

def parse_expr(lex):
  body = find_match([ parse_binop(lex), parse_primitive(lex) ])
  
  if not body:
    return None
  
  return AstExpr(body)

def parse_binop(lex):
  return parse_binop_level(lex, 0)

def parse_binop_level(lex, level):
  op_set = [
    [ "=" ],
    [ "=" ],
    [ "==", "!=" ],
    [ ">=", "<=", "<", ">" ],
    [ "+", "-" ],
    [ "*", "/" ]
  ]
  
  if level == len(op_set):
    return parse_postfix(lex)
  
  lhs = parse_binop_level(lex, level + 1)
  
  op = find_match([ lex.accept(op) for op in op_set[level] ])
  
  if not op:
    return lhs
  
  rhs = parse_binop_level(lex, level)
  
  if not rhs:
    raise LexError(op, f"expected 'Expression' after '{op}' but found {lex.token.text}")
  
  return AstBinop(lhs, op, rhs)

def parse_postfix(lex):
  base = parse_primitive(lex)
  
  if lex.accept('['):
    pos = parse_expr(lex)
    lex.expect(']')
    return AstIndex(base, pos)
  
  return base

def parse_primitive(lex):
  if lex.match("Number"):
    return AstConstant(lex.pop())
  
  if lex.match("Identifier"):
    return AstIdentifier(lex.pop())
  
  if lex.accept("("):
    body = AstExpr(parse_expr(lex), bracket=True)
    lex.expect(")")
    return body
  
  return None
