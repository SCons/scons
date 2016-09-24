import sys

if sys.platform == 'win32':
    args = sys.argv[1:]
    while args:
        a = args[0]
        if a == '-o':
            out = args[1]
            args = args[2:]
            continue
        if not a[0] in '/-':
            break
        args = args[1:]
        if a[:5].lower() == '/out:': out = a[5:]
    infile = open(args[0], 'rb')
    outfile = open(out, 'wb')
    for l in infile.readlines():
        if l[:5] != b'#link':
            outfile.write(l)
    sys.exit(0)
else:
    import getopt
    opts, args = getopt.getopt(sys.argv[1:], 'o:')
    for opt, arg in opts:
        if opt == '-o': out = arg
    infile = open(args[0], 'rb')
    outfile = open(out, 'wb')
    for l in infile.readlines():
        if l[:5] != b'#link':
            outfile.write(l)
    sys.exit(0)
