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
Verify that the Install() Builder works
"""

import os.path
import sys
import time
import TestSCons

test = TestSCons.TestSCons()

f1_out = test.workpath('export', 'f1.out')
f2_out = test.workpath('export', 'f2.out')
f3_out = test.workpath('export', 'f3.out')

test.write('SConstruct', """\
def cat(env, source, target):
    target = str(target[0])
    source = map(str, source)
    f = open(target, "wb")
    for src in source:
        f.write(open(src, "rb").read())
    f.close()

def my_install(dest, source, env):
    import shutil
    shutil.copy2(source, dest)
    open('my_install.out', 'ab').write(dest)

env1 = Environment()
env1.Append(BUILDERS={'Cat':Builder(action=cat)})
env3 = env1.Copy(INSTALL = my_install)

t = env1.Cat(target='f1.out', source='f1.in')
env1.Install(dir='export', source=t)
t = env1.Cat(target='f2.out', source='f2.in')
env1.Install(dir='export', source=t)

t = env3.Cat(target='f3.out', source='f3.in')
env3.Install(dir='export', source=t)
""")

test.write('f1.in', "f1.in\n")
test.write('f2.in', "f2.in\n")
test.write('f3.in', "f3.in\n")

test.run(arguments = '.')

test.fail_test(test.read(f1_out) != "f1.in\n")
test.fail_test(test.read(f2_out) != "f2.in\n")
test.fail_test(test.read(f3_out) != "f3.in\n")

test.fail_test(test.read('my_install.out') != os.path.join('export', 'f3.out'))

# make sure the programs didn't get rebuilt, because nothing changed:
oldtime1 = os.path.getmtime(f1_out)
oldtime2 = os.path.getmtime(f2_out)

test.write('f1.in', "f1.in again\n")

time.sleep(2) # introduce a small delay, to make the test valid

test.run(arguments = '.')

test.fail_test(oldtime1 == os.path.getmtime(f1_out))
test.fail_test(oldtime2 != os.path.getmtime(f2_out))

# Verify that we didn't link to the Installed file.
open(f2_out, 'wb').write("xyzzy\n")
test.fail_test(test.read('f2.out') != "f2.in\n")

# Verify that scons prints an error message
# if a target can not be unlinked before building it:
test.write('f1.in', "f1.in again again\n")

os.chmod(test.workpath('export'), 0555)
f = open(f1_out, 'rb')

test.run(arguments = f1_out,
         stderr="scons: *** [Errno 13] Permission denied: '%s'\n" % os.path.join('export', 'f1.out'),
         status=2)

f.close()

test.pass_test()
