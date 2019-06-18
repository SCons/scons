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
Verify that the Copy() Action works, and preserves file modification
times and modes.
"""

import os
import stat
import sys

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """
Execute(Copy('f1.out', 'f1.in'))
Execute(Copy(File('d2.out'), 'd2.in'))
Execute(Copy('d3.out', File('f3.in')))
def cat(env, source, target):
    target = str(target[0])
    with open(target, "w") as f:
        for src in source:
            with open(str(src), "r") as ifp:
                f.write(ifp.read())
Cat = Action(cat)
env = Environment()
env.Command('bar.out', 'bar.in', [Cat,
                                  Copy("f4.out", "f4.in"),
                                  Copy("d5.out", "d5.in"),
                                  Copy("d6.out", "f6.in")])
env = Environment(OUTPUT = 'f7.out', INPUT = 'f7.in')
env.Command('f8.out', 'f8.in', [Copy('$OUTPUT', '$INPUT'), Cat])
env.Command('f9.out', 'f9.in', [Cat, Copy('${TARGET}-Copy', '$SOURCE')])

env.CopyTo( 'd4', 'f10.in' )
env.CopyAs( 'd4/f11.out', 'f11.in')
env.CopyAs( 'd4/f12.out', 'd5/f12.in')

env.Command('f   13.out', 'f   13.in', Copy('$TARGET', '$SOURCE'))
""")

test.write('f1.in', "f1.in\n")
test.subdir('d2.in')
test.write(['d2.in', 'file'], "d2.in/file\n")
test.write('f3.in', "f3.in\n")
test.subdir('d3.out')
test.write('bar.in', "bar.in\n")
test.write('f4.in', "f4.in\n")
test.subdir('d5.in')
test.write(['d5.in', 'file'], "d5.in/file\n")
test.write('f6.in', "f6.in\n")
test.subdir('d6.out')
test.write('f7.in', "f7.in\n")
test.write('f8.in', "f8.in\n")
test.write('f9.in', "f9.in\n")
test.write('f10.in', "f10.in\n")
test.write('f11.in', "f11.in\n")
test.subdir('d5')
test.write(['d5', 'f12.in'], "f12.in\n")
test.write('f   13.in', "f   13.in\n")

os.chmod('f1.in', 0o646)
os.chmod('f4.in', 0o644)

test.sleep()

d4_f10_in   = os.path.join('d4', 'f10.in')
d4_f11_out  = os.path.join('d4', 'f11.out')
d4_f12_out  = os.path.join('d4', 'f12.out')
d5_f12_in   = os.path.join('d5', 'f12.in')

expect = test.wrap_stdout(read_str = """\
Copy("f1.out", "f1.in")
Copy("d2.out", "d2.in")
Copy("d3.out", "f3.in")
""",
                          build_str = """\
cat(["bar.out"], ["bar.in"])
Copy("f4.out", "f4.in")
Copy("d5.out", "d5.in")
Copy("d6.out", "f6.in")
Copy file(s): "f10.in" to "%(d4_f10_in)s"
Copy file(s): "f11.in" to "%(d4_f11_out)s"
Copy file(s): "%(d5_f12_in)s" to "%(d4_f12_out)s"
Copy("f   13.out", "f   13.in")
Copy("f7.out", "f7.in")
cat(["f8.out"], ["f8.in"])
cat(["f9.out"], ["f9.in"])
Copy("f9.out-Copy", "f9.in")
""" % locals())

test.run(options = '-n', arguments = '.', stdout = expect)

test.must_not_exist('f1.out')
test.must_not_exist('d2.out')
test.must_not_exist(os.path.join('d3.out', 'f3.in'))
test.must_not_exist('f4.out')
test.must_not_exist('d5.out')
test.must_not_exist(os.path.join('d6.out', 'f6.in'))
test.must_not_exist('f7.out')
test.must_not_exist('f8.out')
test.must_not_exist('f9.out')
test.must_not_exist('f9.out-Copy')
test.must_not_exist('d4/f10.in')
test.must_not_exist('d4/f11.out')
test.must_not_exist('d4/f12.out')
test.must_not_exist('f 13.out')
test.must_not_exist('f    13.out')

test.run()

test.must_match('f1.out', "f1.in\n", mode='r')
test.must_match(['d2.out', 'file'], "d2.in/file\n", mode='r')
test.must_match(['d3.out', 'f3.in'], "f3.in\n", mode='r')
test.must_match('f4.out', "f4.in\n", mode='r')
test.must_match(['d5.out', 'file'], "d5.in/file\n", mode='r')
test.must_match(['d6.out', 'f6.in'], "f6.in\n", mode='r')
test.must_match('f7.out', "f7.in\n", mode='r')
test.must_match('f8.out', "f8.in\n", mode='r')
test.must_match('f9.out', "f9.in\n", mode='r')
test.must_match('f9.out-Copy', "f9.in\n", mode='r')
test.must_match('d4/f10.in', 'f10.in\n', mode='r')
test.must_match('d4/f11.out', 'f11.in\n', mode='r')
test.must_match('d4/f12.out', 'f12.in\n', mode='r')
test.must_match('f   13.out', 'f   13.in\n', mode='r')

errors = 0

def must_be_same(f1, f2):
    global errors
    if isinstance(f1, list):
        f1 = os.path.join(*f1)
    if isinstance(f2, list):
        f2 = os.path.join(*f2)
    s1 = os.stat(f1)
    s2 = os.stat(f2)
    for value in ['ST_MODE', 'ST_MTIME']:
        v = getattr(stat, value)
        if s1[v] != s2[v]:
            msg = '%s[%s] %s != %s[%s] %s\n' % \
                  (repr(f1), value, s1[v],
                   repr(f2), value, s2[v],)
            sys.stderr.write(msg)
            errors = errors + 1

must_be_same('f1.out',                  'f1.in')
must_be_same(['d2.out', 'file'],        ['d2.in', 'file'])
must_be_same(['d3.out', 'f3.in'],       'f3.in')
must_be_same('f4.out',                  'f4.in')
must_be_same(['d5.out', 'file'],        ['d5.in', 'file'])
must_be_same(['d6.out', 'f6.in'],       'f6.in')
must_be_same('f7.out',                  'f7.in')
must_be_same(['d4', 'f10.in'],          'f10.in')
must_be_same(['d4', 'f11.out'],         'f11.in')
must_be_same(['d4', 'f12.out'],         ['d5', 'f12.in'])
must_be_same('f   13.out',              'f   13.in')

if errors:
    test.fail_test()

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
