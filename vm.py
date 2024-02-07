
class VM:
  def __init__(self, code):
    self.opc = []
    self.lbl = {}
    self.stack = [0] * 128
    self.frame = []
    self.call = []
    self.arg = []
    self.pc = 0
    self.sp = 0
    self.fp = 0
    
    for line in code:
      if line.startswith("__"):
        self.lbl[line[2:]] = len(self.opc)
      else:
        self.opc.append(line)
  
  def dump(self):
    for label, pos in self.lbl.items():
      print(f'{label}: {pos}')
    
    for n, opc in zip(range(len(self.opc)), self.opc):
      print(n, opc)
  
  def push(self, n):
    self.stack[self.sp // 4] = n
    self.sp += 4
  
  def pop(self):
    self.sp -= 4
    return self.stack[self.sp // 4]
  
  def run(self):
    self.pc = self.lbl['label_main']
    
    while self.pc < len(self.opc):
      args = self.opc[self.pc].split()
      
      if args[0] == "push":
        self.push(int(args[1]))
      elif args[0] == "pop":
        self.pop()
      elif args[0] == "rx":
        registers = {
          "$fp": self.fp,
          "$sp": self.sp,
          "$pc": self.pc
        }
        self.push(registers[args[1]])
      elif args[0] == "add":
        b = self.pop()
        a = self.pop()
        self.push(a + b)
      elif  args[0] == "sub":
        b = self.pop()
        a = self.pop()
        self.push(a - b)
      elif args[0] == "mul":
        b = self.pop()
        a = self.pop()
        self.push(a * b)
      elif args[0] == "div":
        b = self.pop()
        a = self.pop()
        self.push(a // b)
      elif args[0] == "jle":
        b = self.pop()
        a = self.pop()
        if a <= b:
          self.pc = self.lbl[args[1]] - 1
      elif args[0] == "jge":
        b = self.pop()
        a = self.pop()
        if a >= b:
          self.pc = self.lbl[args[1]] - 1
      elif args[0] == "jlt":
        b = self.pop()
        a = self.pop()
        if a < b:
          self.pc = self.lbl[args[1]] - 1
      elif args[0] == "jgt":
        b = self.pop()
        a = self.pop()
        if a > b:
          self.pc = self.lbl[args[1]] - 1
      elif args[0] == "jmp":
        self.pc = self.lbl[args[1]] - 1
      elif args[0] == "load":
        a = self.pop() // 4
        self.push(self.stack[a])
      elif args[0] == "store":
        b = self.pop()
        a = self.pop() // 4
        self.stack[a] = b
      elif args[0] == "frame":
        a = int(args[1])
        fp = self.fp
        self.fp = self.sp
        self.sp += a
        self.frame.append(fp)
      elif args[0] == "end":
        a = self.frame.pop()
        self.sp = self.fp
        self.fp = a
      elif args[0] == "call":
        self.call.append(self.pc)
        self.pc = self.lbl[args[1]] - 1
      elif args[0] == "ret":
        a = self.call.pop()
        self.pc = a
      elif args[0] == "arg":
        a = self.pop()
        self.arg.append(a)
      elif args[0] == "param":
        self.push(self.arg.pop())
      elif args[0] == "print":
        b = self.pop()
        print(">", b)
      else:
        print(args[0])
      
      # info = ' '.join([ (f"[{x}]" if y == self.sp else f"{x}") for x, y in zip(self.stack, range(len(self.stack))) ])
      # print(' '.join(args), ">")
      # print("  " + info)
      
      self.pc += 1
    
    # print("$sp:", self.sp)
