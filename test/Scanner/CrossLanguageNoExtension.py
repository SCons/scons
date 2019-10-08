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

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

# Test behavior of Scanners when evaluating implicit dependencies
# for nodes that do not have mappings from their scanner_key
# to a scanner instance

test.write('SConstruct', r"""
import re

include_re = re.compile(r'^include\s+(\S+)$', re.M)

def scan(node, env, scanpaths, arg):
    contents = node.get_text_contents()
    includes = include_re.findall(contents)
    return includes

def kfile_scan(node, env, scanpaths, arg):
    print('kscan: ' + str(node))
    return scan(node, env, scanpaths, arg)

def k2file_scan(node, env, scanpaths, arg):
    print('k2scan: ' + str(node))
    return scan(node, env, scanpaths, arg)

kscan = Scanner(name = 'kfile',
                function = kfile_scan,
                argument = None,
                skeys = ['.k'],
                recursive = True)

k2scan = Scanner(name = 'k2',
                     function = k2file_scan,
                     argument = None,
                     skeys = ['.k2'])

k2scan2 = Scanner(name = 'k2',
                     function = k2file_scan,
                     argument = None,
                     skeys = [''])

env1 = Environment()
env1.Append(SCANNERS = [ kscan, k2scan ] )
env1.Command( 'k', 'foo.k', Copy( '$TARGET', '$SOURCE' ) )

env2 = env1.Clone()
env2.Append(SCANNERS = [ k2scan2 ] )
env2.Command( 'k2', 'foo.k', Copy( '$TARGET', '$SOURCE' ) )
""")

test.write('foo.k',
"""foo.k 1 line 1
include xxx.k
include yyy
foo.k 1 line 4
""")

test.write('xxx.k', "xxx.k 1\n")
test.write('yyy', "yyy 1\n")
test.write('yyy.k2', "yyy.k2 1\n")

expected_stdout = test.wrap_stdout("""\
kscan: foo.k
kscan: xxx.k
kscan: yyy
Copy("k", "foo.k")
kscan: foo.k
kscan: xxx.k
k2scan: yyy
Copy("k2", "foo.k")
""")

test.run(arguments='k k2', stdout=expected_stdout)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
