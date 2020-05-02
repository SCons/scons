#!/usr/bin/env python
#
# scons-diff.py - diff-like utility for comparing SCons trees
#
# This supports most common diff options (with some quirks, like you can't
# just say -c and have it use a default value), but canonicalizes the
# various version strings within the file like __revision__, __build__,
# etc. so that you can diff trees without having to ignore changes in
# version lines.
#
import difflib
import getopt
import os.path
import re
import sys

Usage = """\
Usage: scons-diff.py [OPTIONS] dir1 dir2
Options:
    -c NUM, --context=NUM       Print NUM lines of copied context.
    -h, --help                  Print this message and exit.
    -n                          Don't canonicalize SCons lines.
    -q, --quiet                 Print only whether files differ.
    -r, --recursive             Recursively compare found subdirectories.
    -s                          Report when two files are the same.
    -u NUM, --unified=NUM       Print NUM lines of unified context.
"""

opts, args = getopt.getopt(sys.argv[1:],
                           'c:dhnqrsu:',
                           ['context=', 'help', 'recursive', 'unified='])

diff_type = None
edit_type = None
context = 2
recursive = False
report_same = False
diff_options = []

def diff_line(left, right):
    if diff_options:
        opts = ' ' + ' '.join(diff_options)
    else:
        opts = ''
    print('diff%s %s %s' % (opts, left, right))

for o, a in opts:
    if o in ('-c', '-u'):
        diff_type = o
        context = int(a)
        diff_options.append(o)
    elif o in ('-h', '--help'):
        print(Usage)
        sys.exit(0)
    elif o == '-n':
        diff_options.append(o)
        edit_type = o
    elif o == '-q':
        diff_type = o
        diff_line = lambda l, r: None
    elif o in ('-r', '--recursive'):
        recursive = True
        diff_options.append(o)
    elif o == '-s':
        report_same = True

try:
    left, right = args
except ValueError:
    sys.stderr.write(Usage)
    sys.exit(1)

def quiet_diff(a, b, fromfile='', tofile='',
               fromfiledate='', tofiledate='', n=3, lineterm='\n'):
    """
    A function with the same calling signature as difflib.context_diff
    (diff -c) and difflib.unified_diff (diff -u) but which prints
    output like the simple, unadorned 'diff" command.
    """
    if a == b:
        return []
    else:
        return ['Files %s and %s differ\n' % (fromfile, tofile)]

def simple_diff(a, b, fromfile='', tofile='',
                fromfiledate='', tofiledate='', n=3, lineterm='\n'):
    """
    A function with the same calling signature as difflib.context_diff
    (diff -c) and difflib.unified_diff (diff -u) but which prints
    output like the simple, unadorned 'diff" command.
    """
    sm = difflib.SequenceMatcher(None, a, b)
    def comma(x1, x2):
        return x1+1 == x2 and str(x2) or '%s,%s' % (x1+1, x2)
    result = []
    for op, a1, a2, b1, b2 in sm.get_opcodes():
        if op == 'delete':
            result.append("%sd%d\n" % (comma(a1, a2), b1))
            result.extend(['< ' + l for l in a[a1:a2]])
        elif op == 'insert':
            result.append("%da%s\n" % (a1, comma(b1, b2)))
            result.extend(['> ' + l for l in b[b1:b2]])
        elif op == 'replace':
            result.append("%sc%s\n" % (comma(a1, a2), comma(b1, b2)))
            result.extend(['< ' + l for l in a[a1:a2]])
            result.append('---\n')
            result.extend(['> ' + l for l in b[b1:b2]])
    return result

diff_map = {
    '-c'        : difflib.context_diff,
    '-q'        : quiet_diff,
    '-u'        : difflib.unified_diff,
}

diff_function = diff_map.get(diff_type, simple_diff)

baseline_re = re.compile('(# |@REM )/home/\S+/baseline/')
comment_rev_re = re.compile('(# |@REM )(\S+) 0.96.[CD]\d+ \S+ \S+( knight)')
revision_re = re.compile('__revision__ = "[^"]*"')
build_re = re.compile('__build__ = "[^"]*"')
date_re = re.compile('__date__ = "[^"]*"')

def lines_read(file):
    return open(file).readlines()

def lines_massage(file):
    text = open(file).read()
    text = baseline_re.sub('\\1', text)
    text = comment_rev_re.sub('\\1\\2\\3', text)
    text = revision_re.sub('__revision__ = "__FILE__"', text)
    text = build_re.sub('__build__ = "0.96.92.DXXX"', text)
    text = date_re.sub('__date__ = "2006/08/25 02:59:00"', text)
    return text.splitlines(1)

lines_map = {
    '-n'        : lines_read,
}

lines_function = lines_map.get(edit_type, lines_massage)

def do_diff(left, right, diff_subdirs):
    if os.path.isfile(left) and os.path.isfile(right):
        diff_file(left, right)
    elif not os.path.isdir(left):
        diff_file(left, os.path.join(right, os.path.split(left)[1]))
    elif not os.path.isdir(right):
        diff_file(os.path.join(left, os.path.split(right)[1]), right)
    elif diff_subdirs:
        diff_dir(left, right)

def diff_file(left, right):
    l = lines_function(left)
    r = lines_function(right)
    d = diff_function(l, r, left, right, context)
    try:
        text = ''.join(d)
    except IndexError:
        sys.stderr.write('IndexError diffing %s and %s\n' % (left, right))
    else:
        if text:
            diff_line(left, right)
            print(text)
        elif report_same:
            print('Files %s and %s are identical' % (left, right))

def diff_dir(left, right):
    llist = os.listdir(left)
    rlist = os.listdir(right)
    u = {}
    for l in llist:
        u[l] = 1
    for r in rlist:
        u[r] = 1
    for x in sorted([ x for x in list(u.keys()) if x[-4:] != '.pyc' ]):
        if x in llist:
            if x in rlist:
                do_diff(os.path.join(left, x),
                        os.path.join(right, x),
                        recursive)
            else:
                print('Only in %s: %s' % (left, x))
        else:
            print('Only in %s: %s' % (right, x))

do_diff(left, right, True)

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
