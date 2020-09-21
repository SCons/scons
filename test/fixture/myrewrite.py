r"""
Phony tool to modify a file in place for testing SCons.

Drops lines that match a pattern.  Currently used to test
ranlib-related behavior without invoking ranlib.
"""

import sys

if __name__ == '__main__':
    line = ('/*' + sys.argv[1] + '*/\n').encode()
    with open(sys.argv[2], 'rb') as ifp:
        lines = [ln for ln in ifp if ln != line]
    with open(sys.argv[2], 'wb') as ofp:
        for ln in lines:
            ofp.write(ln)
    sys.exit(0)
