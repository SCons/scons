
import getopt
import os
import sys
compiler = sys.argv[1]
clen = len(compiler) + 1
opts, args = getopt.getopt(sys.argv[2:], 'co:xf:K:')
for opt, arg in opts:
    if opt == '-o': out = arg
    elif opt == '-x':
        with open('mygcc.out', 'a') as f:
            f.write(compiler + "\n")
with open(out, 'w') as ofp, open(args[0], 'r') as ifp:
    for l in ifp.readlines():
        if l[:clen] != '#' + compiler:
            ofp.write(l)
sys.exit(0)
