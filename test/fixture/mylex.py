"""
Phony lex for testing SCons.

Writes the contents of input file to stdout,
after "substituting" $LEXFLAGS and $I_ARGS

Intended for use as $LEX
"""

import getopt
import sys
import os

def fake_lex():
    if sys.platform == 'win32':
        longopts = ['nounistd']
    else:
        longopts = []
    cmd_opts, args = getopt.getopt(sys.argv[1:], 'I:tx', longopts)
    opt_string = ''
    i_arguments = ''
    for opt, arg in cmd_opts:
        if opt == '-I':
            i_arguments = f'{i_arguments} {arg}'
        else:
            opt_string = f'{opt_string} {opt}'
    for arg in args:
        with open(arg, 'rb') as ifp:
            contents = ifp.read().decode(encoding='utf-8')
        contents = contents.replace('LEXFLAGS', opt_string)
        contents = contents.replace('LEX', 'mylex.py')
        contents = contents.replace('I_ARGS', i_arguments)
        sys.stdout.write(contents)

if __name__ == '__main__':
    fake_lex()
    sys.exit(0)
