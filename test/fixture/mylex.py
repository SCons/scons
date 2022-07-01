"""
Phony lex for testing SCons.

Writes the contents of input file to stdout,
after "substituting" $LEXFLAGS and $I_ARGS

Needs to understand all the lex/flex options the testcases might use.
"""

import getopt
import sys
from pathlib import Path


def make_side_effect(path, text):
    p = Path(path)
    if str(p.parent) != '.':
        p.parent.mkdir(parents=True, exist_ok=True)
    with p.open(mode="wb") as f:
        f.write(text)


def fake_lex():
    make_header = None
    make_table = None

    if sys.platform == 'win32':
        longopts = ['nounistd']
    else:
        longopts = []
    longopts.extend(['header-file=', 'tables-file='])
    cmd_opts, args = getopt.getopt(sys.argv[1:], 'I:tx', longopts)
    opt_string = ''
    i_arguments = ''

    for opt, arg in cmd_opts:
        if opt == '-I':
            i_arguments = f'{i_arguments} {arg}'
        elif opt == '--header-file':
            make_header = arg
            opt_string = f'{opt_string} {opt}={arg}'
        elif opt == '--tables-file':
            make_table = arg
            opt_string = f'{opt_string} {opt}={arg}'
        else:
            opt_string = f'{opt_string} {opt}'

    for arg in args:
        with open(arg, 'rb') as ifp:
            contents = ifp.read().decode(encoding='utf-8')
        contents = contents.replace('LEXFLAGS', opt_string)
        contents = contents.replace('LEX', 'mylex.py')
        contents = contents.replace('I_ARGS', i_arguments)
        sys.stdout.write(contents)

    # Extra bits:
    if make_header:
        make_side_effect(make_header, b"lex header\n")
    if make_table:
        make_side_effect(make_table, b"lex table\n")


if __name__ == '__main__':
    fake_lex()
    sys.exit(0)
