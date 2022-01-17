"""
Phony compiler for testing SCons.

Copies its source files to the target file, dropping lines that match
a pattern, so we can recognize the tool has made a modification.
Intended for use as a *COM construction variable.

Calling convention is:
  argv[1] the function of the script (cc, c++, as, link etc.)
  argv[2] the output file to write
  argv[3:] one or more input files to "compile"

Invocation often looks like:
  Environment(CCCOM = r'%(_python_)s mycompile.py cc $TARGET $SOURCE', ...
"""

import fileinput
import sys

def fake_compile():
    skipline = f"/*{sys.argv[1]}*/\n".encode("utf-8")
    with open(sys.argv[2], 'wb') as ofp, fileinput.input(files=sys.argv[3:], mode='rb') as ifp:
        for line in ifp:
            if line != skipline:
                ofp.write(line)


if __name__ == '__main__':
    fake_compile()
    sys.exit(0)
