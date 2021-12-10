from typing import Type
from Scanner.LexicalError import LexicalError
from Scanner.Token import Token
from Scanner.scanner import Scanners
import re
import operator

f = open("input.txt", "r")
inputFile = f.read() + " "
scanner = Scanners(inputFile)

errors = open('syntax_errors.txt', 'w')
parse_tree = open('parse_tree.txt', 'w')
non_terminals_set = set()
terminals_set = set()
grammar_production_rules = []
no_error = True
input_finished = False
epsilonGrammerRules = ['Declaration-list', 'Param-list', 'Param-prime',
                       'Statement-list', 'C', 'D', 'G', 'Var-prime', 'Factor-prime', 'Args', 'Arg-list-prime']

current_token = None


def split_grammar_rules():
    global grammar_production_rules
    grammar = open('grammar.txt', 'r').read()
    grammar_production_rules = re.split('\n', grammar)
    for i in range(0, len(grammar_production_rules)):
        grammar_production_rules[i] = re.split(
            ' -> | ', grammar_production_rules[i])


def find_terminals_and_non_terminals():
    global non_terminals_set, terminals_set
    for rule in grammar_production_rules:
        non_terminals_set.add(rule[0])
    for rule in grammar_production_rules:
        for T_or_NT in rule:
            if T_or_NT not in non_terminals_set:
                terminals_set.add(T_or_NT)


def convert_file_to_dict(file):
    all_terms = open(file, 'r').read()
    all_terms = re.split('\n', all_terms)
    for i in range(0, len(all_terms)):
        all_terms[i] = re.split(' ', all_terms[i])
    output_dict = {}
    for term in all_terms:
        key = term[0]
        output_dict[key] = set()
        for node in term[1:]:
            output_dict[key].add(node)
    return output_dict


def set_first_and_follows():
    global firsts, follows
    firsts = convert_file_to_dict("firsts.txt")
    for terminal in terminals_set:
        firsts[terminal] = {terminal}
    follows = convert_file_to_dict("follows.txt")


def get_token_value_or_kind():
    inputTokenValue = ''
    if current_token.token_kind == 'SYMBOL':
        inputTokenValue = current_token.value
    elif current_token.token_kind == 'ID':
        inputTokenValue = current_token.token_kind
    elif current_token.token_kind == 'KEYWORD':
        inputTokenValue = current_token.value
    elif current_token.token_kind == 'NUM':
        inputTokenValue = current_token.token_kind
    # should be replaced with: 'elif current_token == '$:'
    elif current_token.token_kind == 'EOF':
        inputTokenValue = '$'
    return inputTokenValue


def create_diagrams():
    global diagram
    diagram = {}
    for rule in grammar_production_rules:
        key = rule[0]
        if key not in diagram:
            diagram[key] = []
        terms_list = []
        for term in rule[1:]:
            terms_list.append(term)
        diagram[key].append(terms_list)


def run_a_diagram(diagram_name):
    global current_token, all_nodes
    selected_path = select_best_path(diagram_name)

    print('current token:', get_token_value_or_kind())
    print('we are in diagram of: ', diagram_name,
          '     selected path is:', selected_path)

    go_through_path(selected_path, diagram_name)


def select_best_path(diagram_name):
    selected_path = []
    for path in diagram[diagram_name]:
        first_edge_in_path = path[0]
        inputTokenToCompare = get_token_value_or_kind()
        print("first edge in path: " + first_edge_in_path)
        if first_edge_in_path in non_terminals_set:
            if(inputTokenToCompare in firsts[first_edge_in_path]):
                selected_path = path
                break

            elif(inputTokenToCompare in follows[first_edge_in_path] and ("EPSILON" in firsts[first_edge_in_path])):
                selected_path = path
                break
                #print('epsilon move in diagram: ', diagram_name)

        if first_edge_in_path in terminals_set:
            if first_edge_in_path == inputTokenToCompare:
                selected_path = path
                break

        if(inputTokenToCompare in follows[diagram_name]) and (diagram_name in epsilonGrammerRules):
            selected_path = ['EPSILON']
            print('epsilon move in diagram: ', diagram_name)
            break

    if(len(selected_path) == 0):
        pass
        # handle error: no suitable path in the diagram

    return selected_path


def go_through_path(selected_path, diagram_name):
    for edge in selected_path:
        global current_token
        print('diagram:', diagram_name, '    edge:', edge)

        # parent is not true:
        parent_node = getNodeByValue(diagram_name)
        current_node = TreeNode(edge, parent=parent_node)
        parent_node.add_child(current_node)

        all_nodes.append(current_node)
        if(edge in terminals_set):
            if(match(edge)):
                current_node.set_token(current_token)
                current_token = scanner.get_next_token()
                if(current_token == False):
                    print('input finished')
                    global input_finished
                    input_finished = True
                    current_token = Token('EOF', '$', 100)
                    return
                else:
                    print(
                        'two terminals are matched and next token will be: ', current_token.value)
                    # return
            else:
                print('two terminals not match')
                # handle error: two terminals not match
        else:
            print('\n...running diagram of: ', edge)
            run_a_diagram(edge)
            print('finished the diagram of: ', edge)
    if input_finished:
        return


def match(expected_token_value):
    if(get_token_value_or_kind() == expected_token_value):
        return True
    else:
        # error handling
        return False


class TreeNode:
    def __init__(self, value, width=0, parent=None):
        self.parent = parent
        self.value = value
        self.children = []
        self.width = width
        self.depth = 0
        self.height = 0
        self.is_terminal = False
        self.token = None

    def add_child(self, child):
        self.children.append(child)
        child.width = self.width + 1

    def is_leave(self):
        return len(self.children) == 0

    def __str__(self):
        return str(self.value) + " " + str(self.width) + " " + str(self.depth)

    def set_token(self, token):
        self.token = token
        self.is_terminal = True

    def show(self):
        if self.is_terminal:
            return "(" + self.token.token_kind + ", " + self.token.value + ") "
        if self.value == 'ε':
            return 'epsilon'
        return self.value


def calculate_depth():
    global head_node

    def visit(node):
        if node.is_leave():
            return
        depth = node.depth + 1
        node.height = 0
        for index in range(len(node.children) - 1, -1, -1):
            child = node.children[index]
            child.depth = depth
            visit(child)
            depth += child.height + 1
            node.height += child.height + 1

    visit(head_node)


def getNodeByValue(value):
    global all_nodes

    for node in all_nodes:
        if node.value == value:
            return node
    return None


horizontal_lines = [0]


def draw_tree():
    global horizontal_lines
    for node in all_nodes:
        for child in node.children:
            horizontal_lines.append(child.width)
        for counter in range(0, node.width - 1):
            if counter + 1 in horizontal_lines:
                parse_tree.write('|   ')
            else:
                parse_tree.write('    ')
        if node.width != 0:
            if node == node.parent.children[0]:
                parse_tree.write('L--- ')
            else:
                parse_tree.write('|--- ')
        horizontal_lines.remove(node.width)
        parse_tree.write(f'{node.show()}\n')


if __name__ == '__main__':

    split_grammar_rules()
    find_terminals_and_non_terminals()
    set_first_and_follows()
    create_diagrams()

    head_node = TreeNode('Program')
    all_nodes = [head_node]
    current_token = scanner.get_next_token()
    run_a_diagram("Program")
    print('\nnodes:')
    for node in all_nodes:
        print(node.value)
    print("***************************************")

    calculate_depth()
    # all_nodes.sort(key=operator.attrgetter('depth'))
    draw_tree()
    parse_tree.close()
    errors.close()
    # if no_error:
    #     errors.write('There is no syntax error.')
