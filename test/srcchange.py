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
Test changing the C source files based on an always-executed revision
extraction and substitution.
"""

import os.path

import TestSCons

test = TestSCons.TestSCons()

test.write('getrevision', """
#!/usr/bin/env python
import string
print string.strip(open('revnum.in','rb').read())
""")

test.write('SConstruct', """
import re
import string

def subrevision(target, source ,env):
    orig = target[0].get_contents()
    new = re.sub('\$REV.*?\$',
                 '$REV: %%s$'%%string.strip(source[0].get_contents()),
                 target[0].get_contents())
    outf = open(str(target[0]),'wb')
    outf.write(new)
    outf.close()

SubRevision = Action(subrevision)

env=Environment()
content_env=env.Copy()
content_env.TargetSignatures('content')
content_env.Command('revision.in', [], '%(python)s getrevision > $TARGET')
content_env.AlwaysBuild('revision.in')
env.Precious('main.cpp')
env.Command('main.cpp', 'revision.in', SubRevision)
exe = env.Program('main.cpp')
env.Default(exe)
""" % {'python':TestSCons.python})

test.write('main.cpp', """\
#include <iostream>
int
main(int argc, char *argv[])
{
    std::cout << "Revision $REV$" << std::endl;
}
""")

test.write('revnum.in', '3.2\n')

prog = 'main' + TestSCons._exe

full_build=test.wrap_stdout("""\
%(python)s getrevision > revision.in
subrevision(["main.cpp"], ["revision.in"])
g++ -c -o main.o main.cpp
g++ -o main main.o
""" % {'python':TestSCons.python})

light_build=test.wrap_stdout("""\
%(python)s getrevision > revision.in
""" % {'python':TestSCons.python})

test.run(arguments='.', stdout=full_build)
test.must_exist(prog)
test.run(program=test.workpath(prog), stdout='Revision $REV: 3.2$\n')

test.run(arguments='.', stdout=light_build)
test.must_exist(prog)

test.run(arguments='.', stdout=light_build)
test.must_exist(prog)

test.write('revnum.in', '3.3\n')

test.run(arguments='.', stdout=full_build)
test.must_exist(prog)
test.run(program=test.workpath(prog), stdout='Revision $REV: 3.3$\n')

test.pass_test()
