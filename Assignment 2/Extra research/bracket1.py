import sys
import re
from itertools import product

# TRUTH TABLE PARSER
def table_reader(filename):
    with open(filename, 'r') as file:
        lines = file.read().split('\n')
    kb = []
    facts = set()
    query = ""
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
                operator_table(part, kb, facts)
        elif mode == 'ASK' and line:
            query = line.strip()
    return kb, facts, query

def generate_truth_table(symbols):
    num_symbols = len(symbols)
    table = []
    for bits in product([True, False], repeat=num_symbols):
        table.append(dict(zip(symbols, bits)))
    return table

def evaluate_condition(row, condition):
    if isinstance(condition, tuple):
        return all(row.get(c, False) for c in condition)
    return row.get(condition, False)

def truth_table(kb, facts, query):
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
                        if evaluate_condition(row, inner_condition):
                            bracket_results[result] = True
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

universal_variables = {
    '^': '&', '∧': '&',
    '|': '||',
    '¬': '~', '!': '~',
    '->': '=>', '→': '=>',
    '<-': '<=', '←': '<=',
    '<->': '<=>', '↔': '<=>'
}

def operator_table(part, kb, facts, current_level=0):
    for variable, symbol in universal_variables.items():
        part = part.replace(variable, symbol)

    if '(' in part:
        current_level += 1

    if '(' in part:
        while '(' in part:
            inner_parts = re.findall(r'\(([^()]+)\)', part)
            for inner_part in inner_parts:
                operator_table(inner_part, kb, facts, current_level)
            part = re.sub(r'\(([^()]+)\)', '@', part)

    if '=>' in part:
        parts = part.split('=>', 1)
        left = tuple(c.strip() for c in parts[0].split('&'))
        right = parts[1].strip()
        kb.append((left, right, current_level))
    elif '<=' in part:
        parts = part.split('<=', 1)
        left = parts[0].strip()
        right = tuple(c.strip() for c in parts[1].split('&'))
        kb.append((right, left, current_level))
    elif '<->' in part:
        parts = part.split('<->', 1)
        left = tuple(c.strip() for c in parts[0].split('&'))
        right = parts[1].strip()
        kb.append((left, right, current_level))
        kb.append((tuple(right.split('&')), left, current_level))
    else:
        facts.add(part)
        facts.discard('')

    return part, facts

if __name__ == "__main__":
    filename = sys.argv[1]
    method = sys.argv[2]

    if method == "TT":
        kb, facts, query = table_reader(filename)
        result = truth_table(kb, facts, query)
        print(result)
        
    else:
        print("Invalid search method. Please choose among: TT, FC, BC")
        sys.exit(1)
