import getopt
import sys

opts, args = getopt.getopt(sys.argv[1:], 'o:s:')
for opt, arg in opts:
    if opt == '-o':
        out = arg

with open(out, 'w') as ofp:
    for f in args:
        with open(f, 'r') as ifp:
            for line in ifp.readlines():
                if line[:5] != '#link':
                    ofp.write(line)
sys.exit(0)
