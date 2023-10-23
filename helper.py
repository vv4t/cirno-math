
def find_match(matches):
  if not any(matches):
    return None
  
  return next((match for match in matches if match is not None))
