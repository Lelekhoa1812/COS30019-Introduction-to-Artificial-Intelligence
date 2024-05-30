import sys
import re
from itertools import product
from inference import evaluate_condition, generate_truth_table

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

def generic_truth_table(kb, facts, query):
    symbols = set()
    for condition, _, _ in kb:
        symbols.update(condition)
    symbols.update(facts)
    truth_table = generate_truth_table(symbols)

    # Organize the knowledge base by bracket levels
    bracket_kb = {}
    for entry in kb:
        if entry[2] not in bracket_kb:
            bracket_kb[entry[2]] = []
        bracket_kb[entry[2]].append(entry)

    for row in truth_table:
        for fact in facts:
            row[fact] = True

        # Evaluate bracketed knowledge base by levels
        for level in sorted(bracket_kb.keys()):
            bracket_results = {}
            for condition, result, _ in bracket_kb[level]:
                if condition == ('@',):
                    inner_conditions = []
                    for prev_level in range(level - 1, -1, -1):
                        for cond, res, _ in bracket_kb.get(prev_level, []):
                            if cond == ('@',):
                                inner_conditions.append(kb[0][0])
                            else:
                                inner_conditions.append(cond)
                    for inner_condition in inner_conditions:
                        # Handle disjunction kb
                        if any('*' in c for c in condition): # Look up for the disjunction component that has been remarked with '*' symbol individually
                            condition = tuple(c.replace('*', '') for c in condition) # Remove that '*' symbol by replace it with an empty string
                            if any(row.get(c, False) for c in condition):  # Ensure any (one or all) disjunction conditions are true
                                row[result] = True
                            condition = tuple(c for c in condition if c.strip()) # Strip (remove) any empty string '' from condition
                        # Handle non-disjunction kb
                        else:
                            if evaluate_condition(row, inner_condition):
                                bracket_results[result] = True
                else:
                    # Handle disjunction kb
                    if any('*' in c for c in condition): # Look up for the disjunction component that has been remarked with '*' symbol individually
                        condition = tuple(c.replace('*', '') for c in condition) # Remove that '*' symbol by replace it with an empty string
                        if any(row.get(c, False) for c in condition):  # Ensure any (one or all) disjunction conditions are true
                            row[result] = True
                        condition = tuple(c for c in condition if c.strip()) # Strip (remove) any empty string '' from condition
                    # Handle non-disjunction kb
                    else:
                        if evaluate_condition(row, condition):
                            bracket_results[result] = True

            for result in bracket_results:
                row[result] = True

    for level in sorted(bracket_kb.keys()):
        print(f"Bracket_kb_{level}: ", bracket_kb[level])

    if evaluate_condition(truth_table[-1], query):
        return f"> YES {len(bracket_kb)}"
    return "NO"

def generic_operator_table(part, kb, facts, level=0):
    for variable, symbol in universal_variables.items():
        part = part.replace(variable, symbol)

    if '(' in part:
        level += 1

    if '(' in part:
        while '(' in part:
            inner_parts = re.findall(r'\(([^()]+)\)', part)
            for inner_part in inner_parts:
                generic_operator_table(inner_part, kb, facts, level)
            part = re.sub(r'\(([^()]+)\)', '@', part)

    # Identify conditional operators (implication, deduction, biconditional)
    # Assertion conditional operators (negation, conjunction, disjunction) 
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

