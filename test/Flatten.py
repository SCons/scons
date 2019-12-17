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

"""
Test that the Flatten() function is available and works.
"""

import TestSCons

test = TestSCons.TestSCons()

test.subdir('work')

test.write(['work', 'SConstruct'], """
def cat(env, source, target):
    target = str(target[0])
    with open(target, "wb") as ofp:
        for src in source:
            with open(str(src), "rb") as ifp:
                ofp.write(ifp.read())
env = Environment(BUILDERS={'Cat':Builder(action=cat)})
f1 = env.Cat('../file1.out', 'file1.in')
f2 = env.Cat('../file2.out', ['file2a.in', 'file2b.in'])
print(list(map(str, Flatten(['begin', f1, 'middle', f2, 'end']))))
print(list(map(str, env.Flatten([f1, [['a', 'b'], 'c'], f2]))))
SConscript('SConscript', "env")
""")

test.write(['work', 'SConscript'], """
Import("env")
print(Flatten([1, [2, 3], 4]))
print(env.Flatten([[[[1], 2], 3], 4]))
""")

test.write('file1.in', "file1.in\n")
test.write('file2a.in', "file2a.in\n")
test.write('file2b.in', "file2b.in\n")

def double_backslash(f):
    p = test.workpath(f)
    return p.replace('\\', '\\\\')

expect = """\
['begin', '%s', 'middle', '%s', 'end']
['%s', 'a', 'b', 'c', '%s']
[1, 2, 3, 4]
[1, 2, 3, 4]
""" % (double_backslash('file1.out'), double_backslash('file2.out'),
       double_backslash('file1.out'), double_backslash('file2.out'))

test.run(chdir = "work",
         arguments = ".",
         stdout = test.wrap_stdout(read_str = expect,
                                   build_str = "scons: `.' is up to date.\n"))

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
