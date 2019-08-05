import getopt
import sys
cmd_opts, args = getopt.getopt(sys.argv[1:], 'o:', [])
opt_string = ''
for opt, arg in cmd_opts:
    if opt == '-o': out = arg
    else: opt_string = opt_string + ' ' + opt
with open(out, 'w') as ofp:
    for a in args:
        with open(a, 'r') as ifp:
            contents = ifp.read()
        ofp.write(contents.replace('YACC', 'myyacc.py'))
sys.exit(0)
