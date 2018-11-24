
def subsequence_group(iterable, group_length):
    
    group_out = []
    
    for item in iterable:
        if len(group_out) == group_length:
            group_out.pop(0)
            
        group_out.append(item)
        
        if len(group_out) == group_length:
            yield tuple(group_out)
            
    if len(group_out) == group_length:
        raise StopIteration()
        
    # This happens if the iterable has fewer than group_length items.
    # Pad with None values
    while len(group_out) < group_length:
        group_out.append(None) 
        
    yield tuple(group_out)
    
        
