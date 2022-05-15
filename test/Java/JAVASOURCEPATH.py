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
Verify that use of $JAVASOURCEPATH allows finding source .java
files in alternate locations by adding the -sourcepath option
to the javac command line.
"""

import TestSCons

test = TestSCons.TestSCons()

where_javac, java_version = test.java_where_javac()

test.write('SConstruct', """
DefaultEnvironment(tools=[])
env = Environment(tools=['javac'])
bar = env.Java(
    target='bar/classes', source='bar/src/TestBar.java', JAVASOURCEPATH=['foo/src']
)
""")

test.subdir('foo',
            ['foo', 'src'],
	    ['foo', 'src', 'com'],
            ['foo', 'src', 'com', 'foo'],
            ['foo', 'src', 'com', 'foo', 'test'],
            'bar', ['bar', 'src'])

test.write(['foo', 'src', 'com', 'foo', 'test', 'TestFoo.java'], """\
package com.foo.test;
public class TestFoo {;}
""")

test.write(['bar', 'src', 'TestBar.java'], """\
package com.bar.test;
import com.foo.test.TestFoo;
class TestBar extends TestFoo {;}
""")

test.run(arguments = '.')

test.must_exist(['bar', 'classes', 'com', 'bar', 'test', 'TestBar.class'])
test.must_exist(['bar', 'classes', 'com', 'foo', 'test', 'TestFoo.class'])

test.up_to_date(arguments = '.')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
