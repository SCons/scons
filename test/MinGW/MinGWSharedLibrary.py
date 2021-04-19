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
Test the ability to configure the $RCCOM construction variable
when using MinGW.
"""

import sys
import TestSCons

import SCons.Tool
import SCons.Tool.mingw
import SCons.Defaults
from SCons.Platform.mingw import MINGW_DEFAULT_PATHS
from SCons.Platform.cygwin import CYGWIN_DEFAULT_PATHS

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

if sys.platform not in ('cygwin', 'win32',):
    test.skip_test("Skipping mingw test on non-Windows platform %s." % sys.platform)

dp = MINGW_DEFAULT_PATHS
gcc = SCons.Tool.find_program_path(test.Environment(), 'gcc', default_paths=dp)
if not gcc:
    test.skip_test("Skipping mingw test, no MinGW found.\n")

test.write('foobar.cc', """
int abc(int a) {
  return (a+1);
}
""")

test.write('SConstruct', """
DefaultEnvironment(tools=[])
env = Environment(tools=['mingw', 'link', 'g++'])
foobar_obj = env.SharedObject('foobar.cc')
env.SharedLibrary('foobar', foobar_obj)

# Now verify versioned shared library doesn't fail
env.SharedLibrary('foobar_ver', foobar_obj, SHLIBVERSION='2.4')
""" % locals())

test.run(arguments = ".")

#test.must_match('aaa.o', "aaa.rc\n")



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
