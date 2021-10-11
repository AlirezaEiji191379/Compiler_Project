import re
from Scanner.Token import Token

program = """if(b=3)
    {
       a==3d;
       4*/4
    }
    else{
      b==4;
    }
"""
key_words = ("if", "else", "void", "int", "repeat", "break", "until", "return")
valid_chars = (
    ";", ",", ":", "[", "]", "{", "}", "(", ")", "+", "-", "<", "=", "*", " ", "\n", "\t", "\r", "\f", "\v", "/")

symbol_table = list()
error_list = list()

lineno = 1
current_pointer = 0
forward_pointer = 0
current_state = 0


####################################
def start_state(c):
    global current_pointer
    global forward_pointer
    if bool(re.match("[a-zA-z]", c)):
        forward_pointer = forward_pointer + 1
        return 1
    elif bool(re.match("[0-9]", c)):
        forward_pointer = forward_pointer + 1
        return 3
    elif (c == ";" or c == "," or c == ":" or c == "[" or c == "]"
          or c == "{" or c == "}" or c == "(" or c == ")" or c == "+" or c == "-" or c == "<"):
        return 5
    elif c == "=":
        forward_pointer = forward_pointer + 1
        return 6
    elif c == "*":
        forward_pointer = forward_pointer+1
        return 8
    elif c == "/":
        forward_pointer = forward_pointer + 1
        return 10
    elif c == " " or c == "\n" or c == "\t" or c == "\r" or c == "\f" or c == "\v":
        return 15
    else:
        return -1


###############################
def state1(c):
    global current_pointer
    global forward_pointer
    if bool(re.match("[a-zA-z0-9]", c)):
        forward_pointer = forward_pointer + 1
        return 1
    elif c in valid_chars:
        return 2
    else:
        return -1


################################
def state2():
    global current_pointer
    global forward_pointer
    global program
    global symbol_table
    str = program[current_pointer:forward_pointer]
    token = None
    if not (str in symbol_table):
        symbol_table.append(str)

    if token in key_words:
        token = Token("KEYWORD", str)
    else:
        token = Token("ID", str)

    current_pointer = forward_pointer
    return 0, token


################################
def state3(c):
    global current_pointer
    global forward_pointer
    if bool(re.match("[0-9]", c)):
        forward_pointer = forward_pointer + 1
        return 3
    elif c in valid_chars:
        return 4
    else:
        return -1


##################################
def state4():
    global current_pointer
    global forward_pointer
    global program
    str = program[current_pointer:forward_pointer]
    token = Token("NUM", str)
    current_pointer = forward_pointer
    return 0, token


##################################
def state5():
    global current_pointer
    global forward_pointer
    str = program[forward_pointer]
    forward_pointer = forward_pointer + 1
    current_pointer = forward_pointer
    token = Token("SYMBOL", str)
    return 0, token


##################################
def state6(c):
    if c == "=":
        return 7
    elif c != "=" and (c in valid_chars or bool(re.match("[0-9a-zA-z]", c))):
        return 9
    else:
        return -1


###################################
def state7():
    global forward_pointer
    global current_pointer
    forward_pointer = forward_pointer + 1
    str = program[current_pointer:forward_pointer]
    current_pointer = forward_pointer
    token = Token("SYMBOL", str)
    return 0, token


##################################
def state8(c):
    global current_pointer
    global forward_pointer
    if c == "/":
        return -1
    else:
        return 9


###################################
def state9():
    global forward_pointer
    global current_pointer
    str = program[current_pointer:forward_pointer]
    token = Token("SYMBOL", str)
    current_pointer = forward_pointer
    return 0, token


###################################
def state10(c):
    global current_pointer
    global forward_pointer
    if c == "/":
        forward_pointer = forward_pointer + 1
        return 11
    elif c == "*":
        forward_pointer = forward_pointer + 1
        return 13
    else:
        return -1


###################################
def state11(c):
    global current_pointer
    global forward_pointer
    if c == "\n":
        return 12
    else:
        forward_pointer = forward_pointer + 1
        return 11


###################################
def state12():
    global current_pointer
    global forward_pointer
    forward_pointer = forward_pointer + 1
    current_pointer = forward_pointer
    return 0


###################################
def state13(c):
    global current_pointer
    global forward_pointer
    if c == "*":
        forward_pointer = forward_pointer + 1
        return 14
    else:
        forward_pointer = forward_pointer + 1
        return 13


####################################
def state14(c):
    global current_pointer
    global forward_pointer
    if c == "*":
        forward_pointer = forward_pointer + 1
        return 14
    elif c == "/":
        return 12
    else:
        forward_pointer = forward_pointer + 1
        return 13


#####################################
def state15(c):
    global lineno
    global forward_pointer
    global current_pointer
    forward_pointer = forward_pointer + 1
    current_pointer = forward_pointer
    if c == "\n":
        lineno = lineno + 1
    return 0


#####################################
def error_state():
    global forward_pointer
    global current_pointer
    global program
    print(program[current_pointer:forward_pointer+1])
    forward_pointer = forward_pointer+1
    current_pointer = forward_pointer
    return 0


def get_next_token():
    compiler_token = None
    global current_pointer
    global forward_pointer
    global current_state
    size = len(program)
    while True:
        #print(current_state)
        if forward_pointer == size:
            return False
        if current_state == 0:
            current_state = start_state(program[forward_pointer])
            #print(current_state)

        elif current_state == 1:
            current_state = state1(program[forward_pointer])

        elif current_state == 2:
            current_state, compiler_token = state2()
            return compiler_token

        elif current_state == 3:
            current_state = state3(program[forward_pointer])

        elif current_state == 4:
            current_state, compiler_token = state4()
            return compiler_token

        elif current_state == 5:
            current_state, compiler_token = state5()
            return compiler_token

        elif current_state == 6:
            current_state = state6(program[forward_pointer])

        elif current_state == 7:
            current_state, compiler_token = state7()
            return compiler_token

        elif current_state == 8:
            current_state = state8(program[forward_pointer])

        elif current_state == 9:
            current_state, compiler_token = state9()
            return compiler_token

        elif current_state == 10:
            current_state = state10(program[forward_pointer])

        elif current_state == 11:
            current_state = state11(program[forward_pointer])

        elif current_state == 12:
            current_state = state12()

        elif current_state == 13:
            current_state = state13(program[forward_pointer])

        elif current_state == 14:
            current_state = state14(program[forward_pointer])

        elif current_state == 15:
            current_state = state15(program[forward_pointer])

        elif current_state == -1:
            current_state = error_state()
        #print(forward_pointer)


# t = len(program)
# print(t)

while True:
    tokens = get_next_token()
    if type(tokens) == bool:
        break
    str = tokens.value + "---->" + tokens.token_kind
    print(str)

#print(symbol_table)
#print(lineno)
