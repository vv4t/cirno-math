from lex import Lex
from parse import parse
from cirno_math import simplify

import sys

for line in sys.stdin:
  lex = Lex(line.rstrip())
  node = parse(lex)
  
  node = simplify(node)
  
  print(node)
