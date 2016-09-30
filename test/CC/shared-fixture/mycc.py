import sys
outfile = open(sys.argv[1], 'wb')
infile = open(sys.argv[2], 'rb')
for l in [l for l in infile.readlines() if l[:6] != b'/*cc*/']:
    outfile.write(l)
sys.exit(0)
