import getopt
import sys
cmd_opts, args = getopt.getopt(sys.argv[1:], 'o:', [])
output = None
opt_string = ''
for opt, arg in cmd_opts:
    if opt == '-o': output = open(arg, 'w')
    else: opt_string = opt_string + ' ' + opt
for a in args:
    contents = open(a, 'r').read()
    output.write(contents.replace('YACC', 'myyacc.py'))
output.close()
sys.exit(0)
