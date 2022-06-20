import getopt
import sys

comment = ('#' + sys.argv[1]).encode()

opts, args = getopt.getopt(sys.argv[2:], 'cf:o:xyz')
optstring = ''
length = len(comment)
for opt, arg in opts:
    if opt == '-o': out = arg
    elif opt not in ('-f', '-K'): optstring = optstring + ' ' + opt

with open(args[0], 'rb') as infile, open(out, 'wb') as outfile:
    outfile.write((optstring + "\n").encode())
    for l in infile:
        if not l.startswith(comment):
            outfile.write(l)

sys.exit(0)
