import sys
outfile = open(sys.argv[1], 'wb')
for f in sys.argv[2:]:
    infile = open(f, 'rb')
    for l in [l for l in infile.readlines() if l != b'/*zip*/\n']:
        outfile.write(l)
sys.exit(0)
