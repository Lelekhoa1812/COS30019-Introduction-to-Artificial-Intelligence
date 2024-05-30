import sys

def parse_input(file_path):
    with open(file_path, 'r') as file:
        lines = file.read().split('\n')
    kb = {}
    facts = set()
    query = 0
    mode = 0
    for line in lines:
        if line == "TELL":
            mode = 'tell'
        elif line == "ASK":
            mode = 'ask'
        elif mode == 'tell':
            parts = line.split(';')
            for part in parts:
                part = part.strip()
                if '=>' in part:
                    left, right = part.split('=>')
                    left_parts = left.split('&')
                    left_parts2 = []
                    for c in left_parts:
                        left_parts2.append(c.strip())
                    condition = tuple(left_parts2)
                    kb.setdefault(right.strip(), []).append(condition)
                else:
                    facts.add(part)
        elif mode == 'ask' and line:
            query = line.strip()
    return kb, facts, query

def backwardchain(kb, facts, query, derived_facts):
    if query in facts:
        derived_facts.add(query)
        return True
    if query not in kb:
        return False
    
    for conditions in kb[query]:
        if all(backwardchain(kb, facts, cond, derived_facts) for cond in conditions):
            derived_facts.add(query)
            return True
    return False

def main():
    file_path = sys.argv[1]
    kb, facts, query = parse_input(file_path)
    derived_facts = set()
    if backwardchain(kb, facts, query, derived_facts):
        derived_facts_list = sorted(derived_facts, key=lambda x: (len(x), x))
        result = "YES: " + ', '.join(derived_facts_list)
    else:
        result = "NO"
    print(result)

if __name__ == "__main__":
    main()