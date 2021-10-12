from Scanner.scanner import Scanners

scanner = Scanners()

while True:
    tokens = scanner.get_next_token()
    if type(tokens) == bool:
        break
    str = tokens.value + "---->" + tokens.token_kind
    print(str)

if scanner.current_state == 13:
    str = scanner.program[scanner.current_pointer:scanner.current_pointer + 7] + "..."
    print(str)
