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

from __future__ import print_function

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

"""
Test that --debug can take multiple options
"""

import re

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """
DefaultEnvironment(tools=[])
def cat(target, source, env):
    with open(str(target[0]), 'wb') as f, open(str(source[0]), 'rb') as infp:
        f.write(infp.read())
env = Environment(BUILDERS={'Cat':Builder(action=Action(cat))})
env.Cat('file.out', 'file.in')
""")

test.write('file.in', "file.in\n")

# Just check that object counts for some representative classes
# show up in the output.

def find_object_count(s, stdout):
    re_string = r'\d+ +\d+   %s' % re.escape(s)
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

for args in ['--debug=prepare,count', '--debug=count,prepare']:
    test.run(arguments = args)
    stdout = test.stdout()
    missing = [o for o in objects if find_object_count(o, stdout) is None]

    if missing:
        print("Missing the following object lines from '%s' output:" % args)
        print("\t", ' '.join(missing))
        print("STDOUT ==========")
        print(stdout)
        test.fail_test(1)

    if 'Preparing target file.out...' not in stdout:
        print("Missing 'Preparing' lines from '%s' output:" % args)
        print("STDOUT ==========")
        print(stdout)
        test.fail_test(1)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
