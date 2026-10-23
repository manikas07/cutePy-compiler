# cutePy Compiler

A compiler for **cutePy**, a small Python-like teaching language, written in Python for the
*Compilers* (Μεταφραστές) course of the Department of Computer Science & Engineering,
University of Ioannina (2023).

**Authors:** Eleftherios Marios Manikas (4723), Stefanos Fotopoulos (4829)

## What it does

| Phase | Output |
|---|---|
| Lexical analysis | Token list with family and line number (printed to the terminal) |
| Syntax analysis | Recursive-descent parser with error messages that include the line |
| Intermediate code | Quadruples written to `Endiamesos.int` |
| Symbol table | Scopes, offsets, parameters, temporaries, framelength and starting quad, written to `Symbol.symb` |
| Semantic checks | Undeclared variables and functions, wrong number of arguments, duplicate declarations |
| Final code | RISC-V assembly written to `Telikos.asm`, runnable in [RARS](https://github.com/TheThirdOne/rars) |

## Usage

Requires Python 3.

```bash
python cutePy_4723_4829.py tests/test3.cpy
```

The output files are written to `output/<program name>/`, next to the compiler, so every program
keeps its own results:

```
output/test3/Endiamesos.int   intermediate code
output/test3/Symbol.symb      symbol table
output/test3/Telikos.asm      RISC-V final code
```

Run every test:

```bash
python run_tests.py
```

Run the generated RISC-V code in RARS (Java required):

```bash
java -jar rars1_6.jar nc output/test3/Telikos.asm
```

or open `output/test3/Telikos.asm` in the RARS GUI, assemble and run. `int(input())` reads an integer from the
console and `print` prints an integer followed by a new line.

## The cutePy language

```
def main_fibonacci():
#{
    #declare x
    def fibonacci(x):
    #{
        if (x<=1):
            return(x);
        else:
            return (fibonacci(x-1)+fibonacci(x-2));
    #}
    x = int(input());
    print(fibonacci(x));
#}
if __name__ == "__main__":
    main_fibonacci();
```

- Blocks are delimited with `#{ ... #}`; indentation has no meaning.
  An `if`/`else`/`while` without `#{ #}` takes exactly one statement.
- Variables are declared with `#declare a, b, c`.
- Comments go between `#$ ... #$`.
- Integers only, in the range `[-(2^32-1), 2^32-1]`; identifiers up to 30 characters.
- Operators: `+ - * //`, `< > <= >= == !=`, `and or not`. Conditions are grouped with `[ ]`.
- Functions can be nested and can use the variables of the functions that enclose them;
  parameters are passed by value.
- A variable must be declared and a function must be defined before it is used.
- `//` truncates toward zero (RISC-V `div`), so `-7 // 2` is `-3`.
- If the `if __name__ == "__main__":` part is missing, the main functions run in the order
  they are defined.

## Example intermediate code

For the `fibonacci` function above:

```
1: begin_block fibonacci _ _
2: <= x 1 4
3: jump _ _ 6
4: ret _ _ x
5: jump _ _ 16
6: - x 1 %1
7: par %1 cv _
8: par %2 ret _
9: call fibonacci _ _
10: - x 2 %3
11: par %3 cv _
12: par %4 ret _
13: call fibonacci _ _
14: + %2 %4 %5
15: ret _ _ %5
16: end_block fibonacci _ _
```

and the symbol table at the end of `fibonacci`:

```
Level: 1
[x/12/cv] <- [%1/16] <- [%2/20] <- [%3/24] <- [%4/28] <- [%5/32]
Level: 0
[x/12] <- [fibonacci/36/1]
```

## Final code

Every function gets an activation record on the stack; `sp` points to its start and the fields
are accessed with negative offsets:

| Offset | Content |
|---|---|
| 0 | return address |
| -4 | access link (frame of the enclosing function) |
| -8 | address where the return value is stored |
| -12 ... | parameters, local variables, temporaries |

Non-local variables are reached by following the access links. A call sets up the new frame
through `fp`, stores the parameters and the access link, moves `sp` and jumps with `jal`.
The call `fibonacci(x)` from `main_fibonacci` (test5):

```
L19:
    addi fp, sp, 36        # framelength of fibonacci
    lw t0, -12(sp)
    sw t0, -12(fp)         # parameter x (by value)
L20:
    addi t0, sp, -16
    sw t0, -8(fp)          # address of temporary %6, where the result goes
L21:
    sw sp, -4(fp)          # access link: fibonacci is nested in main_fibonacci
    addi sp, sp, 36
    jal L1
    addi sp, sp, -36
```

## Tests

| File | Covers | Input | Output in RARS |
|---|---|---|---|
| `tests/test1.cpy` | assignment, `if`, `print` | | `1` |
| `tests/test2.cpy` | `if`/`else`, `int(input())` | any | `1` |
| `tests/test3.cpy` | factorial, fibonacci, count digits, primes, `__main__` part | `5`, `10`, `12345` | `120 55 5 2 3 5 7 11 13 17 19 23 29` |
| `tests/test4.cpy` | primes with doubly nested functions | | `2 3 5 7 11 13 17 19 23 29` |
| `tests/test5.cpy` | recursive fibonacci | `10` | `55` |
| `tests/test6.cpy` | non-local variables through access links, `and`/`or`/`not`, negatives | | `5 7 217 -3 1 12 5` |

## Repository layout

```
cutePy_4723_4829.py   the compiler
run_tests.py          runs all tests
tests/                cutePy test programs
docs/                 test report submitted with the assignment (in Greek)
```

The report in `docs/` documents the original 2023 submission. Since then the compiler has been
fixed (if/else handling, expression results in `return`/`print`/parameters, `__main__` call
generation, backpatching of `and`/`or`/`not`, symbol table offsets and framelengths, lexer error
reporting) and the RISC-V final code generation (phase 3) has been completed.

## License

MIT, see [LICENSE](LICENSE).
