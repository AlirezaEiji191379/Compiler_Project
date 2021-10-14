import re

from Scanner.LexicalError import LexicalError
from Scanner.Token import Token


class Scanners:
    program = """"""

    key_words = ("if", "else", "void", "int", "repeat", "break", "until", "return")
    valid_chars = (
        ";", ",", ":", "[", "]", "{", "}", "(", ")", "+", "-", "<", "=", "*", " ", "\n", "\t", "\r", "\f", "\v", "/")

    symbol_table = list()
    error_list = list()
    tokens_list = list()
    star_comment_line = -1
    lineno = 1
    current_pointer = 0
    forward_pointer = 0
    current_state = 0
    size = 0

    def __init__(self, input):
        self.program = input
        print(self.program)
        self.size = len(input)
        self.symbol_table += ['if', 'else', 'void', 'int', 'repeat', 'break', 'until', 'return']
        pass

    def start_state(self, c):
        if bool(re.match("[a-zA-Z]", c)):
            self.forward_pointer = self.forward_pointer + 1
            return 1
        elif bool(re.match("[0-9]", c)):
            self.forward_pointer = self.forward_pointer + 1
            return 3
        elif (c == ";" or c == "," or c == ":" or c == "[" or c == "]"
              or c == "{" or c == "}" or c == "(" or c == ")" or c == "+" or c == "-" or c == "<"):
            return 5
        elif c == "=":
            self.forward_pointer = self.forward_pointer + 1
            return 6
        elif c == "*":
            self.forward_pointer = self.forward_pointer + 1
            return 8
        elif c == "/":
            self.forward_pointer = self.forward_pointer + 1
            return 10
        elif c == " " or c == "\n" or c == "\t" or c == "\r" or c == "\f" or c == "\v":
            return 15
        else:
            return -1

    def state1(self, c):
        if bool(re.match("[a-zA-Z0-9]", c)):
            self.forward_pointer = self.forward_pointer + 1
            return 1
        elif c in self.valid_chars:
            return 2
        else:
            return -1

    def state2(self):
        str = self.program[self.current_pointer:self.forward_pointer]
        token = None
        if str in self.key_words:
            token = Token("KEYWORD", str, self.lineno)

        else:
            token = Token("ID", str, self.lineno)
            if not (str in self.symbol_table):
                self.symbol_table.append(str)

        self.current_pointer = self.forward_pointer
        return 0, token

    def state3(self, c):
        if bool(re.match("[0-9]", c)):
            self.forward_pointer = self.forward_pointer + 1
            return 3
        elif c in self.valid_chars:
            return 4
        else:
            return -1

    def state4(self):
        str = self.program[self.current_pointer:self.forward_pointer]
        token = Token("NUM", str, self.lineno)
        self.current_pointer = self.forward_pointer
        return 0, token

    def state5(self):
        str = self.program[self.forward_pointer]
        self.forward_pointer = self.forward_pointer + 1
        self.current_pointer = self.forward_pointer
        token = Token("SYMBOL", str, self.lineno)
        return 0, token

    def state6(self, c):
        if c == "=":
            return 7
        elif c != "=" and (c in self.valid_chars or bool(re.match("[0-9a-zA-Z]", c))):
            return 9
        else:
            return -1

    def state7(self):
        self.forward_pointer = self.forward_pointer + 1
        str = self.program[self.current_pointer:self.forward_pointer]
        self.current_pointer = self.forward_pointer
        token = Token("SYMBOL", str, self.lineno)
        return 0, token

    def state8(self, c):
        if c == "/":
            return -1
        elif not (c in self.valid_chars or bool(re.match("[0-9a-zA-Z]", c))):
            return -1
        else:
            return 9

    def state9(self):
        str = self.program[self.current_pointer:self.forward_pointer]
        token = Token("SYMBOL", str, self.lineno)
        self.current_pointer = self.forward_pointer
        return 0, token

    def state10(self, c):
        if c == "/":
            self.forward_pointer = self.forward_pointer + 1
            return 11
        elif c == "*":
            self.forward_pointer = self.forward_pointer + 1
            return 13
        else:
            return -1

    def state11(self, c):
        if c == "\n":
            self.lineno = self.lineno + 1
            return 12
        else:
            self.forward_pointer = self.forward_pointer + 1
            return 11

    def state12(self):
        self.star_comment_line = -1
        self.forward_pointer = self.forward_pointer + 1
        self.current_pointer = self.forward_pointer
        return 0

    def state13(self, c):
        if self.star_comment_line == -1:
            self.star_comment_line = self.lineno
        if c == "*":
            self.forward_pointer = self.forward_pointer + 1
            return 14
        else:
            if c == "\n":
                self.lineno = self.lineno + 1
            self.forward_pointer = self.forward_pointer + 1
            return 13

    def state14(self, c):
        if c == "*":
            self.forward_pointer = self.forward_pointer + 1
            return 14
        elif c == "/":
            return 12
        else:
            self.forward_pointer = self.forward_pointer + 1
            return 13

    def state15(self, c):
        self.forward_pointer = self.forward_pointer + 1
        self.current_pointer = self.forward_pointer
        if c == "\n":
            self.lineno = self.lineno + 1
        return 0

    def error_state(self):
        str = self.program[self.current_pointer:self.forward_pointer + 1]
        error = None
        if bool(re.match("[0-9]", str)):
            error = LexicalError(str, "Invalid number", self.lineno)
        elif str == "*/":
            error = LexicalError(str, "Unmatched comment", self.lineno)
        else:
            error = LexicalError(str, "Invalid input", self.lineno)

        self.error_list.append(error)
        self.forward_pointer = self.forward_pointer + 1
        self.current_pointer = self.forward_pointer
        return 0

    def get_next_token(self):
        while True:
            if self.forward_pointer == self.size:
                return False

            if self.current_state == 0:
                self.current_state = self.start_state(self.program[self.forward_pointer])

            elif self.current_state == 1:
                self.current_state = self.state1(self.program[self.forward_pointer])

            elif self.current_state == 2:
                self.current_state, compiler_token = self.state2()
                self.tokens_list.append(compiler_token)
                return compiler_token

            elif self.current_state == 3:
                self.current_state = self.state3(self.program[self.forward_pointer])
                # print(self.program[self.forward_pointer])


            elif self.current_state == 4:
                self.current_state, compiler_token = self.state4()
                self.tokens_list.append(compiler_token)
                return compiler_token

            elif self.current_state == 5:
                self.current_state, compiler_token = self.state5()
                self.tokens_list.append(compiler_token)
                return compiler_token

            elif self.current_state == 6:
                self.current_state = self.state6(self.program[self.forward_pointer])

            elif self.current_state == 7:
                self.current_state, compiler_token = self.state7()
                self.tokens_list.append(compiler_token)
                return compiler_token

            elif self.current_state == 8:
                self.current_state = self.state8(self.program[self.forward_pointer])

            elif self.current_state == 9:
                self.current_state, compiler_token = self.state9()
                self.tokens_list.append(compiler_token)
                return compiler_token

            elif self.current_state == 10:
                self.current_state = self.state10(self.program[self.forward_pointer])

            elif self.current_state == 11:
                self.current_state = self.state11(self.program[self.forward_pointer])

            elif self.current_state == 12:
                self.current_state = self.state12()

            elif self.current_state == 13:
                self.current_state = self.state13(self.program[self.forward_pointer])

            elif self.current_state == 14:
                self.current_state = self.state14(self.program[self.forward_pointer])

            elif self.current_state == 15:
                self.current_state = self.state15(self.program[self.forward_pointer])

            elif self.current_state == -1:
                self.current_state = self.error_state()
