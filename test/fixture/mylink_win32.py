import sys

args = sys.argv[1:]
while args:
    a = args[0]
    if a[0] != '/':
        break
    args.pop(0)
    if a[:5] == '/OUT:':
        out = a[5:]

with open(out, 'w') as ofp, open(args[0], 'r') as ifp:
    for line in ifp.readlines():
        if line[:5] != '#link':
            ofp.write(line)
sys.exit(0)
