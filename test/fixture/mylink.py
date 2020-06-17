"""
Dummy linker for use by tests"
"""
import getopt
import sys

def fake_link():
    opts, args = getopt.getopt(sys.argv[1:], 'o:s:')
    for opt, arg in opts:
        if opt == '-o':
            out = arg

    with open(out, 'w') as ofp:
        for f in args:
            with open(f, 'r') as ifp:
                for line in ifp.readlines():
                    if line[:5] != '#link':
                        ofp.write(line)
    sys.exit(0)

def fake_win32_link():
    args = sys.argv[1:]
    while args:
        a = args[0]
        if a == '-o':
            out = args[1]
            args = args[2:]
            continue
        if not a[0] in '/-':
            break
        args = args[1:]
        if a[:5].lower() == '/out:': out = a[5:]
    with open(args[0], 'rb') as ifp, open(out, 'wb') as ofp:
        for line in ifp.readlines():
            if not line.startswith(b'#link'):
                ofp.write(line)
    sys.exit(0)

if __name__ == '__main__':
    if sys.platform == 'win32':
        fake_win32_link()
    else:
        fake_link()
