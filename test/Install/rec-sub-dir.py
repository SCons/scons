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
Test using Install() on directory that contains existing subdirectories
causing copytree recursion where the directory already exists.
"""

import os.path

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """\
DefaultEnvironment(tools=[])
Execute(Mkdir('a/b/c'))
Execute(Mkdir('b/c/d'))
Install('z', 'a')
Install('z/a', 'b')
""")

expect="""\
Mkdir("a/b/c")
Mkdir("b/c/d")
Install directory: "a" as "z%sa"
Install directory: "b" as "z%sa%sb"
""" % (os.sep, os.sep, os.sep)
test.run(arguments=["-Q"], stdout=expect)

test.must_exist(test.workpath('a', 'b', 'c'))
test.must_exist(test.workpath('b', 'c', 'd'))
test.must_exist(test.workpath('z', 'a', 'b', 'c', 'd'))

# this run used to fail on Windows with an OS error before the copytree fix
test.run(arguments=["-Q"])

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
