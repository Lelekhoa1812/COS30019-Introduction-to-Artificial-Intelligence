import re
from itertools import product

# Define a dictionary for universal variables.
# Convert the definition to standard operators.
# This way, if a test file uses symbol with the same meaning, they will be treated the same.
universal_variables = {
    '^':  '&',   '∧': '&',  # Conjuction (and)
    '|': '||',              # Disjunction (or)
    '¬':  '~',   '!': '~',  # Negation (not)
    '->': '=>',  '→': '=>', # Implication
    '<-': '<=',  '←': '<=', # Deduction 
    '<=>':'<->', '↔': '<->',# Biconditional 
}

# Operator used for TT method to set facts as from part
def operator_table(part, kb, facts):
    # Check and read universal symbol, if used in the test file.
    for variable, symbol in universal_variables.items():
        part = part.replace(variable, symbol)
    # Identify conditional operators (implication, deduction, biconditional)
    # Assertion conditional operators (negation, conjunction, disjunction) 
    if '=>' in part: # Implication Operator
        parts = part.split('=>')  # Split only once at the first occurrence
        if '&' in parts[0]: # For conjunction operator, strip left component by parts with & symbol in between, parts at index 1 is the right component
            left = tuple([c.strip() for c in parts[0].split('&')]) 
            right = parts[1].strip()
            kb.append((left, right))
        elif '||' in parts[0]: # For disjunction operator, split them similarly to conjunction at first
            left = tuple(['*' + c.strip() if c.strip() else c.strip() for c in parts[0].split('||')]) # Remark disjunction parameter with a '*' symbol
            right = parts[1].strip()
            kb.append((left, right)) 
        elif '~' in parts[0]: # For negation operator
            fact = parts[0].strip('~').strip # Strip negation component
            if fact:
                kb.append(fact, False) # Append false value to kb      
        else: # Neither conjunction nor disjunction, just strip left and right component by parts with the operator symbol in between
            left = tuple(c.strip() for c in parts[0].split('=>'))
            right = parts[1].strip()
            kb.append((left, right))
    elif '<=' in part: # Deduction Operator
        parts = part.split('<=')  # Split only once at the first occurrence
        if '&' in parts[1]: # For conjunction operator, strip right component by parts with & symbol in between, parts at index 1 is the left component
            right = tuple([c.strip() for c in parts[1].split('&')])
            left = parts[0].strip()
            kb.append((right, left))
        elif '||' in parts[1]: # For disjunction operator, split them similarly to conjunction at first
            right = tuple(['*' + c.strip() if c.strip() else c.strip() for c in parts[1].split('||')]) # Remark disjunction parameter with a '*' symbol
            left = parts[0].strip()
            kb.append((right, left))
        elif '~' in parts[1]: # For negation operator
            fact = parts[0].strip('~').strip # Strip negation component
            if fact:
                kb.append(fact, False) # Append false value to kb
        else: # Neither conjunction nor disjunction, just strip right and left component by parts with the operator symbol in between
            right = tuple(c.strip() for c in parts[1].split('<='))
            left = parts[0].strip()
            kb.append((right, left))
    elif '<->' in part: # Biconditional Operator
        if '&' in part: # For conjunction operator
            parts = part.split('<->')  # Split only once at the first occurrence
            left = tuple([c.strip() for c in parts[0].split('&')])
            right = parts[1].strip()
            kb.append((left, right))
            kb.append((tuple(right.split('&')), left))  # Add the converse implication to make sure it append both way (implicate then deduct)
        elif '||' in part: # For disjunction operator
            parts = part.split('<->')  # Split only once at the first occurrence
            left = tuple(['*' + c.strip() if c.strip() else c.strip() for c in parts[0].split('||')]) # Remark disjunction parameter with a '*' symbol
            right = parts[1].strip()
            kb.append((left, right))
            kb.append((tuple(right.split('||')), left))  # Add the converse implication to make sure it append both way (implicate then deduct)
        elif '~' in part: # For negation operator
            fact = part.strip('~').strip # Strip negation component
            if fact:
                kb.append(fact, False) # Append false value to kb
        else: # Neither conjunction nor disjunction
            parts = part.split('<->')  # Split only once at the first occurrence
            left = tuple([c.strip() for c in parts[0].split('<->')])
            right = parts[1].strip()
            kb.append((left, right))
            kb.append((tuple(right.split('<->')), left))  # Add the converse implication to make sure it append both way (implicate then deduct)
    else:
        facts.add(part)
        facts.discard('') # Filter out the empty string as the first module (goal state, which returns as null) should not be appended to the facts count
    return part, facts 

# Operator used for FC and BC methods to set facts as from part
def operator_chain(part, method, kb, facts):
    # Check and read universial symbol, if used in the test file
    for variable, symbol in universal_variables.items():
        part = part.replace(variable, symbol)
    # Print error message when a generic KB (not in Horn-form) is applied for FC and BC method.
    if '(' in part:
        print("Generic KB is not applicable to FC and BC method. Cannot use bracket.")
        return
    if '||' in part:
        print("Generic KB is not applicable to FC and BC method. Cannot use disjunction connective.")
        return
    if '~' in part:
        print("Generic KB is not applicable to FC and BC method. Cannot use negation operator.")
        return
    # Identify conditional operators (implication, deduction, biconditional)
    # Assertion conditional operators (negation, conjunction, disjunction)
    if '=>' in part:  # Implication Operator
        left, right = part.split('=>')
        left_parts = left.split('&')
        left_parts2 = []
        for c in left_parts:
            left_parts2.append(c.strip())
        condition = tuple(left_parts2)
        if method == "FC":
            kb[condition] = right.strip()
        elif method == "BC":
            kb.setdefault(right.strip(), []).append(condition)
    elif '<=' in part:  # Deduction Operator
        right, left = part.split('<=')
        right_parts = right.split('&')
        right_parts2 = []
        for c in right_parts:
            right_parts2.append(c.strip())
        condition = tuple(right_parts2)
        if method == "FC":
            kb[condition] = left.strip()
        elif method == "BC":
            kb.setdefault(left.strip(), []).append(condition)
    elif '<->' in part:  # Biconditional Operator
        left, right = part.split('<->')
        left_parts = left.split('&')
        left_parts2 = []
        for c in left_parts:
            left_parts2.append(c.strip())
        right_parts = right.split('&')
        right_parts2 = []
        for c in right_parts:
            right_parts2.append(c.strip())
        condition_left = tuple(left_parts2)
        condition_right = tuple(right_parts2)
        if method == "FC":
            kb[condition_left] = right.strip()  # Implication fist
            # Then deduction for biconditional
            kb[condition_right] = left.strip()
        elif method == "BC":
            kb.setdefault(right.strip(), []).append(
                condition_left)  # Implication fist
            kb.setdefault(left.strip(), []).append(
                condition_right)  # Then deduction for biconditional
    else:
        facts.add(part)
    return kb, facts

# Operator used for generic TT method (with bracket rules applied) to set facts as from part
# Note that this function can also be applied to a kb that does not have a bracket, however, there must be at least one of them to have the bracket within that test case, else it would return error
# This function has the additional parameter of level (1 or 0), indicating if the part is inside a bracket (1), or not (0)
def generic_operator_table(part, kb, facts, level=0):
    for variable, symbol in universal_variables.items():
        part = part.replace(variable, symbol)
    if '(' in part: # Key difference of this function to the regular TT function is that it increment the bracket level for each time it locates a bracket
        level += 1  # Therefore, the component inside the bracket will be set as level 1, which allow the function to prioritise handling parts without the bracket first
        while '(' in part: # running the loop for bracket case
            inner_parts = re.findall(r'\(([^()]+)\)', part) # Find all inside a bracket, which we set them as the inner_parts
            for inner_part in inner_parts: # Irritate over each inner_part
                generic_operator_table(inner_part, kb, facts, level) # Call the function to run the loop once again with the inner_part extracted, while we have append the level to be 1
            part = re.sub(r'\(([^()]+)\)', '@', part) # Substitute the previous part as @, which that inner part after being evaluated (T/F), will set @ character's value to be T/F
    # Identify conditional operators (implication, deduction, biconditional)
    # Assertion conditional operators (negation, conjunction, disjunction) 
    # Note that this will differ to the regular TT function as the kb appended has the level parameter (0/1) as defined
    if '=>' in part: # Implication Operator
        parts = part.split('=>', 1)  # Split only once at the first occurrence
        if '&' in parts[0]: # For conjunction operator, strip left component by parts with & symbol in between, parts at index 1 is the right component
            left = tuple([c.strip() for c in parts[0].split('&')]) 
            right = parts[1].strip()
            kb.append((left, right, level))
        elif '||' in parts[0]: # For disjunction operator, split them similarly to conjunction at first
            left = tuple(['*' + c.strip() if c.strip() else c.strip() for c in parts[0].split('||')]) # Remark disjunction parameter with a '*' symbol
            right = parts[1].strip()
            kb.append((left, right, level)) 
        elif '~' in parts[0]: # For negation operator
            fact = parts[0].strip('~').strip # Strip negation component
            if fact:
                kb.append(fact, False, level) # Append false value to kb      
        else: # Neither conjunction nor disjunction, just strip left and right component by parts with the operator symbol in between
            left = tuple(c.strip() for c in parts[0].split('=>'))
            right = parts[1].strip()
            kb.append((left, right, level))
    elif '<=' in part: # Deduction Operator
        parts = part.split('<=', 1)  # Split only once at the first occurrence
        if '&' in parts[1]: # For conjunction operator, strip right component by parts with & symbol in between, parts at index 1 is the left component
            right = tuple([c.strip() for c in parts[1].split('&')])
            left = parts[0].strip()
            kb.append((right, left), level)
        elif '||' in parts[1]: # For disjunction operator, split them similarly to conjunction at first
            right = tuple(['*' + c.strip() if c.strip() else c.strip() for c in parts[1].split('||')]) # Remark disjunction parameter with a '*' symbol
            left = parts[0].strip()
            kb.append((right, left), level)
        elif '~' in parts[1]: # For negation operator
            fact = parts[0].strip('~').strip # Strip negation component
            if fact:
                kb.append(fact, False, level) # Append false value to kb
        else: # Neither conjunction nor disjunction, just strip right and left component by parts with the operator symbol in between
            right = tuple(c.strip() for c in parts[1].split('<='))
            left = parts[0].strip()
            kb.append((right, left, level))
    elif '<->' in part: # Biconditional Operator
        if '&' in part: # For conjunction operator
            parts = part.split('<->', 1)  # Split only once at the first occurrence
            left = tuple([c.strip() for c in parts[0].split('&')])
            right = parts[1].strip()
            kb.append((left, right, level))
            kb.append((tuple(right.split('&')), left, level))  # Add the converse implication to make sure it append both way (implicate then deduct)
        elif '||' in part: # For disjunction operator
            parts = part.split('<->', 1)  # Split only once at the first occurrence
            left = tuple(['*' + c.strip() if c.strip() else c.strip() for c in parts[0].split('||')]) # Remark disjunction parameter with a '*' symbol
            right = parts[1].strip()
            kb.append((left, right, level))
            kb.append((tuple(right.split('||')), left, level))  # Add the converse implication to make sure it append both way (implicate then deduct)
        elif '~' in part: # For negation operator
            fact = part.strip('~').strip # Strip negation component
            if fact:
                kb.append(fact, False, level) # Append false value to kb
        else: # Neither conjunction nor disjunction
            parts = part.split('<->', 1)  # Split only once at the first occurrence
            left = tuple([c.strip() for c in parts[0].split('<->')])
            right = parts[1].strip()
            kb.append((left, right, level))
            kb.append((tuple(right.split('<->')), left, level))  # Add the converse implication to make sure it append both way (implicate then deduct)
    else:
        facts.add(part)
        facts.discard('') # Filter out the empty string as the first module (goal state, which returns as null) should not be appended to the facts count
    return part, facts 

def DPLL_propagate_unit_clauses(kb, facts):
    # Propagate unit clauses (clauses with a single literal)
    changed = True
    while changed: # Repeats the process while changes are being made.
        changed = False
        unit_clauses = [clause for clause in kb if len(clause.split('∨')) == 1] # Finds all unit clauses.
        for clause in unit_clauses:
            literal = clause.strip() # Strip white space
            if literal.startswith('¬'):
                literal = literal[1:] # Remove literal
                if literal in facts:
                    continue
                if literal not in facts:
                    facts.add('¬' + literal)  # Add negated literal to facts
                    kb = {cl for cl in kb if literal not in cl}  # Remove satisfied clauses
                    changed = True
            else:
                if '¬' + literal in facts:
                    continue
                if literal not in facts:
                    facts.add(literal)  # Add literal to facts
                    kb = {cl for cl in kb if '¬' + literal not in cl}  # Remove satisfied clauses
                    changed = True
    return kb, facts