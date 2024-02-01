
def find_match(matches):
  for match in matches:
    res = match()
    
    if res:
      return res
  
  return None
