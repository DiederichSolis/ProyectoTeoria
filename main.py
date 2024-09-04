import graphviz
from collections import defaultdict, deque
import sys

# 1. Conversión de Infix a Postfix
def infix_to_postfix(infix_expr):
    precedence = {'*': 3, '.': 2, '|': 1}
    output = []
    stack = []

    def is_operator(c):
        return c in precedence

    def precedence_order(c):
        return precedence[c]

    for char in infix_expr:
        if char.isalnum() or char == 'ε':
            output.append(char)
        elif char == '(':
            stack.append(char)
        elif char == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            stack.pop()  # Pop '('
        else:  # Operator
            while stack and stack[-1] != '(' and precedence_order(stack[-1]) >= precedence_order(char):
                output.append(stack.pop())
            stack.append(char)

    while stack:
        output.append(stack.pop())

    return ''.join(output)

# 2. Construcción de un AFN a partir de la expresión Postfix
class State:
    def __init__(self, name=None):
        self.name = name
        self.edges = []

    def __str__(self):
        return self.name or f"State_{id(self)}"

    def __repr__(self):
        return self.__str__()

class NFA:
    def __init__(self, start, end):
        self.start = start
        self.end = end

def build_nfa(postfix_expr):
    stack = []

    for char in postfix_expr:
        if char.isalnum() or char == 'ε':
            start = State(name=f"Start_{char}")
            end = State(name=f"End_{char}")
            start.edges.append((char, end))
            stack.append(NFA(start, end))
        elif char == '.':
            nfa2 = stack.pop()
            nfa1 = stack.pop()
            nfa1.end.edges.append(('ε', nfa2.start))
            stack.append(NFA(nfa1.start, nfa2.end))
        elif char == '|':
            nfa2 = stack.pop()
            nfa1 = stack.pop()
            start = State(name="Start_Choice")
            end = State(name="End_Choice")
            start.edges.append(('ε', nfa1.start))
            start.edges.append(('ε', nfa2.start))
            nfa1.end.edges.append(('ε', end))
            nfa2.end.edges.append(('ε', end))
            stack.append(NFA(start, end))
        elif char == '*':
            nfa = stack.pop()
            start = State(name="Start_Star")
            end = State(name="End_Star")
            start.edges.append(('ε', nfa.start))
            start.edges.append(('ε', end))
            nfa.end.edges.append(('ε', end))
            nfa.end.edges.append(('ε', nfa.start))
            stack.append(NFA(start, end))

    return stack.pop()

# 3. Conversión de AFN a AFD
class DFA:
    def __init__(self, start_state, accept_states, transition_table):
        self.start_state = start_state
        self.accept_states = accept_states
        self.transition_table = transition_table

def convert_nfa_to_dfa(nfa):
    initial_state = frozenset(epsilon_closure([nfa.start]))
    states = {initial_state}
    unmarked_states = [initial_state]
    dfa_transitions = {}
    dfa_accept_states = set()

    while unmarked_states:
        current = unmarked_states.pop()
        for symbol in get_alphabet(nfa):
            next_state = frozenset(epsilon_closure(move(current, symbol)))
            if not next_state:
                continue
            if next_state not in states:
                states.add(next_state)
                unmarked_states.append(next_state)
            dfa_transitions[(current, symbol)] = next_state

        if nfa.end in current:
            dfa_accept_states.add(current)

    return DFA(initial_state, dfa_accept_states, dfa_transitions)

def epsilon_closure(states):
    stack = list(states)
    closure = set(states)

    while stack:
        state = stack.pop()
        for symbol, next_state in state.edges:
            if symbol == 'ε' and next_state not in closure:
                closure.add(next_state)
                stack.append(next_state)

    return closure

def move(states, symbol):
    result = set()
    for state in states:
        for sym, next_state in state.edges:
            if sym == symbol:
                result.add(next_state)
    return result

def get_alphabet(nfa):
    alphabet = set()
    states_to_check = [nfa.start]
    checked_states = set()

    while states_to_check:
        state = states_to_check.pop()
        if state in checked_states:
            continue
        checked_states.add(state)
        for symbol, next_state in state.edges:
            if symbol != 'ε':
                alphabet.add(symbol)
            states_to_check.append(next_state)

    return alphabet

# 4. Minimización del AFD
def minimize_dfa(dfa):
    states = set()
    for (state, symbol) in dfa.transition_table.keys():
        states.add(state)
        states.add(dfa.transition_table.get((state, symbol), None))
    states.discard(None)

    non_accept_states = states - dfa.accept_states
    partitions = [set(dfa.accept_states), non_accept_states]
    new_partitions = []

    while partitions != new_partitions:
        if new_partitions:
            partitions = new_partitions[:]
            new_partitions = []

        for group in partitions:
            subgroups = {}
            for state in group:
                transition_signature = tuple(
                    dfa.transition_table.get((state, symbol), None) for symbol in get_alphabet_from_dfa(dfa)
                )
                if transition_signature not in subgroups:
                    subgroups[transition_signature] = set()
                subgroups[transition_signature].add(state)
            
            new_partitions.extend(subgroups.values())

    new_states = {}
    for i, group in enumerate(new_partitions):
        new_states[frozenset(group)] = i

    minimized_transitions = {}
    for (state, symbol) in dfa.transition_table.keys():
        dest = dfa.transition_table.get((state, symbol), None)
        if dest is not None:
            source_group = None
            dest_group = None
            
            for group in new_states.keys():
                if state in group:
                    source_group = group
                if dest in group:
                    dest_group = group
            
            if source_group is not None and dest_group is not None:
                minimized_transitions[(new_states[source_group], symbol)] = new_states[dest_group]
            else:
                print(f"Error: No se encontró source_group o dest_group en new_states.")
                print(f"source_group: {source_group}")
                print(f"dest_group: {dest_group}")
                print(f"new_states keys: {list(new_states.keys())}")
                raise KeyError(f"Falta {dest_group} en new_states")

    minimized_start_state = None
    for group in new_partitions:
        if dfa.start_state in group:
            minimized_start_state = new_states[frozenset(group)]
            break

    if minimized_start_state is None:
        print(f"Error: El estado inicial del DFA no se encuentra en new_states.")
        print(f"dfa.start_state: {dfa.start_state}")
        print(f"new_states keys: {list(new_states.keys())}")
        raise KeyError(f"El estado inicial no se encuentra en new_states.")

    minimized_accept_states = {new_states[frozenset(group)] for group in new_partitions if group & set(dfa.accept_states)}

    return DFA(
        minimized_start_state,
        minimized_accept_states,
        minimized_transitions
    )

def get_alphabet_from_dfa(dfa):
    return set(symbol for (_, symbol) in dfa.transition_table.keys())

# 5. Simulación del AFD
def simulate_dfa(dfa, input_string):
    current_state = dfa.start_state
    for symbol in input_string:
        if (current_state, symbol) not in dfa.transition_table:
            return False
        current_state = dfa.transition_table[(current_state, symbol)]

    return current_state in dfa.accept_states

def simulate_nfa(nfa, input_string):
    current_states = frozenset(epsilon_closure([nfa.start]))
    for symbol in input_string:
        next_states = set()
        for state in current_states:
            next_states.update(epsilon_closure(move([state], symbol)))
        current_states = frozenset(next_states)

    return nfa.end in current_states

# 6. Generación de gráficos para NFA y DFA
def draw_nfa(nfa, filename='nfa'):
    dot = graphviz.Digraph(comment='NFA')
    dot.attr(rankdir='LR')

    def add_edges(state, visited):
        if state in visited:
            return
        visited.add(state)
        dot.node(str(state))
        for symbol, next_state in state.edges:
            dot.edge(str(state), str(next_state), label=symbol)
            add_edges(next_state, visited)

    add_edges(nfa.start, set())
    dot.render(filename, format='png', cleanup=True)

def draw_dfa(dfa, filename='dfa'):
    dot = graphviz.Digraph(comment='DFA')
    dot.attr(rankdir='LR')

    for state in dfa.transition_table.keys():
        if state in dfa.accept_states:
            dot.node(str(state), shape='doublecircle')
        else:
            dot.node(str(state))

    for (state, symbol), next_state in dfa.transition_table.items():
        dot.edge(str(state), str(next_state), label=symbol)

    dot.render(filename, format='png', cleanup=True)

def draw_minimized_dfa(dfa, filename='minimized_dfa'):
    dot = graphviz.Digraph(comment='Minimized DFA')
    dot.attr(rankdir='LR')

    for state in dfa.transition_table.keys():
        if state in dfa.accept_states:
            dot.node(str(state), shape='doublecircle')
        else:
            dot.node(str(state))

    for (state, symbol), next_state in dfa.transition_table.items():
        dot.edge(str(state), str(next_state), label=symbol)

    dot.render(filename, format='png', cleanup=True)

def main():
    if len(sys.argv) != 2:
        print("Usage: python regex_to_dfa.py '<regex>'")
        sys.exit(1)

    regex = sys.argv[1]

    postfix_expr = infix_to_postfix(regex)
    nfa = build_nfa(postfix_expr)
    dfa = convert_nfa_to_dfa(nfa)
    minimized_dfa = minimize_dfa(dfa)

    draw_nfa(nfa)
    draw_dfa(dfa)
    draw_minimized_dfa(minimized_dfa)

    print("NFA:")
    print("Start state:", nfa.start)
    print("End state:", nfa.end)

    print("\nDFA:")
    print("Start state:", dfa.start_state)
    print("Accept states:", dfa.accept_states)

    print("\nMinimized DFA:")
    print("Start state:", minimized_dfa.start_state)
    print("Accept states:", minimized_dfa.accept_states)

if __name__ == '__main__':
    main()
