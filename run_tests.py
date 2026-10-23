"""Run the compiler on every test in tests/ and report the result.

Checks that each program compiles and produces Endiamesos.int, Symbol.symb and Telikos.asm
in output/<test name>/.
To run the generated Telikos.asm, use RARS (see README.md).
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
COMPILER = os.path.join(ROOT, "cutePy_4723_4829.py")
TESTS = os.path.join(ROOT, "tests")

failed = 0
for name in sorted(os.listdir(TESTS)):
    if not name.endswith(".cpy"):
        continue
    result = subprocess.run([sys.executable, COMPILER, os.path.join(TESTS, name)],
                            capture_output=True, text=True)
    out_dir = os.path.join(ROOT, "output", os.path.splitext(name)[0])
    outputs = all(os.path.exists(os.path.join(out_dir, f)) and os.path.getsize(os.path.join(out_dir, f)) > 0
                  for f in ("Endiamesos.int", "Symbol.symb", "Telikos.asm"))
    ok = result.returncode == 0 and "Compilation Successfull" in result.stdout and outputs
    failed += not ok
    print("{:<12} {}".format(name, "OK" if ok else "FAILED"))
    if not ok:
        print(result.stdout[-500:])

sys.exit(1 if failed else 0)
