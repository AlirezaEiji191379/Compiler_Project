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
ll1_table = {}
grammar_production_rules = []
no_error = True


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
            return "(" + self.token[0] + ", " + self.token[1] + ") "
        if self.value == 'ε':
            return 'epsilon'
        return self.value


def split_grammar_rules():
    global grammar_production_rules
    grammar = open('grammar.txt', 'r').read()
    grammar_production_rules = re.split('\n', grammar)
    for i in range(0, len(grammar_production_rules)):
        grammar_production_rules[i] = re.split(' -> | ', grammar_production_rules[i])


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

def create_diagrams():
    diagram = {}
    for rule in grammar_production_rules:
        key = rule[0]
        if key not in diagram:
            diagram[key] = []
        terms_list = []    
        for term in rule[1:]:
            terms_list.append(term)
        diagram[key].append(terms_list)

    print(diagram)

if __name__ == '__main__':

    split_grammar_rules()
    find_terminals_and_non_terminals()
    set_first_and_follows()
    create_diagrams()
    



# from Scanner.LexicalError import LexicalError
# from Scanner.scanner import Scanners
# import re

# f = open("input.txt", "r")
# inputFile = f.read() + " "
# scanner = Scanners(inputFile)


# while True:
#     tokens = scanner.get_next_token()
#     if type(tokens) == bool:
#         break
#     tokenValue_Kind = tokens.value + "---->" + tokens.token_kind
#     #print(tokenValue_Kind)

# if scanner.current_state == 13:
#     errorPart = scanner.program[scanner.current_pointer:scanner.current_pointer + 7] + "..."
#     scanner.error_list.append(LexicalError(errorPart, "Unclosed comment", scanner.star_comment_line))

# print()
# print("tokens: ")
# size = len(scanner.tokens_list)

# currentLineNo = 0
# tokensFileContent = ''

# for i in range(size):
#     if currentLineNo != scanner.tokens_list[i].lineno:
#         currentLineNo = scanner.tokens_list[i].lineno
#         if i != 0: tokensFileContent += '\n'
#         tokensFileContent += str(currentLineNo) + '.\t'
#     tokensFileContent += "(" + scanner.tokens_list[i].token_kind + ", " + scanner.tokens_list[i].value + ") "

# print(tokensFileContent)
# f = open('tokens.txt', 'w')
# f.write(tokensFileContent)

# print()
# print("errors :")

# size = len(scanner.error_list)
# currentLineNo = 0

# errorsFileContent = '' if size != 0 else 'There is no lexical error.'
# for i in range(size):
#     if currentLineNo != scanner.error_list[i].lineno:
#         currentLineNo = scanner.error_list[i].lineno
#         if i!=0:errorsFileContent += '\n'
#         errorsFileContent += str(currentLineNo) + '.\t'
#     errorsFileContent += "(" + scanner.error_list[i].error + ", " + scanner.error_list[i].error_kind + ") "

# print(errorsFileContent)
# f = open('lexical_errors.txt', 'w')
# f.write(errorsFileContent)

# print()
# print("symbol table")

# tableFileContent = ''
# for i in range(len(scanner.symbol_table)):
#     tableFileContent += str(i + 1) + '.  ' + scanner.symbol_table[i] + '\n'
# print(tableFileContent)
# f = open('symbol_table.txt', 'w')
# f.write(tableFileContent)
