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
