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

"""
This tests the --duplicate command line option, and the duplicate
SConscript settable option.
"""

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import string
import sys
import os
import os.path
import stat
import TestSCons

python = TestSCons.python

test = TestSCons.TestSCons()

test.write('SConstruct', """
try:
    duplicate = ARGUMENTS['duplicate']
    SetOption('duplicate', duplicate)
except KeyError:
    pass
BuildDir('build', '.', duplicate=1)
SConscript('build/SConscript')
""")

test.write('SConscript', '')

hard = hasattr(os,'link')
soft = hasattr(os,'symlink')
copy = 1 # should always work

bss = test.workpath('build/SConscript')

criterion = {
    'hard'      : lambda nl, islink: nl == 2 and not islink,
    'soft'      : lambda nl, islink: nl == 1 and islink,
    'copy'      : lambda nl, islink: nl == 1 and not islink,
}

description = {
    'hard'      : 'a hard link',
    'soft'      : 'a soft link',
    'copy'      : 'copied',
}

def testLink(file, type):
    nl = os.stat(file)[stat.ST_NLINK]
    islink = os.path.islink(file)
    assert criterion[type](nl, islink), \
           "Expected %s to be %s (nl %d, islink %d)" \
           % (file, description[type], nl, islink)

def RunTest(order, type, bss):
    # Test the command-line --duplicate option.
    test.run(arguments='--duplicate='+order)
    testLink(bss, type)

    # Test setting the option in the SConstruct file.
    test.run(arguments='duplicate='+order)
    testLink(bss, type)

    # Clean up for next run.
    os.unlink(bss)

# test the default (hard-soft-copy)
if hard:   type='hard'
elif soft: type='soft'
else:      type='copy'
RunTest('hard-soft-copy', type, bss)

if soft:   type='soft'
elif hard: type='hard'
else:      type='copy'
RunTest('soft-hard-copy', type, bss)

if soft:   type='soft'
else:      type='copy'
RunTest('soft-copy', type, bss)

if hard:   type='hard'
else:      type='copy'
RunTest('hard-copy', type, bss)

type='copy'
RunTest('copy', type, bss)

test.run(arguments='--duplicate=nonsense', status=2, stderr="""\
usage: scons [OPTION] [TARGET] ...

SCons error: `nonsense' is not a valid duplication style.
""")

test.pass_test()
