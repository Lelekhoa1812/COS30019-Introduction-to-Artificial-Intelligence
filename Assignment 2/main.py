import sys
import re
from itertools import product

# Define a dictionary for universal variables.
# Convert the definition to standard operators.
# This way, if a test file uses symbol with the same meaning, they will be treated the same.
universal_variables = {
    '^': '&', # Conjuction (and) - add extra symbol (∧)
    'v': '||', # Disjunction (or) - add extra symbol (/)
    '¬': '~', # Negation (not) - add extra symbol (∧)
    '->': '=>', # Implication - add extra symbol (→)
    '<-': '<=', # Deduction - add extra symbol (←)
    '<->': '<=>' # Biconditional - add extra symbol (↔)
}

# TRUTH TABLE PARSER
def table_reader(filename):
    with open(filename, 'r') as file:
        lines = file.read().split('\n')
    kb = []
    facts = set()
    query = 0
    mode = 0
    for line in lines:
        line = line.strip()
        if line == "TELL":
            mode = 'TELL'
        elif line == "ASK":
            mode = 'ASK'
        elif mode == 'TELL':
            parts = line.split(';')
            for part in parts:
                part = part.strip()
                for variable, symbol in universal_variables.items(): # Check and read universal symbol, if used in the test file
                    part = part.replace(variable, symbol)
                # Identify conditional operators (implication, deduction, biconditional)
                # Assertion conditional operators (negation, conjunction, disjunction)
                if '=>' in part: # Implication Operator
                    left, right = part.split('=>')
                    left = tuple([c.strip() for c in left.split('&')])
                    kb.append((left, right.strip())) 
                elif '<=' in part: # Deduction Operator
                    right, left = part.split('<=')
                    right = tuple([c.strip() for c in right.split('&')])
                    kb.append((right, left.strip()))   
                elif '<=>' in part: # Biconditional Operator
                    left, right = part.split('<=>')
                    left = tuple([c.strip() for c in left.split('&')])
                    kb.append((left, right.strip()))
                    kb.append((tuple(right.split('&')), left))  # Add the converse implication to make sure it append both way (implicate then deduct)
                else:
                    # Handle brackets
                    brackets = re.findall(r'\((.*?)\)', part)
                    for bracket in brackets:
                        part = part.replace(f'({bracket})', f' {bracket} ')
                    facts.add(part.strip())
        elif mode == 'ASK' and line:
            query = line.strip()
    return kb, facts, query

def generate_truth_table(symbols):
    num_symbols = len(symbols)
    table = []
    for bits in product([True, False], repeat=num_symbols):
        table.append(dict(zip(symbols, bits)))
    return table

def evaluate_expression(expression, row):
    # Evaluate the expression based on the values in the row
    for fact, value in row.items():
        expression = expression.replace(fact, str(value))
    return eval(expression)

def truth_table(kb, facts, query):
    symbols = set()
    for condition, _ in kb:
        symbols.update(condition)
    symbols.update(facts)
    truth_table = generate_truth_table(symbols)
    for row in truth_table:
        for fact, value in row.items():
            if fact in facts:
                row[fact] = True
        for condition, result in kb:
            if all(row[c] for c in condition):
                row[result] = True
    for row in truth_table:
        for fact in facts:
            row[fact] = True  # Set fact values to True
        for condition, result in kb:
            if '(' in result:  # Evaluate expressions within brackets first
                expression = result
                brackets = re.findall(r'\((.*?)\)', result)
                for bracket in brackets:
                    expression = expression.replace(f'({bracket})', str(evaluate_expression(bracket, row)))
                row[result] = evaluate_expression(expression, row)
            else:
                row[result] = all(row[c] for c in condition)
    facts.discard('') # Filter out the empty string as the first module (goal state, which returns as null) should not be appended to the facts count.
    print(facts)
    return f"> YES: {len(facts)}" if query in truth_table[-1] and truth_table[-1][query] else f"NO"#{len(facts)}"    

# FORWARD and BACKWARD CHAIN PARSER
def chain_reader(filename, method):
    with open(filename, 'r') as file:
        lines = file.read().split('\n')
    kb = {}
    facts = set()
    query = 0
    mode = 0  
    for line in lines:
        line = line.strip()
        if line == "TELL":
            mode = 'TELL'
        elif line == "ASK":
            mode = 'ASK'
        elif mode == 'TELL':
            parts = line.split(';')
            for part in parts:
                part = part.strip()
                for variable, symbol in universal_variables.items(): # Check and read universial symbol, if used in the test file
                    part = part.replace(variable, symbol)
                # Identify conditional operators (implication, deduction, biconditional)
                # Assertion conditional operators (negation, conjunction, disjunction)
                if '=>' in part: # Implication Operator
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
                elif '<=' in part: # Deduction Operator
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
                elif '<=>' in part: # Biconditional Operator
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
                        kb[condition_left] = right.strip() # Implication fist 
                        kb[condition_right] = left.strip() # Then deduction for biconditional
                    elif method == "BC":
                        kb.setdefault(right.strip(), []).append(condition_left) # Implication fist 
                        kb.setdefault(left.strip(), []).append(condition_right) # Then deduction for biconditional
                else:
                    # Imagine FC method uses a similar approach to BFS 
                    # It may have to expand all nodes to deeper level
                    if method == "FC": 
                        facts.add(part)
                    # BC however WILL NOT apply this, treat they as DFS, which way in this case, the module expanded is correspond to 1 given route
                    # Other modules are redundant
        elif mode == 'ASK' and line:
            query = line.strip()
    return kb, facts, query

def forward_chain(kb, facts, query):
    changed = True
    while changed:
        changed = False
        for condition, result in kb.items():
            if all(c in facts for c in condition):
                if result not in facts:
                    facts.add(result)
                    changed = True
    facts.discard('') # Filter out the empty string as the first module (goal state, which returns as null) should not be appended to the facts count.
    return f"> YES: {facts}" if query in facts else "NO" # Print test output with either YES (with module expansion) or NO


def backward_chain(kb, facts, query):
    if query in facts:
        return True
    if query not in kb:
        return False
    for conditions in kb[query]:
        inferred_facts = set()
        for cond in conditions:
            if cond not in facts:
                inferred_facts.add(cond)
        inferred_facts.add(query)
        facts.update(inferred_facts)
        facts.discard('') # Filter out the empty string as the first module (goal state, which returns as null) should not be appended to the facts count.
        return f"> YES: {facts}" if all(backward_chain(kb, facts, cond) for cond in conditions) else "NO" # Print test output with either YES (with module expansion) or NO
    return False

# OPERATOR
if __name__ == "__main__":
    filename = sys.argv[1]
    method = sys.argv[2]

    if method == "TT":
        kb, facts, query = table_reader(filename)
        result = truth_table(kb, facts, query)
        print(result)

    elif method == "FC":
        kb, facts, query = chain_reader(filename, method)
        result = forward_chain(kb, facts, query)
        print(result)

    elif method == "BC":
        kb, facts, query = chain_reader(filename, method)
        result = backward_chain(kb, facts, query)
        print(result)

    else: 
        print("Invalid search method. Please choose among: TT, FC, BC") # Invalid search method command
        sys.exit(1)
