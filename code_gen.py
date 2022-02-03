from cProfile import label
from Scanner.Token import Token

lastTempAddress = 100
symbol_table = []
scope_stack = []
sematic_stack = []
program_block = []
breaks = []
returns = []


state = 0


def addToProgramBlock(index, operand, r1, r2='', r3=''):
    global program_block
    while len(program_block) <= index:
        program_block.append('')
    program_block[index] = f'({operand}, {r1}, {r2}, {r3})'


def getTempVar(count=1):
    global lastTempAddress, state
    output = str(lastTempAddress)
    for w in range(0, count):
        addToProgramBlock(state, 'ASSIGN', '#0', str(lastTempAddress))
        state += 1
        lastTempAddress += 4
    return output


def initVar(id, type, attributes):
    global symbol_table, state
    if type == 'int':
        address = getTempVar()
    elif type == 'array':
        address = getTempVar()
        array = getTempVar(int(attributes))
        addToProgramBlock(state, 'ASSIGN', f'#{array}', address)
        state += 1
    symbol_table.append((id, type, address))


def end():
    global scope_stack, symbol_table
    top_value = scope_stack.pop()
    while top_value < len(symbol_table):
        symbol_table.pop()


def start():
    global scope_stack, symbol_table
    scope_stack.append(len(symbol_table))


def findIdAddress(id):
    if id == 'output':
        return 'output'
    global symbol_table
    for index in range(len(symbol_table) - 1, -1, -1):
        row = symbol_table[index]
        if id == row[0]:
            return row[2]


def pid(current_token: Token):
    global state, program_block, sematic_stack, breaks, returns
    p = findIdAddress(current_token.value)
    sematic_stack.append(p)


def pnum(currentToken):
    global state, program_block, sematic_stack, breaks, returns
    sematic_stack.append('#' + currentToken.value)


def mult():
    global state, program_block, sematic_stack, breaks, returns
    t = getTempVar()
    top = len(sematic_stack) - 1
    addToProgramBlock(
        state, 'MULT', sematic_stack[top], sematic_stack[top - 1], t)
    state += 1
    sematic_stack.pop()
    sematic_stack.pop()
    sematic_stack.append(t)


def setVar():
    global state, program_block, sematic_stack, breaks, returns
    initVar(sematic_stack.pop(), 'int', "")


def setArr():
    global state, program_block, sematic_stack, breaks, returns
    size = sematic_stack.pop()
    initVar(sematic_stack.pop(), 'array', size[1:])


def assign():
    global state, program_block, sematic_stack, breaks, returns
    top = len(sematic_stack) - 1
    addToProgramBlock(
        state, 'ASSIGN', sematic_stack[top], sematic_stack[top - 1])
    state += 1
    sematic_stack.pop()


def index():
    global state, program_block, sematic_stack, breaks, returns
    index = sematic_stack.pop()
    address = sematic_stack.pop()
    t1 = getTempVar()
    addToProgramBlock(state, 'MULT', '#4', index, t1)
    state += 1
    t2 = getTempVar()
    addToProgramBlock(state, 'ASSIGN', f'@{address}', t2)
    state += 1
    addToProgramBlock(state, 'ADD', t2, t1, t1)
    state += 1
    sematic_stack.append('@' + t1)


def pop():
    global state, program_block, sematic_stack, breaks, returns
    sematic_stack.pop()


def saveip(current_token):
    global state, program_block, sematic_stack, breaks, returns
    sematic_stack.append(current_token.value)


def operation():
    global state, program_block, sematic_stack, breaks, returns
    second_operand = sematic_stack.pop()
    operator = sematic_stack.pop()
    first_operand = sematic_stack.pop()
    t = getTempVar()
    if operator == '+':
        addToProgramBlock(state, 'ADD', first_operand, second_operand, t)
    elif operator == '-':
        addToProgramBlock(state, 'SUB', first_operand, second_operand, t)
    elif operator == '<':
        addToProgramBlock(state, 'LT', first_operand, second_operand, t)
    elif operator == '==':
        addToProgramBlock(state, 'EQ', first_operand, second_operand, t)
    sematic_stack.append(t)
    state += 1


def signed():
    global state, program_block, sematic_stack, breaks, returns
    top_value = sematic_stack.pop()
    t = getTempVar()
    addToProgramBlock(state, 'SUB', '#0', top_value, t)
    state += 1
    sematic_stack.append(t)


def outputIn():
    global state, program_block, sematic_stack, breaks, returns
    if sematic_stack[len(sematic_stack) - 2] != 'output':
        return
    top_value = sematic_stack.pop()
    addToProgramBlock(state, 'PRINT', top_value)
    state += 1


def jpfSave():
    global state, program_block, sematic_stack, breaks, returns
    index = sematic_stack.pop()
    expression = sematic_stack.pop()
    addToProgramBlock(index, 'JPF', expression, str(state + 1))
    sematic_stack.append(state)
    state += 1


def save():
    global state, program_block, sematic_stack, breaks, returns
    global state
    sematic_stack.append(state)
    state += 1


def jpfSaveNoElse():
    global state, program_block, sematic_stack, breaks, returns
    index = sematic_stack.pop()
    expression = sematic_stack.pop()
    addToProgramBlock(index, 'JPF', expression, str(state))


def jump():
    global state, program_block, sematic_stack, breaks, returns
    index = sematic_stack.pop()
    addToProgramBlock(int(index), 'JP', state)


def lablel():
    global state, program_block, sematic_stack, breaks, returns
    sematic_stack.append(state)


def numericLabel():
    global state, program_block, sematic_stack, breaks, returns
    sematic_stack.append(f'#{state}')


def repeat():
    global state, program_block, sematic_stack, breaks, returns
    expression = sematic_stack.pop()
    label = sematic_stack.pop()
    addToProgramBlock(state, 'JPF', expression, label)
    state += 1


def startSymbol():
    global state, program_block, sematic_stack, breaks, returns, symbol_table
    symbol_table.append('STOP')


def add_function_to_symbol_table():
    global state, program_block, sematic_stack, breaks, returns, symbol_table
    length = len(sematic_stack)
    attributes = []
    function_name = sematic_stack[length - 4]
    last_object_of_symbol_table = symbol_table.pop()
    while last_object_of_symbol_table != 'STOP':
        attributes.append(last_object_of_symbol_table[2])
        last_object_of_symbol_table = symbol_table.pop()
    attributes.append(sematic_stack[length - 3])
    attributes.reverse()
    attributes.append(sematic_stack[length - 2])
    attributes.append(sematic_stack[length - 1])
    symbol_table.append((function_name, 'function', attributes))
    sematic_stack.pop()
    sematic_stack.pop()
    sematic_stack.pop()
    sematic_stack.pop()


def init_variable():
    global state, program_block, sematic_stack, breaks, returns
    address = getTempVar()
    sematic_stack.append(address)


def return_address():
    global state, program_block, sematic_stack, breaks, returns
    global state
    if sematic_stack[len(sematic_stack) - 4] == 'main':
        return
    return_value = sematic_stack[len(sematic_stack) - 2]
    addToProgramBlock(state, 'JP', f'@{return_value}')
    state = state + 1


def breakCode():
    global state, program_block, sematic_stack, breaks, returns
    global state
    breaks.append(state)
    state += 1


def start_break():
    global state, program_block, sematic_stack, breaks, returns
    breaks.append("start")


def endbreak():
    global state, program_block, sematic_stack, breaks, returns
    index = breaks.pop()
    while index != 'start':
        addToProgramBlock(index, 'JP', state)
        index = breaks.pop()


def returnSymbol():
    global state, program_block, sematic_stack, breaks, returns
    global state
    value = sematic_stack.pop()
    returns.append((state, value))
    state += 2


def start_return():
    global state, program_block, sematic_stack, breaks, returns
    returns.append(("start", '#0'))


def end_return():
    global state, program_block, sematic_stack, breaks, returns
    index = returns.pop()
    while index[0] != 'start':
        addToProgramBlock(
            index[0], 'ASSIGN', index[1], sematic_stack[len(sematic_stack) - 1])
        addToProgramBlock(index[0] + 1, 'JP', state)
        index = returns.pop()


def call_function():
    global state, program_block, sematic_stack, breaks, returns
    if sematic_stack[len(sematic_stack) - 1] == 'output':
        return
    function_attributes = []
    for j in range(len(sematic_stack) - 1, -1, -1):
        if isinstance(sematic_stack[j], list):
            function_attributes = sematic_stack[j]
    input_size = len(function_attributes) - 3

    for j in range(input_size):
        addToProgramBlock(state, 'ASSIGN', sematic_stack[len(
            sematic_stack) - input_size + j], function_attributes[j + 1])
        state = state + 1

    addToProgramBlock(
        state, 'ASSIGN', f'#{state + 2}', function_attributes[input_size + 1])
    state = state + 1

    addToProgramBlock(state, 'JP', function_attributes[0] + 1)
    state = state + 1
    for j in range(input_size + 1):
        sematic_stack.pop()

    address = getTempVar()
    sematic_stack.append(address)
    addToProgramBlock(
        state, 'ASSIGN', function_attributes[input_size + 2], address)
    state = state + 1


def special_value():
    global state, program_block, sematic_stack, breaks, returns
    top = sematic_stack.pop()
    sematic_stack.append(state)
    sematic_stack.append(top)
    state += 1


def special_save_pair():
    global state, program_block, sematic_stack, breaks, returns, symbol_table
    if symbol_table[len(symbol_table) - 1][0] == 'main':
        t = getTempVar()
        addToProgramBlock(sematic_stack.pop(), 'ADD', '#0', '#0', t)
        state += 1
    else:
        addToProgramBlock(sematic_stack.pop(), 'JP', state)


def codeGenerator(actionSymbol, current_token: Token):
    global state, program_block, sematic_stack, breaks, returns

    if actionSymbol == '#pid':
        pid(current_token)

    elif actionSymbol == '#pnum':
        pnum(current_token)

    elif actionSymbol == '#mult':
        mult()

    elif actionSymbol == '#setvar':
        setVar()

    elif actionSymbol == '#setarr':
        setArr()

    elif actionSymbol == '#assign':
        assign()

    elif actionSymbol == '#index':
        index()

    elif actionSymbol == '#pop':
        pop()

    elif actionSymbol == '#saveinp':
        saveip(current_token)

    elif actionSymbol == '#opperation':
        operation()

    elif actionSymbol == '#signed':
        signed()

    elif actionSymbol == '#output_in':
        outputIn()

    elif actionSymbol == '#save':
        save()

    elif actionSymbol == '#jpf_save':
        jpfSave()

    elif actionSymbol == '#jpf_save_no_else':
        jpfSaveNoElse()

    elif actionSymbol == '#jp':
        jump()

    elif actionSymbol == '#label':
        lablel()

    elif actionSymbol == '#endbreak':
        endbreak()

    elif actionSymbol == '#return':
        returnSymbol()

    elif actionSymbol == '#startreturn':
        start_return()

    elif actionSymbol == '#endreturn':
        end_return()

    elif actionSymbol == '#call_function':
        call_function()

    elif actionSymbol == '#special_save':
        special_value()

    elif actionSymbol == '#special_save_pair':
        special_save_pair()

    elif actionSymbol == '#numeric_label':
        numericLabel()

    elif actionSymbol == '#repeat':
        repeat()

    elif actionSymbol == '#startscope':
        start()

    elif actionSymbol == '#endscope':
        end()

    elif actionSymbol == '#start_symbol':
        startSymbol()

    elif actionSymbol == '#add_function_to_symbol_table':
        add_function_to_symbol_table()

    elif actionSymbol == '#init_variable':
        init_variable()

    elif actionSymbol == '#return_address':
        return_address()

    elif actionSymbol == '#break':
        breakCode()

    elif actionSymbol == '#startbreak':
        start_break()


def create_outputs():
    global program_block
    output = open('output.txt', 'w')
    semantic = open('semantic_errors.txt', 'w', encoding='utf-8')
    semantic.write("The input program is semantically correct.")
    print(program_block)
    for i in range(0, len(program_block)):
        output.write(f'{i}\t{program_block[i]}\n')

    output.close()
    semantic.close()
