import getopt
import sys
cmd_opts, args = getopt.getopt(sys.argv[1:], 'o:I:x', [])
output = None
opt_string = ''
i_arguments = ''
for opt, arg in cmd_opts:
    if opt == '-o': output = open(arg, 'wb')
    elif opt == '-I': i_arguments = i_arguments + ' ' + arg
    else: opt_string = opt_string + ' ' + opt
for a in args:
    contents = open(a, 'rb').read()
    contents = contents.replace(b'YACCFLAGS', opt_string.encode())
    contents = contents.replace(b'I_ARGS', i_arguments.encode())
    output.write(contents)
output.close()
sys.exit(0)
