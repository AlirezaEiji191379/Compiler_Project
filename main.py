from Scanner.LexicalError import LexicalError
from Scanner.scanner import Scanners

f = open("input.txt", "r")
inputFile = f.read()
scanner = Scanners(inputFile)

while True:
    tokens = scanner.get_next_token()
    if type(tokens) == bool:
        break
    str = tokens.value + "---->" + tokens.token_kind

if scanner.current_state == 13:
    str = scanner.program[scanner.current_pointer:scanner.current_pointer + 7] + "..."
    scanner.error_list.append(LexicalError(str, "unclosed comment", scanner.star_comment_line))

print()
print("tokens: ")
size = len(scanner.tokens_list)

for i in range(size):
    string = "{}. " + "({}," + scanner.tokens_list[i].token_kind + ")"
    print(string.format(scanner.tokens_list[i].lineno,scanner.tokens_list[i].value))

print()
print("errors :")
size = len(scanner.error_list)

for i in range(size):
    string = "{}. " + "({}" + "," + scanner.error_list[i].error_kind + ")"
    print(string.format(scanner.error_list[i].lineno,scanner.error_list[i].error))

print()
print("symbol table")
print(scanner.symbol_table)
