import sys
import re
from itertools import product
from sequence import operator_table, operator_chain, generic_operator_table, DPLL_propagate_unit_clauses

# TRUTH TABLE PARSER
def table_reader(filename):
    with open(filename, 'r') as file:
        lines = file.read().split('\n')
    kb = []
    facts = set() # Set the facts as from KB
    query = 0
    mode = 0
    horn_index = 0 # horn_index value of 0 indicating the test case doesn't contain bracket
    for line in lines: # Strip by lines from the test case
        line = line.strip()
        if line == "TELL":
            mode = 'TELL'
        elif line == "ASK":
            mode = 'ASK'
        elif mode == 'TELL':  # Split and extract parts from the kb after TELL 
            parts = line.split(';') # Split parts of the test case by a semicolon
            for part in parts:
                part = part.strip()
                if any('(' in part for part in parts): # Case there is a bracket, we have to read operator in generic form
                    horn_index = 1 # horn_index value of 1 indicating the test case contain bracket
                if horn_index == 0:    
                    operator_table(part, kb, facts) # Call regular form operator function from sequence.py
                else:
                    generic_operator_table(part, kb, facts) # Call generic operator function from sequence.py
        elif mode == 'ASK' and line: # Split and extract the query from the kb after ASK 
            query = line.strip() # Get the query from ASK mode
    return kb, facts, query, horn_index

# Constructing table as a set of 0s and 1s to state True or False appending to the symbols set
def generate_truth_table(symbols):
    num_symbols = len(symbols) # Total number of symbols (or character) available in this test case 
    table = [] # Initializes an empty list to store the truth table
    for bits in product([True, False], repeat=num_symbols): # Set T/F value as bit (0,1) per number of symbol
        table.append(dict(zip(symbols, bits))) # Creates a dictionary mapping each symbol to a truth value and appends it to the table
    return table # set this table

# Function handle algorithms for TT method (not handling bracket rules)
def truth_table(kb, facts, query):
    symbols = set() # Set the symbols set (or any character in the test case excluding all operators)
    for condition, _ in kb:  # Iterates over each entry in the kb (knowledge base), unpacks each tuple into 'condition' and '_' (ignored)
        symbols.update(condition) # update the condtion to the set of symbols
    symbols.update(facts) # update the facts to the set of symbols
    truth_table = generate_truth_table(symbols)
    for row in truth_table: # iterate over each row in the truth table
        for fact in facts:
            row[fact] = True
        for condition, result in kb:
            # Handle disjunction kb
            if any('*' in c for c in condition): # Look up for the disjunction component that has been remarked with '*' symbol individually
                condition = tuple(c.replace('*', '') for c in condition) # Remove that '*' symbol by replace it with an empty string
                if any(row.get(c, False) for c in condition):  # Ensure any (one or all) disjunction conditions are true
                    row[result] = True
                condition = tuple(c for c in condition if c.strip()) # Strip (remove) any empty string '' from condition
            # Handle non-disjunction kb
            else:
                if all(row[c] for c in condition): # Ensure all conjunction condition are true
                    row[result] = True
    module = condition + (query,) # Module returned contains the condition set from algorithm plus the query from ask section
    return f"> YES: {len(module)}" if query in truth_table[-1] and truth_table[-1][query] else f"NO" 

def evaluate_condition(row, condition):
    if isinstance(condition, tuple): # check if the condition is a tuple
        return all(row.get(c, False) for c in condition) # evaluate each condition in the row and return True if all are True
    return row.get(condition, False) # return the value of the condition in the row, defaulting to False if not found

# Function handle algorithms for TT method in generic form (can handle bracket rules)
def generic_truth_table(kb, facts, query):
    symbols = set()  # Initialize an empty set for symbols
    for condition, _, _ in kb: # Iterate over each entry in the knowledge base
        symbols.update(condition) # Add the condition symbols to the symbols set
    symbols.update(facts)
    truth_table = generate_truth_table(symbols) # Generate the truth table
    # Organize the knowledge base by bracket levels
    bracket_kb = {} # Initialize an empty dictionary to organize the knowledge base by bracket levels
    for entry in kb:  # Iterate over each entry in the knowledge base
        if entry[2] not in bracket_kb: # If the bracket level is not already in the dictionary
            bracket_kb[entry[2]] = [] # If the bracket level is not already in the dictionary
        bracket_kb[entry[2]].append(entry)  # Initialize a list for that bracket level
    for row in truth_table:
        for fact in facts:
            row[fact] = True
        # Evaluate bracketed knowledge base by levels
        for level in sorted(bracket_kb.keys()): # Iterate over each bracket level in ascending order
            bracket_results = {} # Initialize an empty dictionary for bracket results
            for condition, result, _ in bracket_kb[level]:  # Iterate over each entry in the knowledge base at the current bracket level
                if condition == ('@',): # Condition variable contains @ symbol indicating this is a high level of bracket rule that suppose to be evaluate with appropriate bracket ordering sequence
                    inner_conditions = [] # Initialize an empty list for inner conditions
                    for prev_level in range(level - 1, -1, -1): # Iterate over previous bracket levels in descending order
                        for cond, res, _ in bracket_kb.get(prev_level, []):  # Iterate over entries in previous bracket levels
                            if cond == ('@',):
                                inner_conditions.append(kb[0][0])  # Add the condition from the high level of bracket rule
                            else:
                                inner_conditions.append(cond) # Add the condition to the inner conditions list
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
                else: # Condition variable does not contain any bracket, so they can be treated at the base level
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
                    inner_condition = () # Return inner_condition empty casing this variable is not applied
            for result in bracket_results:
                row[result] = True
    module = len(condition) + len(bracket_kb) + len(query) + len(inner_condition) # Total evaluation expanded
    # Uncomment this part to see how bracket rules are evaluated
    #for level in sorted(bracket_kb.keys()):
    #    print(f"Bracket_kb_{level}: ", bracket_kb[level])
    return f"> YES {module}" if evaluate_condition(truth_table[-1], query) else "NO"

# FORWARD and BACKWARD CHAIN PARSER
def chain_reader(filename, method):
    with open(filename, 'r') as file:
        lines = file.read().split('\n')
    kb = {}
    facts = set() # Set the facts as from KB
    query = 0
    mode = 0
    for line in lines:  # Strip by lines from the test case
        line = line.strip()
        if line == "TELL":
            mode = 'TELL'
        elif line == "ASK":
            mode = 'ASK'
        elif mode == 'TELL': # Split and extract parts from the kb after TELL 
            parts = line.split(';') # Split parts of the test case by a semicolon
            for part in parts:
                part = part.strip()
                operator_chain(part, method, kb, facts) # Call operator function from sequence.py
        elif mode == 'ASK' and line: # Split and extract the query from the kb after ASK 
            query = line.strip() # Get the query from ASK mode
    return kb, facts, query

# Function handle algorithms for FC method
def forward_chain(kb, facts, query):
    changed = True
    while changed:
        changed = False
        for condition, result in kb.items(): # Check for condition per result (T/F) in the kb's item set
            if all(c in facts for c in condition):
                if result not in facts:
                    facts.add(result)
                    changed = True
    # Filter out the empty string as the first module (goal state, which returns as null) should not be appended to the facts count
    facts.discard('')
    derived_facts_list = sorted(facts, key=lambda x: (len(x), x)) # sorted by the key and neglect redundant components
    # Print test output with either YES (with module expansion) or NO
    return f"> YES: " + ', '.join(derived_facts_list) if query in facts else "NO"

# Function handle algorithms for BC method
def backward_chain(kb, facts, query, derived_facts):
    if query in facts: # if query in the facts set, set that one to the derived fact for usage
        derived_facts.add(query)
        return True
    if query not in kb: # Case the query in ASK component is out of the kb test case
        return False
    for conditions in kb[query]: # Check for condition in the kb's ASK query part
        if all(backward_chain(kb, facts, cond, derived_facts) for cond in conditions):
            derived_facts.add(query)
            derived_facts_list = sorted(derived_facts, key=lambda x: (len(x), x)) # sorted by the key and neglect redundant components
            return "> YES: " + ', '.join(derived_facts_list) # Print result
        else:
            return "NO"
    return False

# DPLL PARSER
def DPLL_reader(filename):
    with open(filename, 'r') as file:
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

# Evaluate the clauss with conditional checker to set T/F value
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

# MAIN ALGORITHMS OPERATOR
if __name__ == "__main__":
    filename = sys.argv[1]
    method = sys.argv[2]

    if method == "TT": # If it is Truth Table method
        kb, facts, query, horn_index = table_reader(filename)
        if horn_index == 0: # Call regular truth table algorithm casing no bracket rule
            result = truth_table(kb, facts, query)
        elif horn_index == 1: # Call generic truth table algorithm casing bracket rule
            result = generic_truth_table(kb, facts, query)
        print(result)

    elif method == "FC": # If it is Forward Chain method
        kb, facts, query = chain_reader(filename, method)
        result = forward_chain(kb, facts, query)
        print(result)

    elif method == "BC": # If it is Backward Chain method
        kb, facts, query = chain_reader(filename, method)
        derived_facts = set()
        result = backward_chain(kb, facts, query, derived_facts)
        print(result)

    elif method == "DPLL": # If it is Davis-Putnam-Logemann-Loveland method
        kb, facts, query = DPLL_reader(filename)
        # Negate the query and add to the knowledge base to check for entailment
        negated_query = '¬' + query if not query.startswith('¬') else query[1:]
        kb.add(negated_query)
        if DPLL(kb, facts):
            print("NO")  # Query is not entailed
        else:
            print("> YES")  # Query is entailed

    else:
        # Invalid search method command
        print("Invalid search method. Please choose among: TT, FC, BC, DPLL")
        sys.exit(1)

