from ast import *
from semantic import var_type_cmp

class CodeGen:
  def __init__(self, node):
    self.code = []
    self.lbl_name = 0
    self.lbl_main = 'label_main'
    self.scope = None
    self.gen_body(node.body)
  
  def var_alloc(self, scope, size):
    for var in scope.var.values():
      if isinstance(var, AstVar):
        var.loc = size
        size += type_sizeof(var.var_type)
    
    for child in scope.child:
      size += self.var_alloc(child, size)
    
    return size
  
  def gen_body(self, node):
    for fn in node.scope.var.values():
      if isinstance(fn, AstFunc):
        self.gen_func(fn)
    
    self.scope = node.scope
    size = self.var_alloc(self.scope, 0)
    self.emit_label(self.lbl_main)
    self.emit(f'frame {size}')
    
    for stmt in node.body:
      self.gen_stmt(stmt)
  
  def gen_func(self, fn):
    size = self.var_alloc(fn.body.scope, 0)
    
    fn.label = self.label()
    self.lbl_ret = self.label()
    self.scope = fn.body.scope
    
    self.emit_label(fn.label)
    self.emit(f'frame {size}')
    
    loc = 0
    for param in reversed(fn.params):
      self.emit(f'push {loc}')
      self.emit("rx $fp")
      self.emit("add")
      self.emit("param")
      self.emit("store")
      loc += type_sizeof(param.var_type)
    
    self.gen_compound_stmt(fn.body)
    
    self.emit_label(self.lbl_ret)
    self.emit(f'end')
    self.emit(f'ret')
  
  def gen_stmt(self, node):
    if isinstance(node, AstPrintStmt):
      self.gen_print_stmt(node)
    elif isinstance(node, AstReturnStmt):
      self.gen_return_stmt(node)
    elif isinstance(node, AstIfStmt):
      self.gen_if_stmt(node)
    elif isinstance(node, AstWhileStmt):
      self.gen_while_stmt(node)
    elif isinstance(node, AstForStmt):
      self.gen_for_stmt(node)
    elif isinstance(node, AstStmt):
      if isinstance(node.body, AstExpr):
        self.gen_expr(node.body)
      else:
        raise Exception("NOT DONE YET BAKA")
    else:
      raise Exception("NOT DONE YET BAKA")
  
  def gen_if_stmt(self, node):
    lbl_end = self.label()

    self.scope = node.body.scope
    
    self.gen_cmp_cond(node.cond, lbl_end)
    self.gen_compound_stmt(node.body)
    self.emit_label(lbl_end)
    
    self.scope = node.body.scope.parent
  
  def gen_while_stmt(self, node):
    lbl_cond = self.label()
    lbl_end = self.label()
    
    self.scope = node.body.scope
    
    self.emit_label(lbl_cond)
    self.gen_cmp_cond(node.cond, lbl_end)
    self.gen_compound_stmt(node.body)
    self.emit(f'jmp {lbl_cond}')
    self.emit_label(lbl_end)
    
    self.scope = node.body.scope.parent
  
  def gen_for_stmt(self, node):
    self.scope = node.body.scope
    
    if len(node.init) > 0:
      for stmt in node.init:
        self.gen_stmt(stmt)
    
    lbl_cond = self.label()
    lbl_end = self.label()
    
    self.emit_label(lbl_cond)
    self.gen_cmp_cond(node.cond, lbl_end)
    
    self.gen_compound_stmt(node.body)
    
    self.gen_expr(node.step)
    self.emit(f'jmp {lbl_cond}')
    
    self.emit_label(lbl_end)
    
    self.scope = node.body.scope.parent
  
  def gen_print_stmt(self, node):
    self.gen_expr(node.body)
    self.emit('print')
  
  def gen_return_stmt(self, node):
    if node.body:
      self.gen_expr(node.body)
      self.emit('arg')
    self.emit(f'jmp {self.lbl_ret}')
  
  def gen_compound_stmt(self, node):
    for stmt in node.body:
      self.gen_stmt(stmt)
  
  def gen_lvalue(self, node):
    if isinstance(node, AstIdentifier):
      loc = self.scope.find(node.name).loc
      self.emit(f'push {loc}')
      self.emit(f'rx $fp')
      self.emit(f'add')
    elif isinstance(node, AstIndex):
      self.gen_expr(node.pos)
      self.emit(f'push {type_sizeof(node.var_type)}')
      self.emit(f'mul')
      self.gen_lvalue(node.base)
      self.emit(f'add')
    else:
      raise Exception("gen error: not lvalue")

  def gen_expr(self, node):
    if isinstance(node, AstExpr):
      self.gen_expr(node.body)
    elif isinstance(node, AstBinop):
      self.gen_binop(node)
    elif isinstance(node, AstConstant):
      self.gen_constant(node)
    elif isinstance(node, AstCall):
      self.gen_call(node)
    elif isinstance(node, AstIdentifier) or isinstance(node, AstIndex):
      self.gen_lvalue(node)
      self.emit('load')
    else:
      raise Exception("IDK THIS")

  def gen_call(self, node):
    fn = self.scope.find(node.base.name)
    
    if not fn:
      raise Excpetion("CANT FIND FUNCTION!!!!")
    
    for arg in node.args:
      self.gen_expr(arg)
      self.emit(f"arg")
    
    self.emit(f"call {fn.label}")
    self.emit(f"param")

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
    if var_type_cmp(node.lhs.var_type, TypeSpecifier("int")) and var_type_cmp(node.rhs.var_type, TypeSpecifier("int")):
      self.gen_binop_int_int(node)
    else:
      raise Exception("IDK!!!")
  
  def gen_binop_int_int(self, node):
    if node.op.text == "=":
      self.gen_lvalue(node.lhs)
      self.gen_expr(node.rhs)
      self.emit('store')
    elif node.op.text == ">" or node.op.text == "<" or node.op.text == ">=" or node.op.text == "<=":
      lbl_end = self.label()
      lbl_else = self.label()
      
      self.gen_cmp_cond(node, lbl_else, lbl_end)
      self.emit("push 1")
      self.emit(f'jmp {lbl_end}')
      self.emit_label(lbl_else)
      self.emit("push 0")
      self.emit_label(lbl_end)
    else:
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
  else:
    raise Exception("I DONT KNOW THIS ONE!!!")
