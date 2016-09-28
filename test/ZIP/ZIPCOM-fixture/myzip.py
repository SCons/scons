import sys
outfile = open(sys.argv[1], 'wb')
infile = open(sys.argv[2], 'rb')
for l in [l for l in infile.readlines() if l != b'/*zip*/\n']:
    outfile.write(l)
sys.exit(0)
