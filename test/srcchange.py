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

"""
Test changing the C source files based on an always-executed revision
extraction and substitution.

This makes sure we evaluate the content of intermediate files as
expected.  This relies on the default behavior being the equivalent
of Decider('content').
"""

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"


import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.write('getrevision', r"""
with open('revnum.in', 'r') as f:
    print(f.read().strip(), end='')
""")

test.write('SConstruct', r"""
import re

def subrevision(target, source ,env):
    orig = target[0].get_text_contents()
    new = re.sub(r'\$REV.*?\$',
                 '$REV: %%s$'%%source[0].get_text_contents().strip(),
                 target[0].get_text_contents())
    with open(str(target[0]),'w') as outf:
        outf.write(new)

SubRevision = Action(subrevision)

env=Environment()
content_env=env.Clone()
content_env.Command('revision.in', [], r'%(_python_)s getrevision > $TARGET')
content_env.AlwaysBuild('revision.in')
env.Precious('main.c')
env.Command('main.c', 'revision.in', SubRevision)
exe = env.Program('main.c')
env.Default(exe)
""" % locals())

test.write('main.c', r"""
#include <stdio.h>
#include <stdlib.h>
#include <stdio.h>
int
main(int argc, char *argv[])
{
    printf("Revision $REV$\n");
    exit (0);
}

""", mode='w')

test.write('revnum.in', '3.2\n')

program_name = 'main' + TestSCons._exe

light_build = test.wrap_stdout("""\
%(_python_)s getrevision > revision.in
""" % locals())

test.run(arguments='.')
test.must_exist(program_name)
test.run(program=test.workpath(program_name), stdout='Revision $REV: 3.2$\n')

test.run(arguments='.', stdout=light_build)
test.must_exist(program_name)

test.run(arguments='.', stdout=light_build)
test.must_exist(program_name)

test.write('revnum.in', '3.3\n', mode='w')

test.run(arguments='.')
test.must_exist(program_name)
test.run(program=test.workpath(program_name), stdout='Revision $REV: 3.3$\n')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
