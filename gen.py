from ast import *

class CodeGen:
  def __init__(self, node):
    self.var = {}
    self.stack_size = 0
    self.code = []
    self.lbl_name = 0
    self.gen_body(node.body)
  
  def gen_body(self, node):
    for var in node.var.values():
      self.var[var.name.text] = self.stack_size
      self.stack_size += type_sizeof(var.var_type)
    
    self.emit(f'frame {self.stack_size}')
    
    for stmt in node.body:
      self.gen_stmt(stmt)
  
  def gen_stmt(self, node):
    if isinstance(node, AstPrintStmt):
      self.gen_print_stmt(node)
    elif isinstance(node, AstIfStmt):
      self.gen_if_stmt(node)
    elif isinstance(node.body, AstAssign):
      self.gen_assign(node.body)
    elif isinstance(node, AstStmt):
      if isinstance(node.body, AstExpr):
        self.gen_expr(node.body)
    else:
      raise Exception("NOT DONE YET BAKA")
  
  def gen_if_stmt(self, node):
    lbl_end = self.label()
    lbl_else = self.label()
    
    self.gen_cmp_cond(node.cond, lbl_end)
    self.gen_compound_stmt(node.body)
    self.emit_label(lbl_end)
  
  def gen_print_stmt(self, node):
    self.gen_expr(node.body)
    self.emit('print')
  
  def gen_compound_stmt(self, node):
    for stmt in node.body:
      self.gen_stmt(stmt)
  
  def gen_assign(self, node):
    self.gen_lvalue(node.lvalue)
    self.gen_expr(node.value)
    self.emit('store')

  def gen_lvalue(self, node):
    if isinstance(node, AstIdentifier):
      loc = self.var[node.identifier]
      self.emit(f'push {loc}')
      self.emit(f'rx $sp')
      self.emit(f'add')
    elif isinstance(node, AstIndex):
      self.gen_expr(node.pos)
      self.emit(f'push {type_sizeof(node.var_type)}')
      self.emit(f'mul')
      self.gen_lvalue(node.base)
      self.emit(f'add')
    else:
      self.emit("gen error: not lvalue")

  def gen_expr(self, node):
    if isinstance(node, AstExpr):
      self.gen_expr(node.body)
    elif isinstance(node, AstBinop):
      self.gen_binop(node)
    elif isinstance(node, AstConstant):
      self.gen_constant(node)
    elif isinstance(node, AstIdentifier) or isinstance(node, AstIndex):
      self.gen_lvalue(node)
      self.emit('load')

  def gen_constant(self, node):
    self.emit(f'push {node.value}')
  
  def gen_cmp_cond(self, node, lbl_end, lbl_else=None):
    if not lbl_else:
      lbl_else = lbl_end
    
    self.gen_expr(node.lhs)
    self.gen_expr(node.rhs)
    
    if node.op.text == ">":
      self.emit(f'jle {lbl_else}')
    elif node.op.text == ">=":
      self.emit(f'jlt {lbl_else}')
    elif node.op.text == "<":
      self.emit(f'jge {lbl_else}')
    elif node.op.text == "<=":
      self.emit(f'jgt {lbl_else}')
  
  def gen_binop(self, node):
    if node.op.text == ">" or node.op.text == "<" or node.op.text == ">=" or node.op.text == "<=":
      lbl_end = self.label()
      lbl_else = self.label()
      
      self.gen_cmp_cond(node, lbl_else, lbl_end)
      self.emit("push 1")
      self.emit(f'jmp {lbl_end}')
      self.emit_label(lbl_else)
      self.emit("push 0")
      self.emit_label(lbl_end)
      
      return
    
    self.gen_expr(node.lhs)
    self.gen_expr(node.rhs)
      
    if node.op.text == "+":
      self.emit("add")
    elif node.op.text == "-":
      self.emit("sub")
    elif node.op.text == "*":
      self.emit("mul")
    elif node.op.text == "/":
      self.emit("div")
    else:
      raise Exception("I DONT KNOW THIS ONE!!!")
  
  def label(self):
    self.lbl_name += 1
    return f'label_{self.lbl_name}'
  
  def emit_label(self, label):
    self.code.append(f'__{label}')
  
  def emit(self, text):
    self.code.append(text)

def type_sizeof(var_type):
  if isinstance(var_type, TypeSpecifier):
    if var_type.specifier == "int":
      return 4
  elif isinstance(var_type, TypeArray):
    return var_type.size * type_sizeof(var_type.base)
