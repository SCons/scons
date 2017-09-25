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
Test calling SConscript through a construction environment.
"""

import TestSCons

test = TestSCons.TestSCons()

test.subdir('sub1', 'sub2')

test.write("SConstruct", """\
env = Environment(SUB1='sub1', SUB2='sub2')
print("SConstruct")
x = 'xxx'
y = 'yyy'
env.Export(["x", "y"])
env.SConscript('$SUB1/SConscript')
env.SConscript(dirs=['$SUB2'])
SConscript(['s1', 's2'])
env.SConscript(['s3', 's4'])
""")

test.write(['sub1', 'SConscript'], """\
env = Environment()
env.Import("x")
print("sub1/SConscript")
print("x = %s"%x)
""")

test.write(['sub2', 'SConscript'], """\
env = Environment()
env.Import("y")
print("sub2/SConscript")
print("y = %s"%y)
""")

test.write('s1', "\n")
test.write('s2', "\n")
test.write('s3', "\n")
test.write('s4', "\n")

expect = """\
SConstruct
sub1/SConscript
x = xxx
sub2/SConscript
y = yyy
"""

test.run(arguments = ".",
         stdout = test.wrap_stdout(read_str = expect,
                                   build_str = "scons: `.' is up to date.\n"))

test.write("SConstruct", """\
def builder(target, source, env):
    import SCons.Script.SConscript
    assert SCons.Script.SConscript.sconscript_reading == 0
env = Environment(BUILDERS={'builder':Builder(action=builder)})
env.builder('test',[])
import SCons.Script.SConscript
assert SCons.Script.SConscript.sconscript_reading == 1
""")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
