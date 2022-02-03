from Scanner.Token import Token


class CodeGenerator:

    lastTempAddress = 100
    symbol_table = []
    scope_stack = []
    sematic_stack = []
    program_block = []
    breaks = []
    returns = []
    state = 0

    def create_outputs(self):
        output = open('output.txt', 'w')
        semantic = open('semantic_errors.txt', 'w', encoding='utf-8')
        semantic.write("The input program is semantically correct.")
        print(self.program_block)
        for i in range(0, len(self.program_block)):
            output.write(f'{i}\t{self.program_block[i]}\n')

        output.close()
        semantic.close()

    def initVar(self, id, type, attributes):
        if type == 'int':
            address = self.getTempVar()
        elif type == 'array':
            address = self.getTempVar()
            array = self.getTempVar(int(attributes))
            self.addToProgramBlock(self.state, 'ASSIGN', f'#{array}', address)
            self.state += 1
        self.symbol_table.append((id, type, address))

    def addToProgramBlock(self, index, operand, r1, r2='', r3=''):
        while len(self.program_block) <= index:
            self.program_block.append('')
        self.program_block[index] = f'({operand}, {r1}, {r2}, {r3})'

    def getTempVar(self, count=1):
        output = str(self.lastTempAddress)
        for w in range(0, count):
            self.addToProgramBlock(self.state, 'ASSIGN', '#0',
                                   str(self.lastTempAddress))
            self.state += 1
            self.lastTempAddress += 4
        return output

    def end(self):
        top_value = self.scope_stack.pop()
        while top_value < len(self.symbol_table):
            self.symbol_table.pop()

    def start(self):
        self.scope_stack.append(len(self.symbol_table))

    def findIdAddress(self, id):
        if id == 'output':
            return 'output'
        for index in range(len(self.symbol_table) - 1, -1, -1):
            row = self.symbol_table[index]
            if id == row[0]:
                return row[2]

    def pid(self, current_token: Token):
        p = self.findIdAddress(current_token.value)
        self.sematic_stack.append(p)

    def pnum(self, currentToken):
        self.sematic_stack.append('#' + currentToken.value)

    def mult(self):
        t = self.getTempVar()
        top = len(self.sematic_stack) - 1
        self.addToProgramBlock(
            self.state, 'MULT', self.sematic_stack[top], self.sematic_stack[top - 1], t)
        self.state += 1
        self.sematic_stack.pop()
        self.sematic_stack.pop()
        self.sematic_stack.append(t)

    def setVar(self):
        self.initVar(self.sematic_stack.pop(), 'int', "")

    def setArr(self):
        size = self.sematic_stack.pop()
        self.initVar(self.sematic_stack.pop(), 'array', size[1:])

    def assign(self):
        top = len(self.sematic_stack) - 1
        self.addToProgramBlock(
            self.state, 'ASSIGN', self.sematic_stack[top], self.sematic_stack[top - 1])
        self.state += 1
        self.sematic_stack.pop()

    def index(self):
        index = self.sematic_stack.pop()
        address = self.sematic_stack.pop()
        t1 = self.getTempVar()
        self.addToProgramBlock(self.state, 'MULT', '#4', index, t1)
        self.state += 1
        t2 = self.getTempVar()
        self.addToProgramBlock(self.state, 'ASSIGN', f'@{address}', t2)
        self.state += 1
        self.addToProgramBlock(self.state, 'ADD', t2, t1, t1)
        self.state += 1
        self.sematic_stack.append('@' + t1)

    def pop(self):
        self.sematic_stack.pop()

    def saveip(self, current_token):
        self.sematic_stack.append(current_token.value)

    def operation(self):
        second_operand = self.sematic_stack.pop()
        operator = self.sematic_stack.pop()
        first_operand = self.sematic_stack.pop()
        t = self.getTempVar()
        if operator == '+':
            self.addToProgramBlock(
                self.state, 'ADD', first_operand, second_operand, t)
        elif operator == '-':
            self.addToProgramBlock(
                self.state, 'SUB', first_operand, second_operand, t)
        elif operator == '<':
            self.addToProgramBlock(
                self.state, 'LT', first_operand, second_operand, t)
        elif operator == '==':
            self.addToProgramBlock(
                self.state, 'EQ', first_operand, second_operand, t)
        self.sematic_stack.append(t)
        self.state += 1

    def signed(self):
        top_value = self.sematic_stack.pop()
        t = self.getTempVar()
        self.addToProgramBlock(self.state, 'SUB', '#0', top_value, t)
        self.state += 1
        self.sematic_stack.append(t)

    def outputIn(self):
        if self.sematic_stack[len(self.sematic_stack) - 2] != 'output':
            return
        top_value = self.sematic_stack.pop()
        self.addToProgramBlock(self.state, 'PRINT', top_value)
        self.state += 1

    def jpfSave(self):
        index = self.sematic_stack.pop()
        expression = self.sematic_stack.pop()
        self.addToProgramBlock(index, 'JPF', expression, str(self.state + 1))
        self.sematic_stack.append(self.state)
        self.state += 1

    def save(self):
        global state
        self.sematic_stack.append(self.state)
        self.state += 1

    def jpfSaveNoElse(self):
        index = self.sematic_stack.pop()
        expression = self.sematic_stack.pop()
        self.addToProgramBlock(index, 'JPF', expression, str(self.state))

    def jump(self):
        index = self.sematic_stack.pop()
        self.addToProgramBlock(int(index), 'JP', self.state)

    def lablel(self):
        self.sematic_stack.append(self.state)

    def numericLabel(self):
        self.sematic_stack.append(f'#{self.state}')

    def repeat(self):
        expression = self.sematic_stack.pop()
        label = self.sematic_stack.pop()
        self.addToProgramBlock(self.state, 'JPF', expression, label)
        self.state += 1

    def startSymbol(self):
        self.symbol_table.append('STOP')

    def add_function_to_symbol_table(self):
        length = len(self.sematic_stack)
        attributes = []
        function_name = self.sematic_stack[length - 4]
        last_object_of_symbol_table = self.symbol_table.pop()
        while last_object_of_symbol_table != 'STOP':
            attributes.append(last_object_of_symbol_table[2])
            last_object_of_symbol_table = self.symbol_table.pop()
        attributes.append(self.sematic_stack[length - 3])
        attributes.reverse()
        attributes.append(self.sematic_stack[length - 2])
        attributes.append(self.sematic_stack[length - 1])
        self.symbol_table.append((function_name, 'function', attributes))
        self.sematic_stack.pop()
        self.sematic_stack.pop()
        self.sematic_stack.pop()
        self.sematic_stack.pop()

    def init_variable(self):
        address = self.getTempVar()
        self.sematic_stack.append(address)

    def return_address(self):
        if self.sematic_stack[len(self.sematic_stack) - 4] == 'main':
            return
        return_value = self.sematic_stack[len(self.sematic_stack) - 2]
        self.addToProgramBlock(self.state, 'JP', f'@{return_value}')
        self.state = self.state + 1

    def breakCode(self):
        self.breaks.append(self.state)
        self.state += 1

    def start_break(self):
        self.breaks.append("start")

    def endbreak(self):
        index = self.breaks.pop()
        while index != 'start':
            self.addToProgramBlock(index, 'JP', self.state)
            index = self.breaks.pop()

    def returnSymbol(self):
        value = self.sematic_stack.pop()
        self.returns.append((self.state, value))
        self.state += 2

    def start_return(self):
        self.returns.append(("start", '#0'))

    def end_return(self):
        index = self.returns.pop()
        while index[0] != 'start':
            self.addToProgramBlock(
                index[0], 'ASSIGN', index[1], self.sematic_stack[len(self.sematic_stack) - 1])
            self.addToProgramBlock(index[0] + 1, 'JP', self.state)
            index = self.returns.pop()

    def call_function(self):
        if self.sematic_stack[len(self.sematic_stack) - 1] == 'output':
            return
        function_attributes = []
        for j in range(len(self.sematic_stack) - 1, -1, -1):
            if isinstance(self.sematic_stack[j], list):
                function_attributes = self.sematic_stack[j]
        input_size = len(function_attributes) - 3

        for j in range(input_size):
            self.addToProgramBlock(self.state, 'ASSIGN', self.sematic_stack[len(
                self.sematic_stack) - input_size + j], function_attributes[j + 1])
            self.state = self.state + 1

        self.addToProgramBlock(
            self.state, 'ASSIGN', f'#{self.state + 2}', function_attributes[input_size + 1])
        self.state = self.state + 1

        self.addToProgramBlock(self.state, 'JP', function_attributes[0] + 1)
        self.state = self.state + 1
        for j in range(input_size + 1):
            self.sematic_stack.pop()

        address = self.getTempVar()
        self.sematic_stack.append(address)
        self.addToProgramBlock(
            self.state, 'ASSIGN', function_attributes[input_size + 2], address)
        self.state = self.state + 1

    def special_value(self):
        top = self.sematic_stack.pop()
        self.sematic_stack.append(self.state)
        self.sematic_stack.append(top)
        self.state += 1

    def special_save_pair(self):
        if self.symbol_table[len(self.symbol_table) - 1][0] == 'main':
            t = self.getTempVar()
            self.addToProgramBlock(
                self.sematic_stack.pop(), 'ADD', '#0', '#0', t)
            self.state += 1
        else:
            self.addToProgramBlock(self.sematic_stack.pop(), 'JP', self.state)

    def codeGenerator(self, actionSymbol, current_token: Token):
        if actionSymbol == '#pid':
            self.pid(current_token)

        elif actionSymbol == '#pnum':
            self.pnum(current_token)

        elif actionSymbol == '#mult':
            self.mult()

        elif actionSymbol == '#setvar':
            self.setVar()

        elif actionSymbol == '#setarr':
            self.setArr()

        elif actionSymbol == '#assign':
            self.assign()

        elif actionSymbol == '#indexing':
            self.index()

        elif actionSymbol == '#pop':
            self.pop()

        elif actionSymbol == '#savein':
            self.saveip(current_token)

        elif actionSymbol == '#opperation':
            self.operation()

        elif actionSymbol == '#signed':
            self.signed()

        elif actionSymbol == '#output':
            self.outputIn()

        elif actionSymbol == '#save':
            self.save()

        elif actionSymbol == '#jpf_save':
            self.jpfSave()

        elif actionSymbol == '#jpf_save_no_else':
            self.jpfSaveNoElse()

        elif actionSymbol == '#jp':
            self.jump()

        elif actionSymbol == '#label':
            self.lablel()

        elif actionSymbol == '#return':
            self.returnSymbol()

        elif actionSymbol == '#startreturn':
            self.start_return()

        elif actionSymbol == '#endreturn':
            self.end_return()

        elif actionSymbol == '#call':
            self.call_function()

        elif actionSymbol == '#function_save':
            self.special_value()

        elif actionSymbol == '#special_save':
            self.special_save_pair()

        elif actionSymbol == '#numeric_label':
            self.numericLabel()

        elif actionSymbol == '#repeat':
            self.repeat()

        elif actionSymbol == '#startBlock':
            self.start()

        elif actionSymbol == '#endBlock':
            self.end()

        elif actionSymbol == '#start_symbol':
            self.startSymbol()

        elif actionSymbol == '#add_symbol_table':
            self.add_function_to_symbol_table()

        elif actionSymbol == '#init_variable':
            self.init_variable()

        elif actionSymbol == '#return_address':
            self.return_address()

        elif actionSymbol == '#break':
            self.breakCode()

        elif actionSymbol == '#startbreak':
            self.start_break()

        elif actionSymbol == '#endbreak':
            self.endbreak()
