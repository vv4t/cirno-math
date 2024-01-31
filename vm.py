
class VM:
  def __init__(self, code):
    self.opc = []
    self.lbl = {}
    self.stack = []
    self.pc = 0
    self.sp = 0
    
    for line in code:
      if line.startswith("__"):
        self.lbl[line[2:]] = len(self.opc)
      else:
        self.opc.append(line)
    
    print(self.lbl)
    
    for n, opc in zip(range(len(self.opc)), self.opc):
      print(n, opc)
  
  def run(self):
    while self.pc < len(self.opc):
      args = self.opc[self.pc].split()
      
      if args[0] == "push":
        self.stack.append(int(args[1]))
      elif args[0] == "rx":
        registers = {
          "$sp": self.sp,
          "$pc": self.pc
        }
        self.stack.append(registers[args[1]])
      elif args[0] == "add":
        b = self.stack.pop()
        a = self.stack.pop()
        self.stack.append(a + b)
      elif  args[0] == "sub":
        b = self.stack.pop()
        a = self.stack.pop()
        self.stack.append(a - b)
      elif args[0] == "mul":
        b = self.stack.pop()
        a = self.stack.pop()
        self.stack.append(a * b)
      elif args[0] == "div":
        b = self.stack.pop()
        a = self.stack.pop()
        self.stack.append(a / b)
      elif args[0] == "jle":
        b = self.stack.pop()
        a = self.stack.pop()
        if a <= b:
          self.pc = self.lbl[args[1]] - 1
      elif args[0] == "jge":
        b = self.stack.pop()
        a = self.stack.pop()
        if a >= b:
          self.pc = self.lbl[args[1]] - 1
      elif args[0] == "jlt":
        b = self.stack.pop()
        a = self.stack.pop()
        if a < b:
          self.pc = self.lbl[args[1]] - 1
      elif args[0] == "jgt":
        b = self.stack.pop()
        a = self.stack.pop()
        if a > b:
          self.pc = self.lbl[args[1]] - 1
      elif args[0] == "jmp":
        self.pc = self.lbl[args[1]] - 1
      elif args[0] == "load":
        a = self.stack.pop() // 4
        self.stack.append(self.stack[a])
      elif args[0] == "store":
        b = self.stack.pop()
        a = self.stack.pop() // 4
        self.stack[a] = b
      elif args[0] == "frame":
        a = int(args[1]) // 4
        self.stack += [0] * a
      elif args[0] == "print":
        b = self.stack.pop()
        print(">", b)
      else:
        print(args[0])
      
      self.pc += 1
