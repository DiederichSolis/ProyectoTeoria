import graphviz

class Metachar:
    def __init__(self, value):
        self.value = "\\?"
        

class Node:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right
        self.id = id(self)  # Unique ID for Graphviz

class State:
    def __init__(self, is_accept=False, is_deterministic=False):
        self.is_accept = is_accept
        self.is_deterministic = is_deterministic  # AFD or AFN
        self.transitions = {}  # Diccionario que mapea input a estado(s)
        self.epsilon_transitions = []

class NFA:
    def __init__(self, start_state, accept_state):
        self.start_state = start_state
        self.accept_state = accept_state

def postfix_to_ast(postfix):
    stack = []

    for char in postfix:
        if char.isalnum() or char == 'ε':
            stack.append(Node(char))
        else:
            if char == '*':
                operand = stack.pop()
                stack.append(Node(char, left=operand))
            else:
                right = stack.pop()
                left = stack.pop()
                stack.append(Node(char, left, right))
    
    return stack.pop()

def draw_ast(root):
    def add_nodes_edges(graph, node):
        graph.node(str(node.id), node.value)
        if node.left:
            graph.edge(str(node.id), str(node.left.id))
            add_nodes_edges(graph, node.left)
        if node.right:
            graph.edge(str(node.id), str(node.right.id))
            add_nodes_edges(graph, node.right)

    dot = graphviz.Digraph()
    add_nodes_edges(dot, root)
    return dot

def extend_regex(regex):
    return regex.replace('+', '*').replace('?', '|ε')

def get_precedence(c):
    precedence = {
        '(': 1,
        '|': 2,
        '.': 3,
        '?': 4,
        '*': 4,
        '+': 4,
        '^': 5
    }
    return precedence.get(c, 6)

def format_regex(regex):
    all_operators = ['|', '?', '+', '*', '^']
    binary_operators = ['^', '|']
    res = ""
    
    i = 0
    while i < len(regex):
        c1 = regex[i]
        if i + 1 < len(regex):
            c2 = regex[i + 1]
            res += c1
            if (c1 != '(' and c2 != ')' and c2 not in all_operators and c1 not in binary_operators):
                res += '.'
        i += 1
    res += regex[-1]
    
    return res

def infix_to_postfix(regex):
    postfix = ""
    stack = []
    formatted_regex = format_regex(regex)
    steps = []

    for c in formatted_regex:
        if c.isalnum() or c == 'ε':
            postfix += c
            steps.append(f"Added '{c}' to postfix expression")
        elif c == '(':
            stack.append(c)
            steps.append(f"Pushed '{c}' to stack")
        elif c == ')':
            while stack and stack[-1] != '(':
                top = stack.pop()
                postfix += top
                steps.append(f"Popped '{top}' from stack to postfix expression")
            stack.pop()  # Remove '(' from stack
            steps.append(f"Popped '(' from stack")
        else:
            while stack and get_precedence(stack[-1]) >= get_precedence(c):
                top = stack.pop()
                postfix += top
                steps.append(f"Popped '{top}' from stack to postfix expression")
            stack.append(c)
            steps.append(f"Pushed '{c}' to stack")

    while stack:
        top = stack.pop()
        postfix += top
        steps.append(f"Popped '{top}' from stack to postfix expression")
    
    return postfix, steps

def thompson_construct(node):
    if node.value == '*':
        start = State()
        accept = State(is_accept=True)
        nfa = thompson_construct(node.left)

        start.epsilon_transitions.append(nfa.start_state)
        start.epsilon_transitions.append(accept)
        nfa.accept_state.epsilon_transitions.append(nfa.start_state)
        nfa.accept_state.epsilon_transitions.append(accept)

        return NFA(start, accept)

    elif node.value == '|':
        start = State()
        accept = State(is_accept=True)
        left_nfa = thompson_construct(node.left)
        right_nfa = thompson_construct(node.right)

        start.epsilon_transitions.append(left_nfa.start_state)
        start.epsilon_transitions.append(right_nfa.start_state)
        left_nfa.accept_state.epsilon_transitions.append(accept)
        right_nfa.accept_state.epsilon_transitions.append(accept)

        return NFA(start, accept)

    elif node.value == '.':
        left_nfa = thompson_construct(node.left)
        right_nfa = thompson_construct(node.right)

        left_nfa.accept_state.epsilon_transitions.append(right_nfa.start_state)

        return NFA(left_nfa.start_state, right_nfa.accept_state)

    else:
        start = State()
        accept = State(is_accept=True)
        start.transitions[node.value] = [accept]

        return NFA(start, accept)

def nfa_to_dfa(nfa):
    """
    Convierte el AFN en AFD usando el algoritmo de subconjuntos.
    """
    def epsilon_closure(states):
        closure = set(states)
        stack = list(states)
        while stack:
            state = stack.pop()
            for next_state in state.epsilon_transitions:
                if next_state not in closure:
                    closure.add(next_state)
                    stack.append(next_state)
        return closure

    def move(states, char):
        next_states = set()
        for state in states:
            if char in state.transitions:
                next_states.update(state.transitions[char])
        return next_states

    # Estado inicial del AFD es el epsilon-cierre del estado inicial del AFN
    start_state_closure = epsilon_closure([nfa.start_state])
    start_state = State(is_deterministic=True)
    dfa_states = {frozenset(start_state_closure): start_state}
    unprocessed = [start_state_closure]
    dfa_accept_state = None

    # Mapear los estados de aceptación del AFN
    accept_states_nfa = {nfa.accept_state}

    while unprocessed:
        current_closure = unprocessed.pop()
        current_dfa_state = dfa_states[frozenset(current_closure)]

        # Verificar si el conjunto de estados contiene un estado de aceptación del AFN
        if any(state in accept_states_nfa for state in current_closure):
            current_dfa_state.is_accept = True
            dfa_accept_state = current_dfa_state

        # Procesar cada símbolo del alfabeto (excepto epsilon)
        alphabet = set()
        for state in current_closure:
            alphabet.update(state.transitions.keys())

        for char in alphabet:
            if char == 'ε':
                continue
            next_closure = epsilon_closure(move(current_closure, char))

            if frozenset(next_closure) not in dfa_states:
                new_dfa_state = State(is_deterministic=True)
                dfa_states[frozenset(next_closure)] = new_dfa_state
                unprocessed.append(next_closure)
            else:
                new_dfa_state = dfa_states[frozenset(next_closure)]

            current_dfa_state.transitions[char] = [new_dfa_state]

    return NFA(start_state, dfa_accept_state)


def minimize_dfa_partition_refinement(dfa):
    """
    Minimiza el AFD utilizando el refinamiento de particiones, basado en los estados indistinguibles.
    """
    # Paso 1: Eliminar los estados no alcanzables
    dfa = eliminate_unreachable_states(dfa)

    all_states = list(get_all_states(dfa))

    # Paso 2: Inicialización - Particionar en dos grupos: estados de aceptación y no aceptación
    final_states = {state for state in all_states if state.is_accept}
    non_final_states = {state for state in all_states if not state.is_accept}

    partitions = [final_states, non_final_states]
    work_list = [final_states, non_final_states]  # Para seguir refinando

    # Paso 3: Refinar las particiones
    alphabet = set(char for state in all_states for char in state.transitions.keys())

    while work_list:
        current_partition = work_list.pop()

        # Iterar sobre cada símbolo en el alfabeto
        for char in alphabet:
            # Encontrar el conjunto de estados que transitan hacia la partición actual con el símbolo actual
            involved_states = {state for state in all_states if char in state.transitions and state.transitions[char][0] in current_partition}
            
            new_partitions = []
            for partition in partitions:
                intersect = partition.intersection(involved_states)
                difference = partition.difference(involved_states)

                # Refinar la partición si es necesario
                if intersect and difference:
                    new_partitions.append(intersect)
                    new_partitions.append(difference)

                    # Ver si alguna de las dos particiones debe ser agregada al work_list
                    if partition in work_list:
                        work_list.remove(partition)
                        work_list.append(intersect)
                        work_list.append(difference)
                    else:
                        if len(intersect) <= len(difference):
                            work_list.append(intersect)
                        else:
                            work_list.append(difference)
                else:
                    new_partitions.append(partition)

            partitions = new_partitions

    # Paso 4: Construir el AFD minimizado (omitir particiones vacías)
    minimized_states = {
        frozenset(partition): State(is_accept=next(iter(partition)).is_accept, is_deterministic=True)
        for partition in partitions if partition
    }
    
    # Paso 5: Encontrar la partición que contiene el estado inicial
    start_partition = next(partition for partition in partitions if dfa.start_state in partition)
    minimized_start_state = minimized_states[frozenset(start_partition)]

    # Paso 6: Encontrar la partición que contiene el estado de aceptación y manejar múltiples estados de aceptación
    accept_partition = None
    for partition in partitions:
        if dfa.accept_state in partition:
            accept_partition = partition
            break

    if accept_partition is None:
        raise ValueError("El estado de aceptación no fue encontrado en las particiones.")

    minimized_accept_state = minimized_states[frozenset(accept_partition)]

    # Paso 7: Asignar las transiciones del AFD minimizado
    for partition, minimized_state in minimized_states.items():
        if partition:  # Asegurarse de no iterar sobre particiones vacías
            representative_state = next(iter(partition))
            for char, next_state in representative_state.transitions.items():
                next_partition = next(p for p in partitions if next_state[0] in p)
                minimized_state.transitions[char] = [minimized_states[frozenset(next_partition)]]

    return NFA(minimized_start_state, minimized_accept_state)

def eliminate_unreachable_states(dfa):
    """
    Elimina los estados no alcanzables desde el estado inicial.
    """
    reachable = set()
    to_visit = [dfa.start_state]

    while to_visit:
        state = to_visit.pop()
        if state not in reachable:
            reachable.add(state)
            for next_states in state.transitions.values():
                to_visit.extend(next_states)
    
    # Crear nuevo AFD solo con los estados alcanzables
    return NFA(dfa.start_state, dfa.accept_state if dfa.accept_state in reachable else None)

def get_all_states(dfa):
    """
    Realiza una búsqueda en profundidad para obtener todos los estados del AFD.
    """
    visited = set()
    to_visit = [dfa.start_state]

    while to_visit:
        current = to_visit.pop()
        if current not in visited:
            visited.add(current)
            for next_states in current.transitions.values():
                to_visit.extend(next_states)

    return visited

def draw_dfa(dfa):
    """
    Dibuja el AFD utilizando graphviz.
    """
    dot = graphviz.Digraph()

    def add_state(state):
        shape = 'doublecircle' if state.is_accept else 'circle'
        dot.node(str(id(state)), shape=shape)
        for char, next_states in state.transitions.items():
            for s in next_states:
                dot.edge(str(id(state)), str(id(s)), label=char)

    def traverse(state, visited):
        if state not in visited:
            visited.add(state)
            add_state(state)
            for char, next_states in state.transitions.items():
                for s in next_states:
                    traverse(s, visited)

    traverse(dfa.start_state, set())
    return dot


def simulate_dfa(dfa, string):
    """
    Simula la cadena en el AFD y agrega depuración para verificar las transiciones.
    """
    current_state = dfa.start_state
    print(f"Estado inicial: {id(current_state)} - Aceptación: {current_state.is_accept}")

    for char in string:
        if char in current_state.transitions:
            next_state = current_state.transitions[char][0]
            print(f"Transición con '{char}': {id(current_state)} -> {id(next_state)}")
            current_state = next_state
        else:
            print(f"No hay transición para '{char}' desde el estado {id(current_state)}")
            return False  # Si no hay transición válida, la cadena no pertenece al lenguaje

    print(f"Estado final: {id(current_state)} - Aceptación: {current_state.is_accept}")
    return current_state.is_accept  # Verificar si se alcanza un estado de aceptación


def simulate_nfa(nfa, string):
    current_states = set()
    next_states = set()

    def epsilon_closure(states):
        closure = set(states)
        stack = list(states)
        while stack:
            state = stack.pop()
            for next_state in state.epsilon_transitions:
                if next_state not in closure:
                    closure.add(next_state)
                    stack.append(next_state)
        return closure

    current_states = epsilon_closure([nfa.start_state])

    for char in string:
        for state in current_states:
            if char in state.transitions:
                next_states.update(state.transitions[char])
        current_states = epsilon_closure(next_states)
        next_states.clear()

    return nfa.accept_state in current_states

def draw_nfa(nfa):
    dot = graphviz.Digraph()

    def add_state(state):
        shape = 'doublecircle' if state.is_accept else 'circle'
        dot.node(str(id(state)), shape=shape)
        for char, states in state.transitions.items():
            for s in states:
                dot.edge(str(id(state)), str(id(s)), label=char)
        for s in state.epsilon_transitions:
            dot.edge(str(id(state)), str(id(s)), label='ε')

    def traverse(state, visited):
        if state not in visited:
            visited.add(state)
            add_state(state)
            for char, states in state.transitions.items():
                for s in states:
                    traverse(s, visited)
            for s in state.epsilon_transitions:
                traverse(s, visited)

    traverse(nfa.start_state, set())
    return dot


def process_file(input_file, output_file):
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            # Separar la expresión regular y la cadena
            if ',' not in line:
                continue
            regex, cadena = line.strip().split(',')

            # Extender la expresión regular para manejar operadores adicionales
            extended_regex = extend_regex(regex)
            postfix, steps = infix_to_postfix(extended_regex)
            
            # Escribir información en el archivo de salida
            outfile.write(f"Original: {regex}\n")
            outfile.write(f"Cadena a verificar: {cadena}\n")
            outfile.write(f"Postfix: {postfix}\n")
            outfile.write("Pasos de conversión a Postfix:\n")
            for step in steps:
                outfile.write(f"{step}\n")
            outfile.write("\n")
            
            # Construir el árbol sintáctico (AST) y luego el AFN
            root = postfix_to_ast(postfix)
            nfa = thompson_construct(root)
            
            # Dibujar el AST
            dot_ast = draw_ast(root)
            gv_ast_filename = f'ast_{regex}'
            dot_ast.render(filename=gv_ast_filename, format='png', cleanup=True)
            
            # Dibujar el AFN
            dot_nfa = draw_nfa(nfa)
            gv_nfa_filename = f'nfa_{regex}'
            dot_nfa.render(filename=gv_nfa_filename, format='png', cleanup=True)

            # Simular la cadena con el AFN
            resultado_nfa = "sí" if simulate_nfa(nfa, cadena) else "no"
            outfile.write(f"La cadena '{cadena}' pertenece al lenguaje de la expresión regular según el AFN: {resultado_nfa}\n\n")
            
            # Convertir el AFN a AFD
            dfa = nfa_to_dfa(nfa)

            # Dibujar el AFD
            dot_dfa = draw_dfa(dfa)
            gv_dfa_filename = f'dfa_{regex}'
            dot_dfa.render(filename=gv_dfa_filename, format='png', cleanup=True)

            # Simular la cadena con el AFD
            resultado_dfa = "sí" if simulate_dfa(dfa, cadena) else "no"
            outfile.write(f"La cadena '{cadena}' pertenece al lenguaje de la expresión regular según el AFD: {resultado_dfa}\n\n")

            # Minimizar el AFD y dibujarlo
            minimized_dfa = minimize_dfa_partition_refinement(dfa)
            dot_minimized_dfa = draw_dfa(minimized_dfa)
            gv_min_dfa_filename = f'min_dfa_{regex}'
            dot_minimized_dfa.render(filename=gv_min_dfa_filename, format='png', cleanup=True)

# Archivo de entrada y salida
input_file = 'expresiones.txt'
output_file = 'output_postfix.txt'

# Procesar el archivo
process_file(input_file, output_file)
