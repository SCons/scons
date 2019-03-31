import sys

if sys.platform == 'win32':
    args = sys.argv[1:]
    inf = None
    optstring = ''
    while args:
        a = args[0]
        if a == '-o':
            out = args[1]
            args = args[2:]
            continue
        args = args[1:]
        if not a[0] in '/-':
            if not inf:
                inf = a
            continue
        if a[:2] == '/c':
            continue
        if a[:3] == '/Fo':
            out = a[3:]
            continue
        optstring = optstring + ' ' + a
    with open(inf, 'rb') as ifp, open(out, 'wb') as ofp:
        ofp.write(bytearray(optstring + "\n",'utf-8'))
        for l in ifp.readlines():
            if l[:3] != b'#as':
                ofp.write(l)
    sys.exit(0)
else:
    import getopt
    opts, args = getopt.getopt(sys.argv[1:], 'co:x')
    optstring = ''

    for opt, arg in opts:
        if opt == '-o': out = arg
        else: optstring = optstring + ' ' + opt

    with open(args[0], 'rb') as ifp, open(out, 'wb') as ofp:
        ofp.write(bytearray(optstring + "\n",'utf-8'))
        for l in ifp.readlines():
            if l[:3] != b'#as':
                ofp.write(l)

    sys.exit(0)
