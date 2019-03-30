r"""
Phony tool to modify a file in place for testing SCons.

Drops lines that match a pattern.  Currently used to test
ranlib-related behavior without invoking ranlib.
"""

import sys

if __name__ == '__main__':
    line = ('/*' + sys.argv[1] + '*/\n')
    with open(sys.argv[2], 'w') as ofp, open(sys.argv[2], 'r') as ifp:
        lines = [l for l in ifp.readlines() if l != line]
        for l in lines:
            ofp.write(l)
    sys.exit(0)
