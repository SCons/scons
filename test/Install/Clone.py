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
Verify that we can Install() and InstallAs() from a construction
environment cloned from a clone.
"""

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """
DefaultEnvironment(tools=[])
env1 = Environment(DESTDIR='sub1', tools=[])

# Call env1.Install() but not env1.InstallAs() *before* we clone it.
# This is to verify that re-initializing the Install() attribute on the
# construction environment doesn't mess up the environment settings in
# a way that leaves the InstallAs() intializer in place, which leads to
# infinite recursion.
env1.Install('$DESTDIR', 'foo.in')

env2 = env1.Clone(DESTDIR='sub2')
env3 = env2.Clone(DESTDIR='sub3')

env2.Install('$DESTDIR', 'foo.in')
env3.Install('$DESTDIR', 'foo.in')

env1.InstallAs('$DESTDIR/foo.out', 'foo.in')
env2.InstallAs('$DESTDIR/foo.out', 'foo.in')
env3.InstallAs('$DESTDIR/foo.out', 'foo.in')
""")

test.write('foo.in', "foo.in\n")

test.run(arguments = '.')

test.must_match(['sub1', 'foo.in'], "foo.in\n")
test.must_match(['sub2', 'foo.in'], "foo.in\n")
test.must_match(['sub3', 'foo.in'], "foo.in\n")

test.must_match(['sub1', 'foo.out'], "foo.in\n")
test.must_match(['sub2', 'foo.out'], "foo.in\n")
test.must_match(['sub3', 'foo.out'], "foo.in\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
