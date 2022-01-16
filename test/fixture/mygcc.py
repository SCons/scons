import getopt
import sys

def fake_gcc():
    compiler = sys.argv[1].encode('utf-8')
    opts, args = getopt.getopt(sys.argv[2:], 'co:xf:K:')
    for opt, arg in opts:
        if opt == '-o':
            out = arg
        elif opt == '-x':
            with open('mygcc.out', 'ab') as f:
                f.write(compiler + b"\n")

    with open(out, 'wb') as ofp, open(args[0], 'rb') as ifp:
        for line in ifp:
            if not line.startswith(b'#' + compiler):
                ofp.write(line)

if __name__ == '__main__':
    fake_gcc()
    sys.exit(0)
