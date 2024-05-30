import sys

def DPLL_reader(file_path):
    with open(file_path, 'r') as file:
        lines = file.read().split('\n')
    kb = set()  # Knowledge base (set of clauses)
    facts = set()  # Known facts
    query = None  # Query to evaluate
    mode = None  # Mode to track TELL or ASK section
    for line in lines:
        if line == "TELL":
            mode = 'tell'
        elif line == "ASK":
            mode = 'ask'
        elif mode == 'tell' and line.strip():
            parts = line.split('∧') # DPLL test case will be splitted by each ∧ symbol
            for part in parts:
                part = part.strip()
                if part:
                    kb.add(part)  # Add clause to the knowledge base
        elif mode == 'ask' and line.strip():
            query = line.strip()  # Set the query
    return kb, facts, query

def evaluate_clause(clause, facts):
    # Evaluate if the clause is true given the current facts
    literals = clause.replace('¬', 'not ').replace('∨', ' or ').replace('p', 'p')
    literals = literals.split(' or ')
    for literal in literals:
        if literal.startswith('not '):
            if literal[4:] not in facts:
                return True  # Clause is true if negated literal is not in facts
        else:
            if literal in facts:
                return True  # Clause is true if literal is in facts
    return False  # Clause is false if none of the literals make it true

def DPLL_propagate_unit_clauses(kb, facts):
    # Propagate unit clauses (clauses with a single literal)
    changed = True
    while changed:
        changed = False
        unit_clauses = [clause for clause in kb if len(clause.split('∨')) == 1]
        
        for clause in unit_clauses:
            literal = clause.strip()
            if literal.startswith('¬'):
                literal = literal[1:]
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

# Function handle algorithms for DPLL method
def DPLL(kb, facts):
    # Apply the DPLL algorithm
    kb, facts = DPLL_propagate_unit_clauses(kb, facts)
    if all(evaluate_clause(clause, facts) for clause in kb):
        return True  # All clauses are true
    if any(evaluate_clause(clause, facts) is False for clause in kb):
        return False  # Some clause is false
    # Find unassigned literals
    unassigned_literals = {literal.strip() for clause in kb for literal in clause.split('∨')}
    unassigned_literals -= {lit for lit in unassigned_literals if lit.startswith('¬')}
    unassigned_literals -= {lit for lit in facts if not lit.startswith('¬')}
    if not unassigned_literals:
        return True  # No unassigned literals, all clauses are satisfied
    chosen_literal = unassigned_literals.pop()  # Choose a literal to assign
    new_kb = kb.copy()
    new_facts = facts.copy()
    new_facts.add(chosen_literal)  # Assign literal to true
    if DPLL(new_kb, new_facts):
        return True  # If true, return True
    new_kb = kb.copy()
    new_facts = facts.copy()
    new_facts.add('¬' + chosen_literal)  # Assign literal to false
    return DPLL(new_kb, new_facts)  # Recursively check with the new assignment

def main():
    if len(sys.argv) < 2:
        print("Usage: custom1.py <filename>")
        return
    
    file_path = sys.argv[1]
    kb, facts, query = DPLL_reader(file_path)
    
    # Negate the query and add to the knowledge base to check for entailment
    negated_query = '¬' + query if not query.startswith('¬') else query[1:]
    kb.add(negated_query)
    
    if DPLL(kb, facts):
        print("NO")  # Query is not entailed
    else:
        print("YES")  # Query is entailed

if __name__ == "__main__":
    main()
