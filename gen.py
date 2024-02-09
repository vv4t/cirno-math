from ast import *
from semantic import var_type_cmp

class CodeGen:
  def __init__(self, node):
    self.code = []
    self.lbl_name = 0
    self.lbl_main = 'label_main'
    self.scope = None
    self.ax = 0
    self.gen_body(node.body)
  
  def var_alloc(self, scope):
    for var in scope.var.values():
      if isinstance(var, AstVar):
        var.loc = scope.size
        scope.size += type_sizeof(var.var_type)
    
    for child in scope.child:
      child.size = scope.size
      self.var_alloc(child)
      scope.size = child.size
  
  def gen_body(self, node):
    for class_type in node.scope.class_type.values():
      self.var_alloc(class_type.scope)
      class_type.size = class_type.scope.size
    
    for class_type in node.scope.class_type.values():
      for method in class_type.methods:
        self.gen_func(method)
    
    for fn in node.scope.var.values():
      if isinstance(fn, AstFunc):
        self.gen_func(fn)
    
    self.scope = node.scope
    
    self.var_alloc(self.scope)
    self.emit_label(self.lbl_main)
    self.emit(f'frame {self.scope.size}')
    
    for stmt in node.body:
      self.gen_stmt(stmt)
    
    self.emit(f'end')
  
  def gen_func(self, fn):
    self.scope = fn.body.scope
    
    self.var_alloc(self.scope)
    
    fn.label = self.label()
    self.lbl_ret = self.label()
    
    param_size = 4 if self.scope.parent_class else 0
    
    self.emit_label(fn.label)
    self.emit(f'frame {self.scope.size + param_size}')
    
    for param in fn.params:
      param_size += type_sizeof(param.var_type)
    
    if param_size > 0:
      self.emit(f'param {param_size}')
      self.emit('rx $fp')
      self.emit(f'store {param_size}')
    
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
    
    for i in range(self.ax):
      self.emit('pop')
    
    self.ax = 0
  
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
    self.ax -= 1
  
  def gen_return_stmt(self, node):
    if node.body:
      type_size = type_sizeof(node.body.var_type)
      self.gen_expr(node.body)
      
      self.emit(f'arg {type_size}')
      
      self.ax -= type_size // 4
    
    self.emit(f'jmp {self.lbl_ret}')
  
  def gen_compound_stmt(self, node):
    for stmt in node.body:
      self.gen_stmt(stmt)
  
  def gen_lvalue(self, node):
    if isinstance(node, AstIdentifier):
      loc = self.scope.find(node.name).loc + (4 if self.scope.parent_class else 0)
      self.emit(f'push {loc}')
      self.emit(f'rx $fp')
      self.emit(f'add')
      self.ax += 1
    elif isinstance(node, AstIndex):
      self.gen_expr(node.pos)
      self.emit(f'push {type_sizeof(node.var_type)}')
      self.emit(f'mul')
      self.gen_expr(node.base)
      self.emit(f'add')
      self.ax -= 1
    elif isinstance(node, AstUnaryOp) and node.op == '*':
      self.gen_expr(node.body)
    elif isinstance(node, AstAccess):
      if node.direct:
        self.gen_lvalue(node.base)
        class_type = node.base.var_type.class_type
      else:
        self.gen_expr(node.base)
        class_type = node.base.var_type.base.class_type
      
      member = class_type.scope.find(node.name.text)
      
      self.emit(f'push {member.loc}')
      self.emit(f'add')
      
      self.ax -= 1
    else:
      raise Exception("gen error: not lvalue")

  def gen_expr(self, node):
    if isinstance(node, AstExpr):
      self.gen_expr(node.body)
    elif isinstance(node, AstBinop):
      self.gen_binop(node)
    elif isinstance(node, AstUnaryOp):
      self.gen_unary_op(node)
    elif isinstance(node, AstConstant):
      self.gen_constant(node)
    elif isinstance(node, AstCall):
      self.gen_call(node)
    elif isinstance(node, AstIdentifier) or isinstance(node, AstIndex) or isinstance(node, AstAccess):
      self.gen_value(node)
    elif isinstance(node, AstThis):
      self.gen_this(node)
    else:
      raise Exception("IDK THIS")

  def gen_this(self, node):
    if not self.scope.parent_class:
      raise Exception("NOT CLASS WHY??")
    
    self.emit("rx $fp")
    self.emit("load 4")

  def gen_value(self, node):
    type_size = type_sizeof(node.var_type)
    
    self.gen_lvalue(node)
    self.emit(f'load {type_size}')
    
    self.ax += type_size // 4
    self.ax -= 1

  def gen_unary_op(self, node):
    if node.op == '-':
      self.gen_expr(node.body)
      self.emit("push -1")
      self.emit("mul")
    if node.op == '&':
      self.gen_lvalue(node.body)
    elif node.op == '*':
      self.gen_lvalue(node)
      self.emit('load')
    else:
      raise Exception("IDK THIS")

  def gen_call(self, node):
    if isinstance(node.base, AstIdentifier):
      fn = self.scope.find(node.base.name)
    elif isinstance(node.base, AstAccess):
      if node.base.direct:
        fn = node.base.base.var_type.class_type.scope.find(node.base.name.text)
      else:
        fn = node.base.base.var_type.base.class_type.scope.find(node.base.name.text)
    
    if not fn:
      raise Excpetion("CANT FIND FUNCTION!!!!")
    
    mk_tmp = isinstance(node.base, AstAccess) and node.base.direct and not ast_lvalue(node.base.base)   
    
    if mk_tmp:
      self.emit("rx $sp")
      self.emit("arg 4")
      self.gen_expr(node.base.base)
    
    arg_size = 0
    
    if isinstance(node.base, AstAccess):
      if node.base.direct:
        if ast_lvalue(node.base.base):
          self.gen_lvalue(node.base.base)
        else:
          self.emit("param 4")
          self.ax += 1
      else:
        self.gen_expr(node.base.base)
      
      arg_size += 4
    
    for arg in node.args:
      self.gen_expr(arg)
      arg_size += type_sizeof(arg.var_type)
    
    if arg_size > 0:
      self.emit(f'arg {arg_size}')
    
    self.ax -= arg_size // 4
    
    self.emit(f"call {fn.label}")
    
    if mk_tmp:
      for i in range(type_sizeof(node.base.base.var_type) // 4):
        self.emit('pop')
        self.ax -= 1
    
    if fn.var_type:
      type_size = type_sizeof(fn.var_type)
      self.emit(f"param {type_size}")
      self.ax += type_size // 4

  def gen_constant(self, node):
    self.emit(f'push {node.value}')
    self.ax += 1
  
  def gen_cmp_cond(self, node, lbl_end, lbl_else=None):
    if not lbl_else:
      lbl_else = lbl_end
    
    self.gen_expr(node.lhs)
    self.gen_expr(node.rhs)
    
    if node.op == ">":
      self.emit(f'jle {lbl_else}')
    elif node.op == ">=":
      self.emit(f'jlt {lbl_else}')
    elif node.op == "<":
      self.emit(f'jge {lbl_else}')
    elif node.op == "<=":
      self.emit(f'jgt {lbl_else}')
    
    self.ax -= 2
  
  def gen_binop(self, node):
    if (
      var_type_cmp(node.lhs.var_type, TypeSpecifier("int")) and
      var_type_cmp(node.rhs.var_type, TypeSpecifier("int")) or
      (
        isinstance(node.lhs.var_type, TypePointer) and
        isinstance(node.rhs.var_type, TypePointer) and
        var_type_cmp(node.lhs.var_type.base, node.rhs.var_type.base)
      )
    ):
      self.gen_binop_int_int(node)
    elif (
      isinstance(node.lhs.var_type, TypeSpecifier) and
      isinstance(node.rhs.var_type, TypeSpecifier) and
      node.lhs.var_type.class_type.name == node.rhs.var_type.class_type.name
    ):
      self.gen_binop_class_class(node)
    else:
      raise Exception("IDK!!!")
  
  def gen_binop_class_class(self, node):
    if node.op == "=":
      type_size = type_sizeof(node.var_type)
      
      self.gen_expr(node.rhs)
      self.gen_lvalue(node.lhs)
      
      self.emit(f'store {type_size}')
      
      self.ax -= type_size // 4
      self.ax -= 1
    else:
      raise Exception("IDK!!!")
  
  def gen_binop_int_int(self, node):
    if node.op == "=":
      self.gen_expr(node.rhs)
      self.gen_lvalue(node.lhs)
      self.emit('store 4')
      self.ax -= 2
    elif node.op == ">" or node.op == "<" or node.op == ">=" or node.op == "<=":
      lbl_end = self.label()
      lbl_else = self.label()
      
      self.gen_cmp_cond(node, lbl_else, lbl_end)
      self.emit("push 1")
      self.emit(f'jmp {lbl_end}')
      self.emit_label(lbl_else)
      self.emit("push 0")
      self.emit_label(lbl_end)
      
      self.ax += 1
    else:
      self.gen_expr(node.lhs)
      self.gen_expr(node.rhs)
      
      if node.op == "+":
        self.emit("add")
      elif node.op == "-":
        self.emit("sub")
      elif node.op == "*":
        self.emit("mul")
      elif node.op == "/":
        self.emit("div")
      else:
        raise Exception("I DONT KNOW THIS ONE!!!")
      
      self.ax -= 1
  
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
    elif var_type.specifier == "class":
      return var_type.class_type.size
  elif isinstance(var_type, TypeArray):
    return var_type.size * type_sizeof(var_type.base)
  elif isinstance(var_type, TypePointer):
    return 4
  else:
    print(var_type)
    raise Exception("I DONT KNOW THIS ONE!!!")
