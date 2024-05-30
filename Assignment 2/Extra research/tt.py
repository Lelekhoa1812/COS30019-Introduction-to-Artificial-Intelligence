import sys
from itertools import product

def parse_input(file_path):
    with open(file_path, 'r') as file:
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
                if '=>' in part:
                    left, right = part.split('=>')
                    left = tuple([c.strip() for c in left.split('&')])
                    kb.append((left, right.strip()))
                else:
                    facts.add(part)
        elif mode == 'ASK' and line:
            query = line.strip()
    return kb, facts, query

def update_truth_table(truth_table, kb):
    # Apply rules until no new facts are learned
    learned = True
    while learned:
        learned = False
        for premises, conclusion in kb:
            # Check if all premises are true
            if all(truth_table.get(p, False) for p in premises):
                if truth_table.get(conclusion, False) == False:
                    truth_table[conclusion] = True
                    learned = True
    return truth_table

def main():
    file_path = sys.argv[1]
    kb, facts, query = parse_input(file_path)
    
    truth_table = {fact: True for fact in facts}
    
    truth_table = update_truth_table(truth_table, kb)
    
    print("Result:", truth_table.get(query, False))

if __name__ == "__main__":
    main()
