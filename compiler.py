from Scanner.LexicalError import LexicalError
from Scanner.scanner import Scanners
import re

f = open("input.txt", "r")
inputFile = f.read()
scanner = Scanners(inputFile)
print("program: ")

print(scanner.program)

while True:
    tokens = scanner.get_next_token()
    if type(tokens) == bool:
        break
    tokenValue_Kind = tokens.value + "---->" + tokens.token_kind

if scanner.current_state == 13:
    errorPart = scanner.program[scanner.current_pointer:scanner.current_pointer + 7] + "..."
    scanner.error_list.append(LexicalError(errorPart, "Unclosed comment", scanner.star_comment_line))

print()
print("tokens: ")
size = len(scanner.tokens_list)

currentLineNo = 0
tokensFileContent = ''

for i in range(size):
    if (currentLineNo != scanner.tokens_list[i].lineno):
        currentLineNo = scanner.tokens_list[i].lineno
        if (i != 0): tokensFileContent += '\n'
        tokensFileContent += str(currentLineNo) + '.\t'
    tokensFileContent += "(" + scanner.tokens_list[i].token_kind + ", " + scanner.tokens_list[i].value + ") "

print(tokensFileContent)
f = open('tokens.txt', 'w')
f.write(tokensFileContent)

print()
print("errors :")

size = len(scanner.error_list)
currentLineNo = 0

errorsFileContent = '' if size != 0 else 'There is no lexical error.'
for i in range(size):
    if currentLineNo != scanner.error_list[i].lineno:
        currentLineNo = scanner.error_list[i].lineno
        errorsFileContent += '\n'
        errorsFileContent += str(currentLineNo) + '.\t'
    errorsFileContent += "(" + scanner.error_list[i].error + ", " + scanner.error_list[i].error_kind + ") "

print(errorsFileContent)
f = open('lexical_errors.txt', 'w')
f.write(errorsFileContent)

print()
print("symbol table")

tableFileContent = ''
for i in range(len(scanner.symbol_table)):
    tableFileContent += str(i + 1) + '.  ' + scanner.symbol_table[i] + '\n'
print(tableFileContent)
f = open('symbol_table.txt', 'w')
f.write(tableFileContent)
