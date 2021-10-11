import re
from Scanner.Token import Token

program = "if(b==3){a=3;}else{b=4;}"
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
    if bool(re.match("[a-zA-z]", c)):
        return 1
    elif bool(re.match(("[0-9]", c))):
        return 3
    elif (c == ";" or c == "," or c == ":" or c == "[" or c == "]"
          or c == "{" or c == "}" or c == "(" or c == ")" or c == "+" or c == "-" or c == "<"):
        return 5
    elif c == "=":
        return 6
    elif c == "*":
        return 7
    elif c == "/":
        return 10
    elif c == " " or c == "\n" or c == "\t" or c == "\r" or c == "\f" or c == "\v":
        return 15
    else:
        return -1


###############################
def state1(c):
    if bool(re.match("[a-zA-z0-9]", c)):
        return 1
    elif c in valid_chars:
        return 2
    else:
        return -1


################################
def state2(c):
    return 0


################################
def state3(c):
    if bool(re.match("[0-9]"), c):
        return 3
    elif c in valid_chars:
        return 4
    else:
        return -1


##################################
def state4(c):
    return 0


##################################
def state5(c):
    return 0


##################################
def state6(c):
    if c == "=":
        return 7
    elif c != "=" and (c in valid_chars or bool(re.match("[0-9a-zA-z]", c))):
        return 9
    else:
        return -1


###################################
def state7(c):
    return 0


##################################
def state8(c):
    if c == "/" or (c in valid_chars or bool(re.match("[0-9a-zA-z]", c))) == False:
        return -1
    else:
        return 9


###################################
def state9(c):
    return 0


###################################
def state10(c):
    if c == "/":
        return 11
    elif c == "*":
        return 13
    else:
        return -1


###################################
def state11(c):
    if c == "\n":
        return 12
    else:
        return 11


###################################
def state12(c):
    return 0


###################################
def state13(c):
    if c == "*":
        return 14
    else:
        return 13


####################################
def state14(c):
    if c == "*":
        return 14
    elif c == "/":
        return 12
    else:
        return 13


#####################################
def state15(c):
    return 0


#####################################


def get_next_token():
    token = None
    global current_pointer
    global forward_pointer
    global current_state
    while True:
        if current_state == 0:
            current_state = start_state(program[forward_pointer])
            #forward_pointer = forward_pointer+1

        elif current_state == 1:
            current_state = state1(program[forward_pointer])
            forward_pointer = forward_pointer+1

        elif current_state == 2:
            current_state = state2(program[forward_pointer])
            str = program[current_pointer:forward_pointer-1]
            if str in key_words:
                token = Token("KEYWORD", str)
            else:
                token = Token("ID", str)
            current_pointer = forward_pointer
            if not (str in symbol_table):
                symbol_table.append(str)
            return token

        elif current_state == 3:
            current_state = state3(program[forward_pointer])
            forward_pointer = forward_pointer + 1

        elif current_state == 4:
            current_state = state4(program[forward_pointer])
            str = program[current_pointer:forward_pointer]
            current_pointer = forward_pointer
            token = Token("NUM", str)
            return token


        elif current_state == 5:
            current_state = state5(program[forward_pointer])
            str = program[forward_pointer]
            forward_pointer = forward_pointer+1
            current_pointer = current_pointer
            token = Token("SYMBOL", str)
            return token

        elif current_state == 6:
            current_state = state6(program[forward_pointer])
            forward_pointer = forward_pointer + 1

        elif current_state == 7:
            current_state = state7(program[forward_pointer])


        elif current_state == 8:
            current_state = state8(program[forward_pointer])

        elif current_state == 9:
            current_state = state9(program[forward_pointer])

        elif current_state == 10:
            current_state = state10(program[forward_pointer])

        elif current_state == 11:
            current_state = state11(program[forward_pointer])

        elif current_state == 12:
            current_state = state12(program[forward_pointer])

        elif current_state == 13:
            current_state = state13(program[forward_pointer])

        elif current_state == 14:
            current_state = state14(program[forward_pointer])

        elif current_state == 15:
            current_state = state15(program[forward_pointer])

        elif current_state == -1:
            current_state = state15(program[forward_pointer])
