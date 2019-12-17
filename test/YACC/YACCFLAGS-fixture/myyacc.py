import getopt
import sys
cmd_opts, args = getopt.getopt(sys.argv[1:], 'o:I:x', [])
opt_string = ''
i_arguments = ''
for opt, arg in cmd_opts:
    if opt == '-o': out = arg
    elif opt == '-I': i_arguments = i_arguments + ' ' + arg
    else: opt_string = opt_string + ' ' + opt
with open(out, 'wb') as ofp:
    for a in args:
        with open(a, 'rb') as ifp:
            contents = ifp.read()
        contents = contents.replace(b'YACCFLAGS', opt_string.encode())
        contents = contents.replace(b'I_ARGS', i_arguments.encode())
        ofp.write(contents)
sys.exit(0)
