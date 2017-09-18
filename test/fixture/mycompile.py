import sys
line = ('/*' + sys.argv[1] + '*/\n').encode()
outfile = open(sys.argv[2], 'wb')
for f in sys.argv[3:]:
    infile = open(f, 'rb')
    for l in [l for l in infile.readlines() if l != line]:
        outfile.write(l)
sys.exit(0)
