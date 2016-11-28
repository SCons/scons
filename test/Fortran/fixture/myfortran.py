import getopt
import sys
print(sys.argv)
comment = ('#' + sys.argv[1]).encode()
length = len(comment)
opts, args = getopt.getopt(sys.argv[2:], 'cf:o:K:')
for opt, arg in opts:
    if opt == '-o': out = arg
infile = open(args[0], 'rb')
outfile = open(out, 'wb')
for l in infile.readlines():
    if l[:length] != comment:
        outfile.write(l)
sys.exit(0)
