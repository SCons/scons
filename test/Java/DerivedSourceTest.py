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
Test of javac.py when building java code from derived sources.

Original issue definition:
Java emitter for derived sources outputs bogus class files.

Repeatable with any N-tier, with N > 1, Java derived-source builds where
any of the following conditions are meet:
1. The java class does not belong to the root package.
2. A java source (*.java) creates N targets (*.class) where N > 1.
"""

import os
import TestSCons
import SCons.Node.FS
import SCons.Defaults

SCons.Defaults.DefaultEnvironment(tools = [])

test = TestSCons.TestSCons()

# This test is known to fail as of July 2014; see Tigris issue 1771 and issue 2931.
# Once the underlying issue is corrected, this test should be re-enabled.
test.skip_test('Skipping derived-source test until issue 1771 is fixed.\n')

# No result if tools not available
test.no_result( condition=(test.where_is( 'javac' ) is None) )
test.no_result( condition=(test.where_is( 'jar' ) is None) )

test.write(
    ['Sample.java'],
"""
// Condition 1: class does not exist in the root package.
package org.sample;

public class Sample {
    // Condition 2: inner class definition causes javac to create
    // a second class file.
    enum InnerEnum {
        stuff,
        and,
        things
    }
}
"""
)

test.write(
    ['SConstruct'],
"""
import os

env = Environment(
    tools = [
        'javac',
        'jar',
    ]
)

env.Command(
    os.path.join( 'org', 'sample', 'Sample.java' ),
   'Sample.java',
    Copy(
        '$TARGET',
        '$SOURCE'
    )
)

# Copy operation makes the *.java file(s) under org derived-source.
env.Java(
    'build',
    'org'
)
"""
)

expected = test.wrap_stdout(
build_str =
'''\
Copy("org/sample/Sample.java", "Sample.java")
javac -d build -sourcepath org/sample org/sample/Sample.java
+-.
  +-build
  | +-build/org
  |   +-build/org/sample
  |     +-build/org/sample/Sample$InnerEnum.class
  |      +-org/sample/Sample.java
  |     +-build/org/sample/Sample.class
  |      +-org/sample/Sample.java
  +-org
    +-org/sample
      +-org/sample/Sample.java
'''.replace( '/', os.sep )
)

test.run( arguments = '--tree=derived', stdout = expected )

test.up_to_date(arguments = '.')
