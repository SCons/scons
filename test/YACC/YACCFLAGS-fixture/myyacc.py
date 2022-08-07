import getopt
import sys
from pathlib import Path


def make_side_effect(path, text):
    p = Path(path)
    if str(p.parent) != '.':
        p.parent.mkdir(parents=True, exist_ok=True)
    with p.open(mode="wb") as f:
        f.write(text)


def fake_yacc():
    make_header = None
    make_graph = None

    longopts = ["defines=", "header=", "graph="]
    cmd_opts, args = getopt.getopt(sys.argv[1:], 'o:I:x', longopts)
    opt_string = ''
    i_arguments = ''

    for opt, arg in cmd_opts:
        if opt == '-o':
            out = arg
        elif opt == '-I':
            i_arguments = f'{i_arguments} {arg}'
        elif opt in ('--defines', '--header'):
            make_header = arg
            opt_string = f'{opt_string} {opt}={arg}'
        elif opt == '--graph':
            make_graph = arg
            opt_string = f'{opt_string} {opt}={arg}'
        else:
            opt_string = f'{opt_string} {opt}'

    with open(out, 'wb') as ofp:
        for a in args:
            with open(a, 'rb') as ifp:
                contents = ifp.read()
            contents = contents.replace(b'YACCFLAGS', opt_string.encode())
            contents = contents.replace(b'YACC', b'myyacc.py')
            contents = contents.replace(b'I_ARGS', i_arguments.encode())
            ofp.write(contents)

    # Extra bits:
    if make_header:
        make_side_effect(make_header, b"yacc header\n")
    if make_graph:
        make_side_effect(make_graph, b"yacc graph\n")


if __name__ == '__main__':
    fake_yacc()
    sys.exit(0)

# If -d is specified on the command line, yacc will emit a .h
# or .hpp file with the same name as the .c or .cpp output file.

# If -g is specified on the command line, yacc will emit a .vcg
# file with the same base name as the .y, .yacc, .ym or .yy file.

# If -v is specified yacc will create the output debug file
# which is not really source for any process, but should
# be noted and also be cleaned (issue #2558)
