#!/usr/bin/env python
#
# __COPYRIGHT__
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
#

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons

python = TestSCons.python

test = TestSCons.TestSCons()

# Execute a subsidiary SConscript just to make sure we can
# get at the SCanners keyword from there.

test.write('SConstruct', """
SConscript('SConscript')
""")

test.write('SConscript', r"""
import re

include_re = re.compile(r'^include\s+(\S+)$', re.M)
exception_re = re.compile(r'^exception\s+(.+)$', re.M)

def kfile_scan(node, env, target, arg):
    contents = node.get_text_contents()
    exceptions = exception_re.findall(contents)
    if exceptions:
        raise Exception("kfile_scan error:  %s" % exceptions[0])
    includes = include_re.findall(contents)
    return includes

kscan = Scanner(name = 'kfile',
                function = kfile_scan,
                argument = None,
                recursive = 1,
                skeys = ['.k'])

def process(outf, inf):
    for line in inf.readlines():
        if line[:8] == 'include ':
            file = line[8:-1]
            with open(file, 'rb') as ifp:
                process(outf, ifp)
        else:
            outf.write(line)

def cat(env, source, target):
    target = str(target[0])
    with open(target, 'wb') as outf:
        for src in source:
            with open(str(src), 'rb') as inf:
                process(outf, inf)

env = Environment(BUILDERS={'Cat':Builder(action=cat)})
env.Append(SCANNERS = [kscan])

env.Cat('foo', 'foo.k')

bar_in = File('bar.in')
env.Cat('bar', bar_in)
""")

test.write('foo.k',
"""foo.k 1 line 1
include xxx
include yyy
foo.k 1 line 4
""")

test.write('bar.in',
"""include yyy
bar.in 1 line 2
bar.in 1 line 3
include zzz
""")

test.write('xxx', "xxx 1\n")

test.write('yyy', "exception yyy 1\n")

test.write('zzz', "zzz 1\n")

test.run(arguments = '.',
         status = 2,
         stderr = """\
scons: *** [foo] Exception : kfile_scan error:  yyy 1
""")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
