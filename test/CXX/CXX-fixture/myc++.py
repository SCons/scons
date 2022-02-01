"""
Phony c++ command for testing SCons.

Copies its source file to the target file, dropping lines that match
a pattern, so we can recognize the tool has made a modification.
Intended for use as the $CXX construction variable.

Note: mycxx.py differs from the general fixture file mycompile.py
in arg handling: that one is intended for use as a *COM consvar,
where no compiler consvars will be passed on, this one is intended
for use as $CXX, where arguments like -o come into play.
"""
import getopt
import sys

def fake_win32_cxx():
    args = sys.argv[1:]
    inf = None
    while args:
        arg = args[0]
        if arg == '-o':
            out = args[1]
            args = args[2:]
            continue
        args = args[1:]
        if arg[0] not in '/-':
            if not inf:
                inf = arg
            continue
        if arg.startswith('/Fo'):
            out = arg[3:]

    with open(inf, 'rb') as infile, open(out, 'wb') as outfile:
        for line in infile:
            if not line.startswith(b'/*c++*/'):
                outfile.write(line)

def fake_cxx():
    opts, args = getopt.getopt(sys.argv[1:], 'co:')
    for opt, arg in opts:
        if opt == '-o':
            out = arg

    with open(args[0], 'rb') as infile, open(out, 'wb') as outfile:
        for line in infile:
            if not line.startswith(b'/*c++*/'):
                outfile.write(line)

if __name__ == '__main__':
    print(f"DEBUG: {sys.argv[0]}: {sys.argv[1:]}")
    if sys.platform == 'win32':
        fake_win32_cxx()
    else:
        fake_cxx()
    sys.exit(0)
