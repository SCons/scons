r"""
Phony tool to modify a file in place for testing SCons.

Drops lines that match a pattern.  Currently used to test
ranlib and ar behavior without actually invoking those tools.
"""

import sys

def rewrite():
    line = ('/*' + sys.argv[1] + '*/\n').encode('utf-8')
    with open(sys.argv[2], 'rb') as ifp:
        lines = [ln for ln in ifp if ln != line]
    with open(sys.argv[2], 'wb') as ofp:
        ofp.writelines(lines)


if __name__ == '__main__':
    rewrite()
    sys.exit(0)
