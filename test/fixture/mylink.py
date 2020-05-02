r"""
Phony "linker" for testing SCons.

Recognizes the option to specify an output file, ignoring
all others; copies input lines to the output file except
ones that contain a pattern, so we can recognize the tool
has made a modification.
"""

import sys

if __name__ == '__main__':
    if sys.platform == 'win32':
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
            for line in ifp:
                if not line.startswith(b'#link'):
                    ofp.write(line)
        sys.exit(0)
    else:
        import getopt
        opts, args = getopt.getopt(sys.argv[1:], 'o:')
        for opt, arg in opts:
            if opt == '-o': out = arg
        with open(args[0], 'rb') as ifp, open(out, 'wb') as ofp:
            for line in ifp:
                if not line.startswith(b'#link'):
                    ofp.write(line)
        sys.exit(0)
