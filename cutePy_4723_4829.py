# ELEFTHERIOS MARIOS MANIKAS AM:4723
# STEFANOS FOTOPOULOS AM:4829
#
# cutePy compiler: lexical analysis, syntax analysis,
# intermediate code (quads), symbol table and final code (RISC-V).
#
# Usage:  python cutePy_4723_4829.py <file.cpy>
# Output: output/<program>/ with Endiamesos.int (quads), Symbol.symb (symbol table)
#         and Telikos.asm (RISC-V), next to this script
import os
import sys

out_dir = '.'   # set in __main__: output/<program name>/

verbalUnits = []
listOfid = []
counter = 0
counter_line = 1
tk = ''
fam = ''
relOperators = ['<', '>', '!=', '<=', '>=', '==']
addOperators = ['+', '-']
mulOperators = ['*', '//']
assignment = ['=']
delimeter = [';', ':', ',', '"']
groupSymbols = ['[', ']', '(', ')', '#{', '#}']
keywords = ['False', 'None', 'True', 'and', 'as', 'program', 'break', 'class', 'continue', 'def', 'del',
            'elif', 'else', 'except', 'for', 'from', 'global', 'if', 'import', 'in', 'is', 'not', 'or', 'return',
            'while', '#declare', 'print', 'input', 'int']


# ----------------------------------------------------------------------------
# Lexical analysis
# ----------------------------------------------------------------------------

def start_compile():
    global verbalUnits, listOfid
    if len(sys.argv) < 2:
        print("Usage: python cutePy_4723_4829.py <file.cpy>")
        sys.exit(1)
    filePath = sys.argv[1]
    with open(filePath, "r") as file:
        content = file.read()
    listOfElements = list(content)
    n = len(listOfElements)
    pos_limit = (2 ** 32) - 1
    neg_limit = -((2 ** 32) - 1)

    def line_of(pos):
        return content.count('\n', 0, pos) + 1

    def lex_error(msg, pos):
        print(msg, 'line:', line_of(pos))
        sys.exit(1)

    k = 0
    while k < n:
        c = listOfElements[k]
        if c == ' ' or c == '\t' or c == '\r':
            k += 1
        elif c == '\n':
            verbalUnits.append(c)
            k += 1
        elif c in ',;:[]()+-*"':
            verbalUnits.append(c)
            k += 1
        elif c == '/':
            if k + 1 < n and listOfElements[k + 1] == '/':
                verbalUnits.append('//')
                k += 2
            else:
                lex_error("Expecting a second / to be a division", k)
        elif c in '<>=':
            if k + 1 < n and listOfElements[k + 1] == '=':
                verbalUnits.append(c + '=')
                k += 2
            else:
                verbalUnits.append(c)
                k += 1
        elif c == '!':
            if k + 1 < n and listOfElements[k + 1] == '=':
                verbalUnits.append('!=')
                k += 2
            else:
                lex_error("Expecting = after ! so as to have !=", k)
        elif c == '#':
            start = k
            k += 1
            if k >= n:
                lex_error("Expecting something after #", start)
            elif listOfElements[k] == '$':
                # comment: skip everything up to the closing #$
                k += 1
                while True:
                    if k + 1 >= n:
                        lex_error("Missing closing comment section with #$", start)
                    if listOfElements[k] == '#' and listOfElements[k + 1] == '$':
                        k += 2
                        break
                    k += 1
            elif listOfElements[k] == '{':
                verbalUnits.append('#{')
                k += 1
            elif listOfElements[k] == '}':
                verbalUnits.append('#}')
                k += 1
            elif ''.join(listOfElements[k:k + 7]) == 'declare' and \
                    not (k + 7 < n and (listOfElements[k + 7].isalnum() or listOfElements[k + 7] == '_')):
                verbalUnits.append('#declare')
                k += 7
            else:
                lex_error("Expecting $, {, } or declare after #", start)
        elif c.isalpha() or c == '_':
            word = c
            k += 1
            while k < n and (listOfElements[k].isalnum() or listOfElements[k] == '_'):
                word += listOfElements[k]
                k += 1
            if len(word) > 30:
                lex_error("The word has over 30 characters make it smaller", k)
            verbalUnits.append(word)
            listOfid.append(word)
        elif c.isdigit():
            word = c
            k += 1
            while k < n and listOfElements[k].isdigit():
                word += listOfElements[k]
                k += 1
            if k < n and (listOfElements[k].isalpha() or listOfElements[k] == '_'):
                lex_error("A number can not be followed by a letter", k)
            num = int(word)
            if not (neg_limit <= num <= pos_limit):
                lex_error("The number must be between [ -((2^32) -1) , (2^32) -1 ]", k)
            verbalUnits.append(word)
        else:
            lex_error("Illegal character {!r}".format(c), k)

    line = 1
    for i in verbalUnits:
        if i in keywords:
            print("{:<31} {:<31} {:<11}".format(i, "family:keyword", "line:{}".format(line)))
        elif i in relOperators:
            print("{:<31} {:<31} {:<11}".format(i, "family:relOperator", "line:{}".format(line)))
        elif i in addOperators:
            print("{:<31} {:<31} {:<11}".format(i, "family:addOperator", "line:{}".format(line)))
        elif i in mulOperators:
            print("{:<31} {:<31} {:<11}".format(i, "family:mulOperator", "line:{}".format(line)))
        elif i in delimeter:
            print("{:<31} {:<31} {:<11}".format(i, "family:delimiter", "line:{}".format(line)))
        elif i in assignment:
            print("{:<31} {:<31} {:<11}".format(i, "family:assignment", "line:{}".format(line)))
        elif i in groupSymbols:
            print("{:<31} {:<31} {:<11}".format(i, "family:groupSymbol", "line:{}".format(line)))
        elif i.isdigit():
            print("{:<31} {:<31} {:<11}".format(i, "family:number", "line:{}".format(line)))
        elif i == '\n':
            line += 1
        else:
            print("{:<31} {:<31} {:<11}".format(i, "family:id", "line:{}".format(line)))


def lex(j):
    if j > len(verbalUnits) - 1:
        return 'EOF', 'EOF'
    elif verbalUnits[j] in keywords:
        return verbalUnits[j], 'keywords'
    elif verbalUnits[j] in listOfid:
        return verbalUnits[j], 'id'
    elif verbalUnits[j] in relOperators:
        return verbalUnits[j], 'relOperators'
    elif verbalUnits[j] in addOperators:
        return verbalUnits[j], 'addOperators'
    elif verbalUnits[j] in mulOperators:
        return verbalUnits[j], 'mulOperators'
    elif verbalUnits[j] in assignment:
        return verbalUnits[j], 'assignment'
    elif verbalUnits[j] in delimeter:
        return verbalUnits[j], 'delimeter'
    elif verbalUnits[j] in groupSymbols:
        return verbalUnits[j], 'groupSymbols'
    elif verbalUnits[j] == '\n':
        return 'newLine', 'newLine'
    elif verbalUnits[j].isdigit():
        return verbalUnits[j], 'number'
    print("Unknown token", verbalUnits[j])
    sys.exit(1)


def lexer():
    # Returns the next token; new lines only advance the line counter.
    global counter, counter_line
    token, family = lex(counter)
    counter += 1
    while family == 'newLine':
        counter_line += 1
        token, family = lex(counter)
        counter += 1
    return token, family


# ----------------------------------------------------------------------------
# Intermediate code
# ----------------------------------------------------------------------------

quads = []
label_num = 1
counterTemp = 1


def genQuad(op, op1, op2, op3):
    global label_num
    quads.append([label_num, op, op1, op2, op3])
    label_num += 1


def nextQuad():
    return label_num


def newTemp():
    global counterTemp
    tmp = "%" + str(counterTemp)
    counterTemp += 1
    insert_entity(TemporaryVariable(tmp, "int", 0))
    return tmp


def emptyList():
    return []


def makeList(label):
    return [label]


def mergeList(list1, list2):
    return list1 + list2


def backpatch(lst, label):
    for q in lst:
        quads[q - 1][4] = label


def printEndiamesos():
    with open(os.path.join(out_dir, "Endiamesos.int"), "w") as file1:
        for q in quads:
            row = '{}: {} {} {} {}'.format(*q)
            print(row)
            file1.write(row + "\n")


# ----------------------------------------------------------------------------
# Symbol table
# ----------------------------------------------------------------------------

class Entity:
    def __init__(self, name):
        self.name = name


class Procedure(Entity):
    def __init__(self, name, startingQuad, framelength, formalParameters):
        super().__init__(name)
        self.startingQuad = startingQuad
        self.framelength = framelength
        self.formalParameters = formalParameters

    def update_fields(self, startingQuad, framelength):
        self.startingQuad = startingQuad
        self.framelength = framelength

    def add_standard_parameter(self, parameter):
        self.formalParameters.append(parameter)


class Function(Procedure):
    def __init__(self, name, datatype, startingQuad, framelength, formalParameters):
        super().__init__(name, startingQuad, framelength, formalParameters)
        self.datatype = datatype

    def __str__(self):
        return '[{}/{}/{}]'.format(self.name, self.framelength, self.startingQuad)


class FormalParameter(Entity):
    def __init__(self, name, datatype, mode):
        super().__init__(name)
        self.datatype = datatype
        self.mode = mode


class Variable(Entity):
    def __init__(self, name, datatype, offset):
        super().__init__(name)
        self.datatype = datatype
        self.offset = offset

    def __str__(self):
        return '[{}/{}]'.format(self.name, self.offset)


class Parameter(FormalParameter):
    def __init__(self, name, datatype, mode, offset):
        FormalParameter.__init__(self, name, datatype, mode)
        self.offset = offset

    def __str__(self):
        return '[{}/{}/{}]'.format(self.name, self.offset, self.mode)


class TemporaryVariable(Variable):
    pass


class Scope:
    def __init__(self, name, level):
        self.name = name
        self.level = level
        self.entities = []

    def next_offset(self):
        offsets = [e.offset for e in self.entities if hasattr(e, 'offset')]
        return max(offsets) + 4 if offsets else 12

    def framelength(self):
        return self.next_offset()


scopes = []          # scopes[i] is the scope with nesting level i
symbfile_name = "Symbol.symb"


def new_scope(name):
    scopes.append(Scope(name, len(scopes)))
    return scopes[-1]


def remove_scope():
    if not scopes:
        print("There no scope to delete")
        sys.exit(1)
    scopes.pop()


def insert_entity(entity):
    scope = scopes[-1]
    for e in scope.entities:
        if e.name == entity.name:
            print("Error:", entity.name, "is already declared in scope", scope.name, 'line:', counter_line)
            sys.exit(1)
    if hasattr(entity, 'offset'):
        entity.offset = scope.next_offset()
    scope.entities.append(entity)


def search(name):
    # Returns (entity, nesting level of the scope it belongs to) or (None, None)
    for scope in reversed(scopes):
        for e in scope.entities:
            if e.name == name:
                return e, scope.level
    return None, None


def check_variable(name):
    entity, _ = search(name)
    if entity is None or not hasattr(entity, 'offset'):
        print("Error:", name, "is not a declared variable", 'line:', counter_line)
        sys.exit(1)


def check_function(name, num_params):
    entity, _ = search(name)
    if not isinstance(entity, Function):
        print("Error:", name, "is not a declared function", 'line:', counter_line)
        sys.exit(1)
    if len(entity.formalParameters) != num_params:
        print("Error:", name, "expects", len(entity.formalParameters), "parameters but got",
              num_params, 'line:', counter_line)
        sys.exit(1)


def print_symbol_table(header):
    lines = ["Current Scope: " + header]
    for scope in reversed(scopes):
        lines.append("Level: {}".format(scope.level))
        lines.append(" <- ".join(str(e) for e in scope.entities))
    text = "\n".join(lines) + "\n\n"
    print(text)
    with open(os.path.join(out_dir, symbfile_name), "a") as symbfile:
        symbfile.write(text)


# ----------------------------------------------------------------------------
# Final code (RISC-V)
#
# Activation record (sp points to its start, fields at -offset(sp)):
#    0: return address   4: access link   8: address of the return value
#   12...: parameters, local variables, temporaries
# ----------------------------------------------------------------------------

asm = []
asm_main_label = None
branch_ops = {'==': 'beq', '!=': 'bne', '<': 'blt', '>': 'bgt', '<=': 'ble', '>=': 'bge'}
arith_ops = {'+': 'add', '-': 'sub', '*': 'mul', '//': 'div'}


def emit(line):
    asm.append(line if line.endswith(':') else '    ' + line)


def current_level():
    return len(scopes) - 1      # -1 inside the __main__ part


def is_number(v):
    return v.lstrip('-').isdigit()


def gnvlcode(v):
    # t0 <- address of a non-local variable, following the access links
    entity, lvl = search(v)
    emit('lw t0, -4(sp)')
    for _ in range(current_level() - lvl - 1):
        emit('lw t0, -4(t0)')
    emit('addi t0, t0, -{}'.format(entity.offset))


def loadvr(v, reg):
    if is_number(v):
        emit('li {}, {}'.format(reg, v))
        return
    entity, lvl = search(v)
    if lvl == current_level():
        emit('lw {}, -{}(sp)'.format(reg, entity.offset))
    else:
        gnvlcode(v)
        emit('lw {}, 0(t0)'.format(reg))


def storerv(reg, v):
    entity, lvl = search(v)
    if lvl == current_level():
        emit('sw {}, -{}(sp)'.format(reg, entity.offset))
    else:
        gnvlcode(v)
        emit('sw {}, 0(t0)'.format(reg))


def callee_info(name):
    # (starting quad, framelength, nesting level of the callee's own scope)
    if name in main_functions:
        return main_functions[name][0], main_functions[name][1], 0
    entity, lvl = search(name)
    return entity.startingQuad, entity.framelength, lvl + 1


def generate_final(startQuad, is_main_function=False):
    # Translates the quads of one block, while its scope is still alive.
    call = None
    for q in quads[startQuad - 1:]:
        label, op, x, y, z = q
        emit('L{}:'.format(label))
        if op == 'begin_block':
            if x == '__main__':
                emit('addi sp, sp, 12')
                emit('mv gp, sp')
            else:
                emit('sw ra, 0(sp)')
        elif op == 'end_block':
            if x != '__main__':
                emit('lw ra, 0(sp)')
                emit('jr ra')
            break
        elif op == 'halt':
            emit('li a0, 0')
            emit('li a7, 10')
            emit('ecall')
        elif op == 'jump':
            emit('j L{}'.format(z))
        elif op in branch_ops:
            loadvr(x, 't1')
            loadvr(y, 't2')
            emit('{} t1, t2, L{}'.format(branch_ops[op], z))
        elif op == '=':
            loadvr(x, 't1')
            storerv('t1', z)
        elif op in arith_ops:
            loadvr(x, 't1')
            loadvr(y, 't2')
            emit('{} t1, t1, t2'.format(arith_ops[op]))
            storerv('t1', z)
        elif op == 'in':
            emit('li a7, 5')
            emit('ecall')
            storerv('a0', x)
        elif op == 'out':
            loadvr(x, 'a0')
            emit('li a7, 1')
            emit('ecall')
            emit('la a0, str_nl')
            emit('li a7, 4')
            emit('ecall')
        elif op == 'ret':
            if not is_main_function:
                loadvr(z, 't1')
                emit('lw t0, -8(sp)')
                emit('sw t1, 0(t0)')
            emit('lw ra, 0(sp)')
            emit('jr ra')
        elif op in ('par', 'call'):
            if call is None:
                name = x if op == 'call' else next(c[2] for c in quads[label - 1:] if c[1] == 'call')
                start, framelength, level_callee = callee_info(name)
                call = {'start': start, 'framelength': framelength, 'level': level_callee, 'i': 0}
                emit('addi fp, sp, {}'.format(framelength))
            if op == 'par' and y == 'cv':
                loadvr(x, 't0')
                emit('sw t0, -{}(fp)'.format(12 + 4 * call['i']))
                call['i'] += 1
            elif op == 'par' and y == 'ret':
                entity, _ = search(x)
                emit('addi t0, sp, -{}'.format(entity.offset))
                emit('sw t0, -8(fp)')
            elif op == 'call':
                # access link: the frame of the callee's parent
                hops = current_level() - (call['level'] - 1)
                if hops == 0:
                    emit('sw sp, -4(fp)')
                else:
                    emit('lw t0, -4(sp)')
                    for _ in range(hops - 1):
                        emit('lw t0, -4(t0)')
                    emit('sw t0, -4(fp)')
                emit('addi sp, sp, {}'.format(call['framelength']))
                emit('jal L{}'.format(call['start']))
                emit('addi sp, sp, -{}'.format(call['framelength']))
                call = None


def printTelikos():
    with open(os.path.join(out_dir, "Telikos.asm"), "w") as f:
        f.write('.data\nstr_nl: .asciz "\\n"\n.text\nL0:\n    j Lmain\n')
        for line in asm:
            if line == 'L{}:'.format(asm_main_label):
                f.write('Lmain:\n')
            f.write(line + '\n')


# ----------------------------------------------------------------------------
# Syntax analysis
# ----------------------------------------------------------------------------

main_functions = {}   # name -> (starting quad, framelength)


def error(expected):
    print('Error Perimena', expected, 'kai vrika', tk, 'line:', counter_line)
    sys.exit(1)


def expect(symbol):
    global tk, fam
    if tk == symbol and fam != 'EOF' and fam != 'id':
        tk, fam = lexer()
    else:
        error(symbol)


def expect_id():
    global tk, fam
    if fam != 'id':
        error('Family id')
    name = tk
    tk, fam = lexer()
    return name


def starts_statement():
    return fam == 'id' or tk in ('print', 'return', 'if', 'while')


def syntax():
    start_Rule()


def start_Rule():
    global tk, fam
    tk, fam = lexer()
    main_part()
    if tk == 'if':
        call_main_part()
    elif fam == 'EOF':
        # no 'if __name__ == "__main__":' part: call every main function in order
        print("No __main__ part: the main functions are called in the order they are defined")
        main_program(list(main_functions))
    if fam != 'EOF':
        error('def || if __name__ || EOF')
    print("Compilation Successfull")


def main_part():
    if tk != 'def':
        error('def')
    while tk == 'def':
        main_function()


def main_function():
    expect('def')
    functionName = expect_id()
    if functionName in main_functions:
        print("Error: main function", functionName, "is already defined", 'line:', counter_line)
        sys.exit(1)
    expect('(')
    expect(')')
    expect(':')
    expect('#{')
    new_scope(functionName)
    declarations()
    while tk == 'def':
        function()
    startQuad = nextQuad()
    genQuad("begin_block", functionName, "_", "_")
    statements()
    expect('#}')
    genQuad("end_block", functionName, "_", "_")
    main_functions[functionName] = (startQuad, scopes[-1].framelength())
    print_symbol_table("{} (framelength {}, startQuad {})".format(
        functionName, scopes[-1].framelength(), startQuad))
    generate_final(startQuad, is_main_function=True)
    remove_scope()


def function():
    expect('def')
    functionName = expect_id()
    func = Function(functionName, "int", 0, 0, [])
    insert_entity(func)
    new_scope(functionName)
    expect('(')
    for par in id_list():
        func.add_standard_parameter(FormalParameter(par, "int", "cv"))
        insert_entity(Parameter(par, "int", "cv", 0))
    expect(')')
    expect(':')
    expect('#{')
    declarations()
    while tk == 'def':
        function()
    startQuad = nextQuad()
    genQuad("begin_block", functionName, "_", "_")
    statements()
    expect('#}')
    genQuad("end_block", functionName, "_", "_")
    func.update_fields(startQuad, scopes[-1].framelength())
    print_symbol_table(functionName)
    generate_final(startQuad)
    remove_scope()


def declarations():
    while tk == '#declare':
        declaration_line()


def declaration_line():
    expect('#declare')
    for name in id_list():
        insert_entity(Variable(name, "int", 0))


def id_list():
    global tk, fam
    names = []
    if fam == 'id':
        names.append(expect_id())
        while tk == ',':
            tk, fam = lexer()
            names.append(expect_id())
    return names


def statements():
    if not starts_statement():
        error('id || print || return || if || while')
    while starts_statement():
        statement()


def statement():
    if fam == 'id' or tk == 'print' or tk == 'return':
        simple_statement()
    elif tk == 'if' or tk == 'while':
        structured_statement()
    else:
        error('id || print || return || if || while')


def block():
    # statement | #{ statements #}
    global tk, fam
    if tk == '#{':
        tk, fam = lexer()
        statements()
        expect('#}')
    else:
        statement()


def simple_statement():
    if fam == 'id':
        assignment_stat()
    elif tk == 'print':
        print_stat()
    elif tk == 'return':
        return_stat()
    else:
        error('id || print || return')


def structured_statement():
    if tk == 'if':
        if_stat()
    elif tk == 'while':
        while_stat()
    else:
        error('if || while')


def assignment_stat():
    check_variable(tk)
    id1 = expect_id()
    expect('=')
    if tk == 'int':
        expect('int')
        expect('(')
        expect('input')
        expect('(')
        expect(')')
        expect(')')
        expect(';')
        genQuad('in', id1, '_', '_')
    else:
        E_place = expression()
        expect(';')
        genQuad('=', E_place, '_', id1)


def print_stat():
    expect('print')
    expect('(')
    E_place = expression()
    expect(')')
    expect(';')
    genQuad('out', E_place, '_', '_')


def return_stat():
    expect('return')
    expect('(')
    E_place = expression()
    expect(')')
    expect(';')
    genQuad('ret', '_', '_', E_place)


def if_stat():
    global tk, fam
    expect('if')
    expect('(')
    condition_true, condition_false = condition()
    expect(')')
    expect(':')
    backpatch(condition_true, nextQuad())
    block()
    ifList = makeList(nextQuad())
    genQuad('jump', '_', '_', '_')
    backpatch(condition_false, nextQuad())
    if tk == 'else':
        tk, fam = lexer()
        expect(':')
        block()
    backpatch(ifList, nextQuad())


def while_stat():
    expect('while')
    condQuad = nextQuad()
    expect('(')
    condition_true, condition_false = condition()
    expect(')')
    expect(':')
    backpatch(condition_true, nextQuad())
    block()
    genQuad('jump', '_', '_', condQuad)
    backpatch(condition_false, nextQuad())


def condition():
    global tk, fam
    B_true, B_false = bool_term()
    while tk == 'or':
        backpatch(B_false, nextQuad())
        tk, fam = lexer()
        Q2_true, Q2_false = bool_term()
        B_true = mergeList(B_true, Q2_true)
        B_false = Q2_false
    return B_true, B_false


def bool_term():
    global tk, fam
    Q_true, Q_false = bool_factor()
    while tk == 'and':
        backpatch(Q_true, nextQuad())
        tk, fam = lexer()
        R2_true, R2_false = bool_factor()
        Q_false = mergeList(Q_false, R2_false)
        Q_true = R2_true
    return Q_true, Q_false


def bool_factor():
    global tk, fam
    if tk == 'not':
        tk, fam = lexer()
        expect('[')
        B_true, B_false = condition()
        expect(']')
        return B_false, B_true
    if tk == '[':
        tk, fam = lexer()
        B_true, B_false = condition()
        expect(']')
        return B_true, B_false
    E1_place = expression()
    if fam != 'relOperators':
        error('Family relOperators')
    rel_op = tk
    tk, fam = lexer()
    E2_place = expression()
    R_true = makeList(nextQuad())
    genQuad(rel_op, E1_place, E2_place, '_')
    R_false = makeList(nextQuad())
    genQuad('jump', '_', '_', '_')
    return R_true, R_false


def expression():
    sign = optional_sign()
    T1_place = term()
    if sign == '-':
        w = newTemp()
        genQuad('-', '0', T1_place, w)
        T1_place = w
    while fam == 'addOperators':
        tkOper = ADD_OP()
        T2_place = term()
        w = newTemp()
        genQuad(tkOper, T1_place, T2_place, w)
        T1_place = w
    return T1_place


def term():
    F1_place = factor()
    while fam == 'mulOperators':
        tkOper = MUL_OP()
        F2_place = factor()
        w = newTemp()
        genQuad(tkOper, F1_place, F2_place, w)
        F1_place = w
    return F1_place


def factor():
    global tk, fam
    if fam == 'number':
        F_place = tk
        tk, fam = lexer()
        return F_place
    elif tk == '(':
        tk, fam = lexer()
        E_place = expression()
        expect(')')
        return E_place
    elif fam == 'id':
        name = expect_id()
        if tk == '(':
            return id_tail(name)
        check_variable(name)
        return name
    error('number || ( || id')


def id_tail(name):
    global tk, fam
    expect('(')
    params = actual_par_list()
    expect(')')
    check_function(name, len(params))
    for p in params:
        genQuad("par", p, "cv", "_")
    w = newTemp()
    genQuad("par", w, "ret", "_")
    genQuad("call", name, "_", "_")
    return w


def actual_par_list():
    global tk, fam
    params = []
    if tk == ')':
        return params
    params.append(expression())
    while tk == ',':
        tk, fam = lexer()
        params.append(expression())
    return params


def optional_sign():
    return ADD_OP()


def call_main_part():
    expect('if')
    if tk != '__name__':
        error('__name__')
    expect_id()
    expect('==')
    expect('"')
    if tk != '__main__':
        error('__main__')
    expect_id()
    expect('"')
    expect(':')
    calls = [main_function_call()]
    while fam == 'id':
        calls.append(main_function_call())
    main_program(calls)


def main_function_call():
    name = expect_id()
    if name not in main_functions:
        print("Error:", name, "is not a main function", 'line:', counter_line)
        sys.exit(1)
    expect('(')
    expect(')')
    expect(';')
    return name


def main_program(calls):
    global asm_main_label
    asm_main_label = nextQuad()
    genQuad("begin_block", "__main__", "_", "_")
    for name in calls:
        genQuad("call", name, "_", "_")
    genQuad('halt', '_', '_', '_')
    genQuad("end_block", "__main__", "_", "_")
    generate_final(asm_main_label)


def ADD_OP():
    global tk, fam
    if fam == 'addOperators':
        oper = tk
        tk, fam = lexer()
        return oper
    return None


def MUL_OP():
    global tk, fam
    if fam == 'mulOperators':
        oper = tk
        tk, fam = lexer()
        return oper
    return None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python cutePy_4723_4829.py <file.cpy>")
        sys.exit(1)
    program = os.path.splitext(os.path.basename(sys.argv[1]))[0]
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", program)
    os.makedirs(out_dir, exist_ok=True)
    open(os.path.join(out_dir, symbfile_name), "w").close()
    start_compile()
    print("End of Verbal Analysis")
    syntax()
    printEndiamesos()
    printTelikos()
    print("Output files written to", out_dir)
