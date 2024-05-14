import re
from itertools import product

# Define a dictionary for universal variables.
# Convert the definition to standard operators.
# This way, if a test file uses symbol with the same meaning, they will be treated the same.
universal_variables = {
    '^': '&',  # Conjuction (and) - add extra symbol (∧)
    'v': '||',  # Disjunction (or) - add extra symbol (/)
    '¬': '~',  # Negation (not) - add extra symbol (∧)
    '->': '=>',  # Implication - add extra symbol (→)
    '<-': '<=',  # Deduction - add extra symbol (←)
    '<->': '<=>'  # Biconditional - add extra symbol (↔)
}


def operator_table(part, kb, facts):
    # Check and read universal symbol, if used in the test file.
    for variable, symbol in universal_variables.items():
        part = part.replace(variable, symbol)
    # Handle brackets, by which we run the table operator function loop once more with the part component inside the bracket.
    while '(' in part:
        brackets = re.findall(r'\(([^()]+)\)', part)  # Find all contents within brackets
        for bracket in brackets:
            result, _ = operator_table(bracket, kb, facts)  # Recursively evaluate expression within brackets
            part = part.replace(f'({bracket})', result)  # Replace bracketed expression with its result
            print("Current part:", part) # Debug keep tracking on the part result once relocate bracket
    # Identify conditional operators (implication, deduction, biconditional)
    # Assertion conditional operators (negation, conjunction, disjunction)
    if '=>' in part: # Implication Operator
        parts = part.split('=>', 1)  # Split only once at the first occurrence
        left = tuple([c.strip() for c in parts[0].split('&')])
        right = parts[1].strip()
        kb.append((left, right)) 
    elif '<=' in part: # Deduction Operator
        parts = part.split('<=', 1)  # Split only once at the first occurrence
        right = tuple([c.strip() for c in parts[0].split('&')])
        left = parts[1].strip()
        kb.append((right, left))   
    elif '<=>' in part: # Biconditional Operator
        parts = part.split('<=>', 1)  # Split only once at the first occurrence
        left = tuple([c.strip() for c in parts[0].split('&')])
        right = parts[1].strip()
        kb.append((left, right))
        kb.append((tuple(right.split('&')), left))  # Add the converse implication to make sure it append both way (implicate then deduct).
    else:
        facts.add(part)
        facts.discard('') # Filter out the empty string as the first module (goal state, which returns as null) should not be appended to the facts count.
    return part, facts 


# Operator used for FC and BC to set facts as from part
def operator_chain(part, method, kb, facts):
    # Check and read universial symbol, if used in the test file.
    for variable, symbol in universal_variables.items():
        part = part.replace(variable, symbol)
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
    elif '<=>' in part:  # Biconditional Operator
        left, right = part.split('<=>')
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
        # Imagine FC method uses a similar approach to BFS,
        # It may have to expand all nodes to deeper level.
        if method == "FC":
            facts.add(part)
        # BC however WILL NOT apply this, treat they as DFS, which way in this case, the module expanded is correspond to 1 given route.
        # Other modules are redundant.
    return kb, facts
