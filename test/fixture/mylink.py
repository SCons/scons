import getopt
import sys

opts, args = getopt.getopt(sys.argv[1:], 'o:s:')
for opt, arg in opts:
    if opt == '-o':
        out = arg

with open(out, 'w') as ofp:
    for f in args:
        with open(f, 'r') as ifp:
            for l in ifp.readlines():
                if l[:5] != '#link':
                    ofp.write(l)
sys.exit(0)
