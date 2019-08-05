import sys
with open(sys.argv[1], 'wb') as outfp:
    for f in sys.argv[2:]:
        with open(f, 'rb') as infp:
            outfp.write(infp.read())
