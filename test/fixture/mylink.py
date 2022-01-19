"""
Phony linker for testing SCons.

Copies its source files to the target file, dropping lines that match
a pattern, so we can recognize the tool has made a modification.
Intended for use as the $LINK construction variable.
"""
import fileinput
import getopt
import sys

def fake_link():
    opts, args = getopt.getopt(sys.argv[1:], 'o:s:')
    for opt, arg in opts:
        if opt == '-o':
            out = arg

    with open(out, 'wb') as ofp, fileinput.input(files=args, mode='rb') as ifp:
        for line in ifp:
            if not line.startswith(b'#link'):
                ofp.write(line)

def fake_win32_link():
    args = sys.argv[1:]
    while args:
        arg = args[0]
        if arg == '-o':
            out = args[1]
            args = args[2:]
            continue
        if arg[0] not in '/-':
            break
        args = args[1:]
        if arg.lower().startswith('/out:'):
            out = arg[5:]
    with open(args[0], 'rb') as ifp, open(out, 'wb') as ofp:
        for line in ifp:
            if not line.startswith(b'#link'):
                ofp.write(line)

if __name__ == '__main__':
    if sys.platform == 'win32':
        fake_win32_link()
    else:
        fake_link()
    sys.exit(0)
