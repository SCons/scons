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
__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

"""
Use pychecker to catch various Python coding errors.
"""

import os
import os.path
import sys

import TestSCons

test = TestSCons.TestSCons()

test.skip_test('Not ready for clean pychecker output; skipping test.\n')

try:
    import pychecker
except ImportError:
    pychecker = test.where_is('pychecker')
    if not pychecker:
        test.skip_test("Could not find 'pychecker'; skipping test(s).\n")
    program = pychecker
    default_arguments = []
else:
    pychecker = os.path.join(os.path.split(pychecker.__file__)[0], 'checker.py')
    program = sys.executable
    default_arguments = [pychecker]

try:
    cwd = os.environ['SCONS_CWD']
except KeyError:
    src_engine = os.environ['SCONS_LIB_DIR']
else:
    src_engine = os.path.join(cwd, 'build', 'scons-src', 'src', 'engine')
    if not os.path.exists(src_engine):
        src_engine = os.path.join(cwd, 'src', 'engine')

src_engine_ = os.path.join(src_engine, '')

MANIFEST = os.path.join(src_engine, 'MANIFEST.in')
with open(MANIFEST) as f:
    files = f.read().split()

files = [f for f in files if f[-3:] == '.py']

ignore = [
    'SCons/compat/__init__.py',
    'SCons/compat/_scons_UserString.py',
    'SCons/compat/_scons_hashlib.py',
    'SCons/compat/_scons_sets.py',
    'SCons/compat/_scons_subprocess.py',
    'SCons/compat/builtins.py',
]

u = {}
for file in files:
    u[file] = 1
for file in ignore:
    try:
        del u[file]
    except KeyError:
        pass
files = sorted(u.keys())

mismatches = []

default_arguments.extend([
    '--quiet',
    '--limit=1000',
    # Suppress warnings about unused arguments to functions and methods.
    # We have too many wrapper functions that intentionally only use some
    # of their arguments.
    '--no-argsused',
])

if sys.platform == 'win32':
    default_arguments.extend([
        '--blacklist', '"pywintypes,pywintypes.error"',
    ])

per_file_arguments = {
    #'SCons/__init__.py' : [
    #    '--varlist',
    #    '"__revision__,__version__,__build__,__buildsys__,__date__,__developer__"',
    #],
}

pywintypes_warning = "warning: couldn't find real module for class pywintypes.error (module name: pywintypes)\n"

os.environ['PYTHONPATH'] = src_engine

for file in files:

    args = (default_arguments + 
            per_file_arguments.get(file, []) +
            [os.path.join(src_engine, file)])

    test.run(program=program, arguments=args, status=None, stderr=None)

    stdout = test.stdout()
    stdout = stdout.replace(src_engine_, '')

    stderr = test.stderr()
    stderr = stderr.replace(src_engine_, '')
    stderr = stderr.replace(pywintypes_warning, '')

    if test.status or stdout or stderr:
        mismatches.append('\n')
        mismatches.append(' '.join([program] + args) + '\n')

        mismatches.append('STDOUT =====================================\n')
        mismatches.append(stdout)

        if stderr:
            mismatches.append('STDERR =====================================\n')
            mismatches.append(stderr)

if mismatches:
    print(''.join(mismatches[1:]))
    test.fail_test()

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
