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

This depends on using content signatures for evaluation of intermediate
Nodes.  We used to configure this explicitly using
TargetSignatures('content'), but we now rely on the default behavior
being the equivalent of Decider('content').
"""

import os.path

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

#if os.path.exists('sconsign.py'):
#    sconsign = 'sconsign.py'
#elif os.path.exists('sconsign'):
#    sconsign = 'sconsign'
#else:
#    print "Can find neither 'sconsign.py' nor 'sconsign' scripts."
#    test.no_result(1)

test.subdir('src', ['src', 'sub'])

test.write('fake_cc.py', """\
import sys
ofp = open(sys.argv[1], 'wb')
ofp.write('fake_cc.py:  %s\\n' % sys.argv)
for s in sys.argv[2:]:
    ofp.write(open(s, 'rb').read())
""")

test.write('fake_link.py', """\
import sys
ofp = open(sys.argv[1], 'wb')
ofp.write('fake_link.py:  %s\\n' % sys.argv)
for s in sys.argv[2:]:
    ofp.write(open(s, 'rb').read())
""")

test.write('SConstruct', """\
SConsignFile(None)
env = Environment(PROGSUFFIX = '.exe',
                  OBJSUFFIX = '.obj',
                  CCCOM = r'%(_python_)s fake_cc.py $TARGET $SOURCES',
                  LINKCOM = r'%(_python_)s fake_link.py $TARGET $SOURCES')
env.SConscript('src/SConstruct', exports=['env'])
env.Object('foo.c')
""" % locals())

test.write(['src', 'SConstruct'], """\
SConsignFile(None)
env = Environment(PROGSUFFIX = '.exe',
                  OBJSUFFIX = '.obj',
                  CCCOM = r'%(_python_)s fake_cc.py $TARGET $SOURCES',
                  LINKCOM = r'%(_python_)s fake_link.py $TARGET $SOURCES')
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
fake_link.py:  ['fake_link.py', '%(src_prog_exe)s', '%(src_main_obj)s', 'foo.obj', '%(src_sub_bar_obj)s']
fake_cc.py:  ['fake_cc.py', '%(src_main_obj)s', '%(src_main_c)s']
src/main.c
fake_cc.py:  ['fake_cc.py', 'foo.obj', 'foo.c']
foo.c
fake_cc.py:  ['fake_cc.py', '%(src_sub_bar_obj)s', '%(src_sub_bar_c)s']
src/sub/bar.c
""" % locals()

if os.sep == '\\':
    import string
    expect = string.replace(expect, '\\', '\\\\')

test.must_match(['src', 'prog.exe'], expect)

test.up_to_date(chdir='src', arguments = test.workpath())

test.up_to_date(arguments = '.')

test.pass_test()
