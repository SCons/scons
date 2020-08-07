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
Verify that targets with the same SideEffect are not built in parallel
when the -j option is used.
"""

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.write('build.py', """
import os
import sys
import time

lockdir = 'build.lock'
logfile = 'log.txt'

try:
    os.mkdir(lockdir)
except OSError as e:
    msg = 'could not create lock directory: %s\\n' % e
    sys.stderr.write(msg)
    sys.exit(1)

src, target = sys.argv[1:]

with open(logfile, 'ab') as f:
    f.write(('%s -> %s\\n' % (src, target)).encode())
with open(target, 'wb') as ofp, open(src, 'rb') as ifp:
    ofp.write(ifp.read())

# Give the other threads a chance to start.
time.sleep(1)

os.rmdir(lockdir)
""")

test.write('SConstruct', """\
Build = Builder(action=r'%(_python_)s build.py $SOURCE $TARGET')
env = Environment(BUILDERS={'Build':Build})
env.Build('h1.out', 'h1.in')
env.Build('g2.out', 'g2.in')
env.Build('f3.out', 'f3.in')
SideEffect('log.txt', ['h1.out', 'g2.out', 'f3.out'])
env.Build('log.out', 'log.txt')
""" % locals())

test.write('h1.in', 'h1.in\n')
test.write('g2.in', 'g2.in\n')
test.write('f3.in', 'f3.in\n')
test.write('baz.in', 'baz.in\n')


test.run(arguments = "-j 4 .")

test.must_match('h1.out', 'h1.in\n')
test.must_match('g2.out', 'g2.in\n')
test.must_match('f3.out', 'f3.in\n')
test.must_exist('log.txt')
test.must_exist('log.out')

stdout = test.stdout()


build_lines =  [
    'build.py h1.in h1.out', 
    'build.py g2.in g2.out', 
    'build.py f3.in f3.out', 
]

missing = []
for line in build_lines:
    if stdout.find(line) == -1:
        missing.append(line)

if missing:
    print("===== standard output is missing the following lines:")
    print('\n'.join(missing))
    print("===== STDOUT ========================================")
    print(stdout)
    test.fail_test()


log = test.read('log.txt', mode='r')

log_lines = [
    'f3.in -> f3.out',
    'h1.in -> h1.out',
    'g2.in -> g2.out',
]

missing = []
for line in log_lines:
    if log.find(line) == -1:
        missing.append(line)

if missing:
    print("===== log file 'log.txt' is missing the following lines:")
    print('\n'.join(missing))
    print("===== STDOUT ===========================================")
    print(log)
    test.fail_test()

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
