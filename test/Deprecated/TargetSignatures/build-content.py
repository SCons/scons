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
Verify basic interaction of the historic TargetSignatures('build')
and TargetSignatures('content') settings, overriding one with
the other in specific construction environments.
"""

import re

import TestSCons

test = TestSCons.TestSCons(match = TestSCons.match_re_dotall)

expect = TestSCons.re_escape("""
scons: warning: The env.TargetSignatures() method is deprecated;
\tconvert your build to use the env.Decider() method instead.
""") + TestSCons.file_expr


sconstruct_contents = """\
SetOption('warn', 'deprecated-target-signatures')
env = Environment()

def copy1(env, source, target):
    with open(str(target[0]), 'wb') as fo, open(str(source[0]), 'rb') as fi:
        fo.write(fi.read())

def copy2(env, source, target):
    %s
    return copy1(env, source, target)

env['BUILDERS']['Copy1'] = Builder(action=copy1)
env['BUILDERS']['Copy2'] = Builder(action=copy2)

env.Copy2('foo.mid', 'foo.in')
env.Copy1('foo.out', 'foo.mid')

env2 = env.Clone()
env2.TargetSignatures('%s')
env2.Copy2('bar.mid', 'bar.in')
env2.Copy1('bar.out', 'bar.mid')

TargetSignatures('%s')
"""

def write_SConstruct(test, *args):
    contents = sconstruct_contents % args
    test.write('SConstruct', contents)



write_SConstruct(test, '', 'build', 'content')

test.write('foo.in', 'foo.in')
test.write('bar.in', 'bar.in')

test.run(arguments="bar.out foo.out",
         stdout=re.escape(test.wrap_stdout("""\
copy2(["bar.mid"], ["bar.in"])
copy1(["bar.out"], ["bar.mid"])
copy2(["foo.mid"], ["foo.in"])
copy1(["foo.out"], ["foo.mid"])
""")),
         stderr = expect)

test.up_to_date(arguments='bar.out foo.out', stderr=None)



# Change the code in the the copy2() function, which should change
# its content and trigger a rebuild of the targets built with it.

write_SConstruct(test, 'x = 2 # added this line', 'build', 'content')

test.run(arguments="bar.out foo.out",
         stdout=re.escape(test.wrap_stdout("""\
copy2(["bar.mid"], ["bar.in"])
copy1(["bar.out"], ["bar.mid"])
copy2(["foo.mid"], ["foo.in"])
scons: `foo.out' is up to date.
""")),
         stderr = expect)



# Swapping content and build signatures no longer causes a rebuild
# because we record the right underlying information regardless.

write_SConstruct(test, 'x = 2 # added this line', 'content', 'build')

test.up_to_date(arguments="bar.out foo.out", stderr=None)



# Change the code in the the copy2() function back again, which should
# trigger another rebuild of the targets built with it.

write_SConstruct(test, '', 'content', 'build')

test.run(arguments='bar.out foo.out',
         stdout=re.escape(test.wrap_stdout("""\
copy2(["bar.mid"], ["bar.in"])
scons: `bar.out' is up to date.
copy2(["foo.mid"], ["foo.in"])
copy1(["foo.out"], ["foo.mid"])
""")),
         stderr = expect)



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
