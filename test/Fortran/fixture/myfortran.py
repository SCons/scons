import getopt
import sys

print(sys.argv)
comment = ('#' + sys.argv[1]).encode()

opts, args = getopt.getopt(sys.argv[2:], 'cf:o:K:')
for opt, arg in opts:
    if opt == '-o':
        out = arg

with open(args[0], 'rb') as infile, open(out, 'wb') as outfile:
    for l in infile:
        if not l.startswith(comment):
            outfile.write(l)

sys.exit(0)
