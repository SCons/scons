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
This tests the --duplicate command line option, and the duplicate
SConscript settable option.
"""

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import os
import sys
import stat
import TestSCons

python = TestSCons.python

test = TestSCons.TestSCons()

test.write('SConstruct', """
DefaultEnvironment(tools=[])
try:
    duplicate = ARGUMENTS['duplicate']
    SetOption('duplicate', duplicate)
except KeyError:
    pass
VariantDir('build', '.', duplicate=1)
SConscript('build/SConscript')
""")

test.write('SConscript', '')

# we don't use links on windows currently as they
# require permissions not usually set
hard = hasattr(os, 'link') and sys.platform != 'win32'
soft = hasattr(os, 'symlink') and sys.platform != 'win32'
copy = 1 # should always work

bss = test.workpath('build/SConscript')

criterion_hardlinks = {
    'hard'      : lambda nl, islink: nl == 2 and not islink,
    'soft'      : lambda nl, islink: nl == 1 and islink,
    'copy'      : lambda nl, islink: nl == 1 and not islink,
}

criterion_no_hardlinks = {
    'hard'      : lambda nl, islink: not islink,
    'soft'      : lambda nl, islink: islink,
    'copy'      : lambda nl, islink: not islink,
}

# On systems without hard linking, it doesn't make sense to check ST_NLINK
if hard:
    criterion = criterion_hardlinks
else:
    criterion = criterion_no_hardlinks

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
usage: scons [OPTIONS] [VARIABLES] [TARGETS]

SCons Error: `nonsense' is not a valid duplication option type, try:
    hard-soft-copy, soft-hard-copy, hard-copy, soft-copy, copy
""")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
