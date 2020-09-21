r"""
Phony "compiler" for testing SCons.

Copies its source files to the target file, dropping lines
that match a pattern, so we can recognize the tool
has made a modification.
"""

import sys

if __name__ == '__main__':
    line = ('/*' + sys.argv[1] + '*/\n').encode()
    with open(sys.argv[2], 'wb') as ofp:
        for f in sys.argv[3:]:
            with open(f, 'rb') as ifp:
                lines = [ln for ln in ifp if ln != line]
                for ln in lines:
                    ofp.write(ln)
    sys.exit(0)
