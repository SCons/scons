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

Verify that we handle the case where Install() and InstallAs()
Builder instances are saved and then re-used from a different, Clone()d
construction environment, after the .Install() and .InstallAs() methods
are replaced by wrappers that fetch the saved methods from a different
environment.
"""

import os.path

import TestSCons

test = TestSCons.TestSCons()

test.subdir('outside', 'sub')

test.write('SConstruct', """\
DefaultEnvironment(tools=[])
import os.path

def cat(env, source, target):
    target = str(target[0])
    with open(target, 'wb') as ofp:
        for src in source:
            with open(str(src), 'rb') as ifp:
                ofp.write(ifp.read())

env = Environment(tools=[], DESTDIR='dest')
env.Append(BUILDERS={'Cat':Builder(action=cat)})

env.SconsInternalInstallFunc = env.Install
env.SconsInternalInstallAsFunc = env.InstallAs

def InstallWithDestDir(dir, source):
    abspath = os.path.splitdrive(env.Dir(dir).get_abspath())[1]
    return env.SconsInternalInstallFunc('$DESTDIR'+abspath, source)
def InstallAsWithDestDir(target, source):
    abspath = os.path.splitdrive(env.File(target).get_abspath())[1]
    return env.SconsInternalInstallAsFunc('$DESTDIR'+abspath, source)

# Add the wrappers directly as attributes.
env.Install = InstallWithDestDir
env.InstallAs = InstallAsWithDestDir

e1 = env

t = e1.Cat(target='f1.out', source='f1.in')
e1.Install('export', source=t)
t = e1.Cat(target='f2.out', source='f2.in')
e1.InstallAs('export/f2-new.out', source=t)

e2 = env.Clone()

t = e2.Cat(target='f3.out', source='f3.in')
e2.Install('export', source=t)
t = e2.Cat(target='f4.out', source='f4.in')
e2.InstallAs('export/f4-new.out', source=t)

""")

test.write('f1.in', "f1.in\n")
test.write('f2.in', "f2.in\n")
test.write('f3.in', "f3.in\n")
test.write('f4.in', "f4.in\n")

test.run(arguments = '.')

export = os.path.splitdrive(test.workpath('export'))[1]

f1_out     = test.workpath('dest') + os.path.join(export, 'f1.out')
f2_new_out = test.workpath('dest') + os.path.join(export, 'f2-new.out')
f3_out     = test.workpath('dest') + os.path.join(export, 'f3.out')
f4_new_out = test.workpath('dest') + os.path.join(export, 'f4-new.out')

test.must_match(f1_out,         "f1.in\n")
test.must_match(f2_new_out,     "f2.in\n")
test.must_match(f3_out,         "f3.in\n")
test.must_match(f4_new_out,     "f4.in\n")

test.up_to_date(arguments = '.')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
