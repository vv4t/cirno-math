from parse import BinopNode, NumberNode
from lex import Token

def simplify(node):
  return collapse_constant(node)

def collapse_constant(node):
  if not isinstance(node, BinopNode):
    return node
  
  node.lhs = collapse_constant(node.lhs)
  node.rhs = collapse_constant(node.rhs)
  
  op_dict = {
    '+': lambda a, b: a + b,
    '-': lambda a, b: a - b,
    '*': lambda a, b: a * b,
    '/': lambda a, b: a / b,
  }
  
  if isinstance(node.lhs, NumberNode) and isinstance(node.rhs, NumberNode):
    text = str(op_dict[node.op.token_type](node.lhs.number, node.rhs.number))
    return NumberNode(Token("Number", text))
  
  return node
