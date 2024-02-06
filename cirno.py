from vm import VM
from lex import Lex, LexError
from parse import Parse
from gen import CodeGen
from semantic import semantic_pass, SemanticError

try:
  lex = Lex("main.9c")
  node = Parse(lex).parse()

  node = semantic_pass(node)

  code_gen = CodeGen(node)
  
  vm = VM(code_gen.code)
  # vm.dump()
  vm.run()
except (LexError, SemanticError) as e:
  print(e)
