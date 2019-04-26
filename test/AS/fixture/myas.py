import sys

if sys.platform == 'win32':
    args = sys.argv[1:]
    inf = None
    while args:
        a = args[0]
        if a == '-o':
            out = args[1]
            args = args[2:]
            continue
        args = args[1:]
        if not a[0] in "/-":
            if not inf:
                inf = a
            continue
        if a[:3] == '/Fo': out = a[3:]
    with open(inf, 'rb') as ifp, open(out, 'wb') as ofp:
        for l in ifp.readlines():
            if l[:3] != b'#as':
                ofp.write(l)
    sys.exit(0)

else:
    import getopt
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'co:')
    except getopt.GetoptError:
        # we may be called with --version, just quit if so
        sys.exit(0)
    for opt, arg in opts:
        if opt == '-o': out = arg
    if args:
        with open(args[0], 'rb') as ifp, open(out, 'wb') as ofp:
            for l in ifp.readlines():
                if l[:3] != b'#as':
                    ofp.write(l)
    sys.exit(0)
