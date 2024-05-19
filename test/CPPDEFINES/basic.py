#!/usr/bin/env python
#
# MIT License
#
# Copyright The SCons Foundation
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
Verify basic use of CPPPDEFINES with various data types.
"""

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """\
test_list = [
    'xyz',
    ['x', 'y', 'z'],
    ['x', ['y', 123], 'z', ('int', '$INTEGER')],
    {'c': 3, 'b': None, 'a': 1},
    "${TESTDEFS}",
    "${GEN}",
]

def generator(target, source, env, for_signature):
    if target and source:
        return '_'.join([str(target[0]), 'GENERATED', str(source[0])])
    return 'TARGET_AND_SOURCE_ARE_MISSING'

for i in test_list:
    env = Environment(
        CPPDEFPREFIX='-D',
        CPPDEFSUFFIX='',
        INTEGER=0,
        TESTDEFS=["FOO", "BAR=1"],
        GEN=generator,
    )
    ttt = env.Entry('#ttt')
    sss = env.Entry('#sss')
    print(
        env.Clone(CPPDEFINES=i).subst(
            '$_CPPDEFFLAGS',
            target=[ttt],
            source=[sss],
        )
    )

for i in test_list:
    env = Environment(
        CPPDEFPREFIX='|',
        CPPDEFSUFFIX='|',
        INTEGER=1,
        TESTDEFS=["FOO", "BAR=1"],
        GEN=generator,
    )
    ttt = env.Entry('#ttt')
    sss = env.Entry('#sss')
    print(
        env.Clone(CPPDEFINES=i).subst(
            '$_CPPDEFFLAGS',
            target=[ttt],
            source=[sss],
        )
    )
""")

expect = test.wrap_stdout(
    build_str="scons: `.' is up to date.\n",
    read_str="""\
-Dxyz
-Dx -Dy -Dz
-Dx -Dy=123 -Dz -Dint=0
-Dc=3 -Db -Da=1
-DFOO -DBAR=1
-Dttt_GENERATED_sss
|xyz|
|x| |y| |z|
|x| |y=123| |z| |int=1|
|c=3| |b| |a=1|
|FOO| |BAR=1|
|ttt_GENERATED_sss|
""",
)
test.run(arguments = '.', stdout=expect)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
