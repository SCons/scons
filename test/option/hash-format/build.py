import sys
with open(sys.argv[1], 'wb') as f, open(sys.argv[2], 'rb') as infp:
    f.write(infp.read())