import sys
import re
from itertools import product
from sequence import operator_table, operator_chain

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
                operator_table(part, kb, facts) # Call operator function from sequence.py
        elif mode == 'ASK' and line:
            query = line.strip()
    return kb, facts, query


def generate_truth_table(symbols):
    num_symbols = len(symbols)
    table = []
    for bits in product([True, False], repeat=num_symbols):
        table.append(dict(zip(symbols, bits)))
    return table


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
    print(facts)
    return f"> YES: {len(facts)}" if query in truth_table[-1] and truth_table[-1][query] else f"NO" #{len(facts)}"   

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
                operator_chain(part, method, kb, facts) # Call operator function from sequence.py
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
    # Filter out the empty string as the first module (goal state, which returns as null) should not be appended to the facts count.
    facts.discard('')
    # Print test output with either YES (with module expansion) or NO
    return f"> YES: {facts}" if query in facts else "NO"


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
        # Filter out the empty string as the first module (goal state, which returns as null) should not be appended to the facts count.
        facts.discard('')
        # Print test output with either YES (with module expansion) or NO
        return f"> YES: {facts}" if all(backward_chain(kb, facts, cond) for cond in conditions) else "NO"
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
        # Invalid search method command
        print("Invalid search method. Please choose among: TT, FC, BC")
        sys.exit(1)

