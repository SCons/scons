#!/usr/bin/env python
#
# MIT Licenxe
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
Verify that the Install() Builder works
"""

import os.path
import time

import TestSCons

test = TestSCons.TestSCons()

test.subdir('outside', 'work', ['work', 'sub'])

f1_out = test.workpath('work', 'export', 'f1.out')
f2_out = test.workpath('work', 'export', 'f2.out')
f3_out = test.workpath('work', 'export', 'f3.out')
f4_out = test.workpath('work', 'export', 'f4.out')
f5_txt = test.workpath('outside', 'f5.txt')
f6_txt = test.workpath('outside', 'f6.txt')
f6_sep = f6_txt.replace(os.sep, '/')

_SUBDIR_f4_out = os.path.join('$SUBDIR', 'f4.out')

test.write(['work', 'SConstruct'], """\
DefaultEnvironment(tools=[])
def cat(env, source, target):
    target = str(target[0])
    with open(target, 'wb') as ofp:
        for src in source:
            with open(str(src), 'rb') as ifp:
                ofp.write(ifp.read())

def my_install(dest, source, env):
    import shutil
    shutil.copy2(source, dest)
    with open('my_install.out', 'a') as f:
        f.write(dest)

env1 = Environment(tools=[])
env1.Append(BUILDERS={'Cat':Builder(action=cat)})
env3 = env1.Clone(INSTALL = my_install)

t = env1.Cat(target='f1.out', source='f1.in')
env1.Install(dir='export', source=t)
t = env1.Cat(target='f2.out', source='f2.in')
Install(dir='export', source=t)

t = env3.Cat(target='f3.out', source='f3.in')
env3.Install(dir='export', source=t)

env4 = env1.Clone(EXPORT='export', SUBDIR='sub')
t = env4.Cat(target='sub/f4.out', source='sub/f4.in')
env4.Install(dir='$EXPORT', source=r'%(_SUBDIR_f4_out)s')

env1.Install('.', r'%(f5_txt)s')
env1.Install('export', r'%(f5_txt)s')
env1.Install('.', r'%(f6_sep)s')
env1.Install('export', r'%(f6_sep)s')

# test passing a keyword arg (not used, but should be accepted)
env7 = env1.Clone(EXPORT='export')
env7.Install(dir='$EXPORT', source='./f1.in', FOO="bar")

""" % locals())

test.write(['work', 'f1.in'], "f1.in\n")
test.write(['work', 'f2.in'], "f2.in\n")
test.write(['work', 'f3.in'], "f3.in\n")
test.write(['work', 'sub', 'f4.in'], "sub/f4.in\n")
test.write(f5_txt, "f5.txt\n")
test.write(f6_txt, "f6.txt\n")

test.run(chdir = 'work', arguments = '.')

test.must_match(f1_out,                         "f1.in\n", mode='r')
test.must_match(f2_out,                         "f2.in\n", mode='r')
test.must_match(f3_out,                         "f3.in\n", mode='r')
test.must_match(f4_out,                         "sub/f4.in\n", mode='r')
test.must_match(['work', 'f5.txt'],             "f5.txt\n", mode='r')
test.must_match(['work', 'export', 'f5.txt'],   "f5.txt\n", mode='r')
test.must_match(['work', 'f6.txt'],             "f6.txt\n", mode='r')
test.must_match(['work', 'export', 'f6.txt'],   "f6.txt\n", mode='r')

test.must_match(['work', 'my_install.out'], os.path.join('export', 'f3.out'), mode='r')
test.must_match(['work', 'export', 'f1.in'],   "f1.in\n", mode='r')

# make sure the programs didn't get rebuilt, because nothing changed:
oldtime1 = os.path.getmtime(f1_out)
oldtime2 = os.path.getmtime(f2_out)

test.write(['work', 'f1.in'], "f1.in again\n")

time.sleep(2) # introduce a small delay, to make the test valid

test.run(chdir = 'work', arguments = '.')

test.fail_test(oldtime1 == os.path.getmtime(f1_out))
test.fail_test(oldtime2 != os.path.getmtime(f2_out))

# Verify that we didn't link to the Installed file.
with open(f2_out, 'w') as f:
    f.write("xyzzy\n")
test.must_match(['work', 'f2.out'], "f2.in\n", mode='r')

# Verify that scons prints an error message
# if a target can not be unlinked before building it:
test.write(['work', 'f1.in'], "f1.in again again\n")

os.chmod(test.workpath('work', 'export'), 0o555)
with open(f1_out, 'rb'):
    expect = [
        "Permission denied",
        "The process cannot access the file because it is being used by another process",
        "Der Prozess kann nicht auf die Datei zugreifen, da sie von einem anderen Prozess verwendet wird",
    ]

    test.run(chdir='work', arguments=f1_out, stderr=None, status=2)

    test.must_contain_any_line(test.stderr(), expect)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
