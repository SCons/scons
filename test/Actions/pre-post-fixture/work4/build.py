import sys
outfp = open(sys.argv[1], 'wb')
for f in sys.argv[2:]:
    outfp.write(open(f, 'rb').read())
outfp.close()
