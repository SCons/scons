import fileinput
import sys

args = sys.argv[1:]
while args:
    arg = args[0]
    if arg == 'cf':
        out = args[1]
        args = args[1:]
    else:
        break
    args = args[1:]

with open(out, 'wb') as ofp, fileinput.input(files=args, mode='rb') as ifp:
    for line in ifp:
        if not line.startswith(b'/*jar*/'):
            ofp.write(line)

sys.exit(0)
