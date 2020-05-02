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
import getopt
import sys

filenames = sys.argv[1:]

if not filenames:
    print("""Usage:  memlogs.py file [...]

Summarizes the --debug=memory numbers from one or more build logs.
""")
    sys.exit(0)

fmt = "%12s %12s %12s %12s    %s"

print(fmt % ("pre-read", "post-read", "pre-build", "post-build", ""))

for fname in sys.argv[1:]:
    lines = [l for l in open(fname).readlines() if l[:7] == 'Memory ']
    t = tuple([l.split()[-1] for l in lines]) + (fname,)
    print(fmt % t)

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
