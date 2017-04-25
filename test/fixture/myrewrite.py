import sys
line = ('/*' + sys.argv[1] + '*/\n').encode()
lines = open(sys.argv[2], 'rb').readlines()
outfile = open(sys.argv[2], 'wb')
for l in [l for l in lines if l != line]:
    outfile.write(l)
sys.exit(0)
