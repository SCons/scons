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
Test the Qt tool warnings.
"""

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import os
import re

import TestSCons

test = TestSCons.TestSCons()

SConstruct_path = test.workpath('SConstruct')

test.Qt_dummy_installation()

test.Qt_create_SConstruct(SConstruct_path)

test.write('aaa.cpp', r"""
#include "my_qobject.h"
void aaa(void) Q_OBJECT
""")

test.write('SConscript', r"""
Import("env")
import os
env.StaticLibrary('aaa.cpp')
""")

test.run(stderr=None)

match12 = r"""
scons: warning: Generated moc file 'aaa.moc' is not included by 'aaa.cpp'
""" + TestSCons.file_expr

if not re.search(match12, test.stderr()):
    print("Did not find expected regular expression in stderr:")
    print(test.stderr())
    test.fail_test()

os.environ['QTDIR'] = test.QT

test.run(arguments='-n noqtdir=1')

# We'd like to eliminate $QTDIR from the environment as follows:
#       del os.environ['QTDIR']
# But unfortunately, in at least some versions of Python, the Environment
# class doesn't implement a __delitem__() method to make the library
# call to actually remove the deleted variable from the *external*
# environment, so it only gets removed from the Python dictionary.
# Consequently, we need to just wipe out its value as follows>
os.environ['QTDIR'] = ''
test.run(stderr=None, arguments='-n noqtdir=1')

moc = test.where_is('moc')
if moc:
    import os.path
    qtdir = os.path.dirname(os.path.dirname(moc))
    qtdir = qtdir.replace('\\', '\\\\' )

    expect = r"""
scons: warning: Could not detect qt, using moc executable as a hint \(QTDIR=%s\)
File "%s", line \d+, in (\?|<module>)
""" % (qtdir, re.escape(SConstruct_path))
else:

    expect = r"""
scons: warning: Could not detect qt, using empty QTDIR
File "%s", line \d+, in (\?|<module>)
""" % re.escape(SConstruct_path)

test.fail_test(not test.match_re(test.stderr(), expect))

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
