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

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

attempt_file_names = [ 
    'File with spaces',
    'File"with"double"quotes',
    "File'with'single'quotes",
    "File\nwith\nnewlines",
    "File\\with\\backslashes",
    "File;with;semicolons",
    "File<with>redirect",
    "File|with|pipe",
    "File*with*asterisk",
    "File&with&ampersand",
    "File?with?question",
    "File\twith\ttab",
    "File$$with$$dollar",
    "Combination '\"\n\\;<>?|*\t&"
    ]

test.write("cat.py", """\
import sys
with open(sys.argv[1], 'wb') as f, open(sys.argv[2], 'rb') as ifp:
    f.write(ifp.read())
""")

file_names = []
for fn in attempt_file_names:
    try:
        in_name = fn.replace('$$', '$') + '.in'
        test.write(in_name, fn + '\n')
        file_names.append(fn)
    except IOError:
        # if the Python interpreter can't handle it, don't bother
        # testing to see if SCons can
        pass

def buildFileStr(fn):
    return "env.Build(source=r\"\"\"%s.in\"\"\", target=r\"\"\"%s.out\"\"\")" % ( fn, fn )

xxx = '\n'.join(map(buildFileStr, file_names))

test.write("SConstruct", """
env=Environment(BUILDERS = {'Build' : Builder(action = r'%(_python_)s cat.py $TARGET $SOURCE')})

%(xxx)s
""" % locals())

test.run(arguments='.')

for fn in file_names:
    out_name = fn.replace('$$', '$') + '.out'
    test.fail_test(test.read(out_name, mode='r') != fn + '\n')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
