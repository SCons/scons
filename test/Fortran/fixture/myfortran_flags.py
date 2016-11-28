import getopt
import sys
comment = ('#' + sys.argv[1]).encode()
opts, args = getopt.getopt(sys.argv[2:], 'cf:o:xy')
optstring = ''
length = len(comment)
for opt, arg in opts:
    if opt == '-o': out = arg
    elif opt not in ('-f', '-K'): optstring = optstring + ' ' + opt
infile = open(args[0], 'rb')
outfile = open(out, 'wb')
outfile.write((optstring + "\n").encode())
for l in infile.readlines():
    if l[:length] != comment:
        outfile.write(l)
sys.exit(0)
