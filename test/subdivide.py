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
Verify that rebuilds do not occur when SConsignFile(None) is used to
put a .sconsign file in each directory and we subdvide the dependency
tree with subsidiary *SConstruct* files in various subdirectories.

This depends on using content signatures for evaluation of
intermediate Nodes. This relies on the default behavior
being the equivalent of Decider('content').
"""

import os
import TestSCons

test = TestSCons.TestSCons()

test.subdir('src', ['src', 'sub'])

_python_ = TestSCons._python_

# Because this test sets SConsignFile(None), we execute our fake
# scripts directly, not by feeding them to the Python executable.
# That is, we chmod 0o755 and use a "#!/usr/bin/env python" first
# line for POSIX systems, and add .PY to the %PATHEXT% variable on
# Windows.  If we didn't do this, then running this script with
# suitable prileveges would create a .sconsign file in the directory
# where the Python executable lives.  This can happen out of the
# box on Mac OS X, with the result that the .sconsign statefulness
# can mess up other tests.

fake_cc_py = test.workpath('fake_cc.py')
fake_link_py = test.workpath('fake_link.py')

test.write(fake_cc_py, """\
import sys
with open(sys.argv[1], 'w') as ofp:
    ofp.write('fake_cc.py:  %s\\n' % sys.argv)
    for s in sys.argv[2:]:
        with open(s, 'r') as ifp:
            ofp.write(ifp.read())
""")

test.write(fake_link_py, """\
import sys
with open(sys.argv[1], 'w') as ofp:
    ofp.write('fake_link.py:  %s\\n' % sys.argv)
    for s in sys.argv[2:]:
        with open(s, 'r') as ifp:
            ofp.write(ifp.read())
""")

test.chmod(fake_cc_py, 0o755)
test.chmod(fake_link_py, 0o755)

test.write('SConstruct', """\
DefaultEnvironment(tools=[])
SConsignFile(None)
env = Environment(PROGSUFFIX = '.exe',
                  OBJSUFFIX = '.obj',
                  CCCOM = r'%(_python_)s %(fake_cc_py)s $TARGET $SOURCES',
                  LINKCOM = r'%(_python_)s %(fake_link_py)s $TARGET $SOURCES')
env.PrependENVPath('PATHEXT', '.PY')
env.SConscript('src/SConstruct', exports=['env'])
env.Object('foo.c')
""" % locals())

test.write(['src', 'SConstruct'], """\
DefaultEnvironment(tools=[])
SConsignFile(None)
env = Environment(PROGSUFFIX = '.exe',
                  OBJSUFFIX = '.obj',
                  CCCOM = r'%(_python_)s %(fake_cc_py)s $TARGET $SOURCES',
                  LINKCOM = r'%(_python_)s %(fake_link_py)s $TARGET $SOURCES')
env.PrependENVPath('PATHEXT', '.PY')
p = env.Program('prog', ['main.c', '../foo$OBJSUFFIX', 'sub/bar.c'])
env.Default(p)
""" % locals())

test.write('foo.c', """\
foo.c
""")

test.write(['src', 'main.c'], """\
src/main.c
""")

test.write(['src', 'sub', 'bar.c'], """\
src/sub/bar.c
""")

test.run()

src_prog_exe    = os.path.join('src', 'prog.exe')
src_main_c      = os.path.join('src', 'main.c')
src_main_obj    = os.path.join('src', 'main.obj')
src_sub_bar_c   = os.path.join('src', 'sub', 'bar.c')
src_sub_bar_obj = os.path.join('src', 'sub', 'bar.obj')

expect = """\
fake_link.py:  ['%(fake_link_py)s', '%(src_prog_exe)s', '%(src_main_obj)s', 'foo.obj', '%(src_sub_bar_obj)s']
fake_cc.py:  ['%(fake_cc_py)s', '%(src_main_obj)s', '%(src_main_c)s']
src/main.c
fake_cc.py:  ['%(fake_cc_py)s', 'foo.obj', 'foo.c']
foo.c
fake_cc.py:  ['%(fake_cc_py)s', '%(src_sub_bar_obj)s', '%(src_sub_bar_c)s']
src/sub/bar.c
""" % locals()

if os.sep == '\\':
    expect = expect.replace('\\', '\\\\')

test.must_match(['src', 'prog.exe'], expect, mode='r')

test.up_to_date(chdir='src', arguments = test.workpath())

test.up_to_date(arguments = '.')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
