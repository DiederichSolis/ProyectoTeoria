import graphviz
from collections import defaultdict, deque

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
