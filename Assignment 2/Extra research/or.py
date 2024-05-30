import re
from itertools import product

# Universal variables, if needed (example provided here, update as necessary)
universal_variables = {
    '=>': '=>',
    '<=': '<=',
    '<=>': '<=>',
    '&': '&',
    '||': '||',
    '~': '~'
}

# TRUTH TABLE PARSER
def table_reader(filename):
    with open(filename, 'r') as file:
        lines = file.read().split('\n')
    kb = []
    facts = set()  # Set the facts as from KB
    query = ''
    mode = ''
    for line in lines:  # Strip by lines from the test case
        line = line.strip()
        if line == "TELL":
            mode = 'TELL'
        elif line == "ASK":
            mode = 'ASK'
        elif mode == 'TELL':  # Split and extract parts from the kb after TELL
            parts = line.split(';')  # Split parts of the test case by a semicolon
            for part in parts:
                part = part.strip()
                operator_table(part, kb, facts)  # Call operator function from sequence.py
        elif mode == 'ASK' and line:  # Split and extract the query from the kb after ASK
            query = line.strip()  # Get the query from ASK mode
    return kb, facts, query

# Constructing table as a set of 0s and 1s to state True or False appending to the symbols set
def generate_truth_table(symbols):
    num_symbols = len(symbols)  # Total number of symbols (or character) available in this test case
    table = []  # Initializes an empty list to store the truth table
    for bits in product([True, False], repeat=num_symbols):  # Set T/F value as bit (0,1) per number of symbol
        table.append(dict(zip(symbols, bits)))  # Creates a dictionary mapping each symbol to a truth value and appends it to the table
    return table  # set this table

# Function handle algorithms for TT method
def truth_table(kb, facts, query):
    symbols = set()  # Set the symbols set (or any character in the test case excluding all operators)
    for condition, _ in kb:  # Iterates over each entry in the kb (knowledge base), unpacks each tuple into 'condition' and '_' (ignored)
        symbols.update(condition)  # update the condtion to the set of symbols
    symbols.update(facts)  # update the facts to the set of symbols
    truth_table = generate_truth_table(symbols)
    for row in truth_table:
        for fact in facts:
            row[fact] = True
        for condition, result in kb:
            if any(row.get(c, False) for c in condition):  # Ensure any of the conditions in disjunction are true
                row[result] = True
    module = condition + (query,)  # Module returned contains the condition set from algorithm plus the query from ask section
    return f"> YES: {len(module)}" if query in truth_table[-1] and truth_table[-1][query] else f"NO {len(module)}"

# Operator used for TT method to set facts as from part
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
            print("Current part:", part)  # Debug keep tracking on the part result once relocate bracket
    # Identify conditional operators (implication, deduction, biconditional)
    # Assertion conditional operators (negation, conjunction, disjunction)
    if '=>' in part:  # Implication Operator
        parts = part.split('=>', 1)  # Split only once at the first occurrence
        if '&' in parts[0]:  # For conjunction operator, strip left component by parts with & symbol in between, parts at index 1 is the right component
            left = tuple([c.strip() for c in parts[0].split('&')])
            right = parts[1].strip()
            kb.append((left, right))
        elif '||' in parts[0]:  # For disjunction operator, split them similarly to conjunction at first
            left = tuple([c.strip() for c in parts[0].split('||')])
            right = parts[1].strip()
            kb.append((left, right))
        elif '~' in parts[0]:  # For negation operator
            fact = parts[0].strip('~').strip  # Strip negation component
            if fact:
                kb.append((fact,), False)  # Append false value to kb
        else:  # Neither conjunction nor disjunction, just strip left and right component by parts with the operator symbol in between
            left = tuple(c.strip() for c in parts[0].split('=>'))
            right = parts[1].strip()
            kb.append((left, right))
    elif '<=' in part:  # Deduction Operator
        parts = part.split('<=', 1)  # Split only once at the first occurrence
        if '&' in parts[1]:  # For conjunction operator, strip right component by parts with & symbol in between, parts at index 1 is the left component
            right = tuple([c.strip() for c in parts[1].split('&')])
            left = parts[0].strip()
            kb.append((right, left))
        elif '||' in parts[1]:  # For disjunction operator, split them similarly to conjunction at first
            right = tuple([c.strip() for c in parts[1].split('||')])
            left = parts[0].strip()
            kb.append((right, left))
        elif '~' in parts[1]:  # For negation operator
            fact = parts[0].strip('~').strip  # Strip negation component
            if fact:
                kb.append((fact,), False)  # Append false value to kb
        else:  # Neither conjunction nor disjunction, just strip right and left component by parts with the operator symbol in between
            right = tuple(c.strip() for c in parts[1].split('<='))
            left = parts[0].strip()
            kb.append((right, left))
    elif '<=>' in part:  # Biconditional Operator
        if '&' in part:  # For conjunction operator
            parts = part.split('<=>', 1)  # Split only once at the first occurrence
            left = tuple([c.strip() for c in parts[0].split('&')])
            right = parts[1].strip()
            kb.append((left, right))
            kb.append((tuple(right.split('&')), left))  # Add the converse implication to make sure it append both way (implicate then deduct)
        elif '||' in part:  # For disjunction operator
            parts = part.split('<=>', 1)  # Split only once at the first occurrence
            left = tuple([c.strip() for c in parts[0].split('||')])
            right = parts[1].strip()
            kb.append((left, right))
            kb.append((tuple(right.split('||')), left))  # Add the converse implication to make sure it append both way (implicate then deduct)
        elif '~' in part:  # For negation operator
            fact = part.strip('~').strip  # Strip negation component
            if fact:
                kb.append((fact,), False)  # Append false value to kb
        else:  # Neither conjunction nor disjunction
            parts = part.split('<=>', 1)  # Split only once at the first occurrence
            left = tuple([c.strip() for c in parts[0].split('<=>')])
            right = parts[1].strip()
            kb.append((left, right))
            kb.append((tuple(right.split('<=>')), left))  # Add the converse implication to make sure it append both way (implicate then deduct)
    else:
        facts.add(part)
        facts.discard('')  # Filter out the empty string as the first module (goal state, which returns as null) should not be appended to the facts count
    return part, facts

# Test case for Scenario 1
test_filename = 'test_scenario_1.txt'
test_case = """
TELL
a || b => c; a
ASK
c
"""

with open(test_filename, 'w') as f:
    f.write(test_case)

kb, facts, query = table_reader(test_filename)
result = truth_table(kb, facts, query)
print(result)
