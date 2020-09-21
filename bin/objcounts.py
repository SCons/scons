#!/usr/bin/env python
#
# Copyright (c) 2005 The SCons Foundation
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
import re
import sys

filenames = sys.argv[1:]

if len(sys.argv) != 3:
    print("""Usage:  objcounts.py file1 file2

Compare the --debug=object counts from two build logs.
""")
    sys.exit(0)

def fetch_counts(fname):
    contents = open(fname).read()
    m = re.search('\nObject counts:(\n\s[^\n]*)*', contents, re.S)
    lines = m.group().split('\n')
    list = [l.split() for l in lines if re.match('\s+\d', l)]
    d = {}
    for l in list:
        d[l[-1]] = list(map(int, l[:-1]))
    return d

c1 = fetch_counts(sys.argv[1])
c2 = fetch_counts(sys.argv[2])

common = {}
for k in list(c1.keys()):
    try:
        common[k] = (c1[k], c2[k])
    except KeyError:
        # Transition:  we added the module to the names of a bunch of
        # the logged objects.  Assume that c1 might be from an older log
        # without the modules in the names, and look for an equivalent
        # in c2.
        if not '.' in k:
            s = '.'+k
            l = len(s)
            for k2 in list(c2.keys()):
                if k2[-l:] == s:
                    common[k2] = (c1[k], c2[k2])
                    del c1[k]
                    del c2[k2]
                    break
    else:
        del c1[k]
        del c2[k]

def diffstr(c1, c2):
    try:
        d = c2 - c1
    except TypeError:
        d = ''
    else:
        if d:
            d = '[%+d]' % d
        else:
            d = ''
    return " %5s/%-5s %-8s" % (c1, c2, d)

def printline(c1, c2, classname):
    print(diffstr(c1[2], c2[2]) + \
          diffstr(c1[3], c2[3]) + \
          ' ' + classname)

for k in sorted(common.keys()):
    c = common[k]
    printline(c[0], c[1], k)

for k in sorted(list(c1.keys())):
    printline(c1[k], ['--']*4, k)

for k in sorted(list(c2.keys())):
    printline(['--']*4, c2[k], k)

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
