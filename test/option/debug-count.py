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
Test that the --debug=count option works.
"""

import string
import re

import TestSCons

test = TestSCons.TestSCons()

try:
    import weakref
except ImportError:
    x = "Python version has no 'weakref' module; skipping tests.\n"
    test.skip_test(x)



test.write('SConstruct', """
def cat(target, source, env):
    open(str(target[0]), 'wb').write(open(str(source[0]), 'rb').read())
env = Environment(BUILDERS={'Cat':Builder(action=Action(cat))})
env.Cat('file.out', 'file.in')
""")

test.write('file.in', "file.in\n")

# Just check that object counts for some representative classes
# show up in the output.

def find_object_count(s, stdout):
    re_string = '\d+ +\d+   %s' % re.escape(s)
    return re.search(re_string, stdout)

objects = [
    'Action.CommandAction',
    'Builder.BuilderBase',
    'Environment.Base',
    'Executor.Executor',
    'Node.FS',
    'Node.FS.Base',
    'Node.Node',
]

for args in ['-h --debug=count', '--debug=count']:
    test.run(arguments = args)
    stdout = test.stdout()

    missing = filter(lambda o: find_object_count(o, stdout) is None, objects)

    if missing:
        print "Missing the following object lines from '%s' output:" % args
        print "\t", string.join(missing)
        print "STDOUT =========="
        print stdout
        test.fail_test(1)

expect_warning = """
scons: warning: --debug=count is not supported when running SCons
\twith the python -O option or optimized \\(.pyo\\) modules.
""" + TestSCons.file_expr

test.run(arguments = '--debug=count -h',
         interpreter = ['python', '-O'],
         stderr = expect_warning,
         match = TestSCons.match_re)


test.pass_test()
