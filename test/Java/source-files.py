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
Verify that we can pass the Java() builder explicit lists of .java
files as sources.
"""

import TestSCons

test = TestSCons.TestSCons()

# Keep this logic because it skips the test if javac or jar not found.
where_javac, java_version = test.java_where_javac()
where_jar = test.java_where_jar()

test.write('SConstruct', """
env = Environment(tools=['javac'])
env.Java(target='class1', source='com/Example1.java')
env.Java(target='class2', source=['com/Example2.java', 'com/Example3.java'])
""")

test.subdir('com', 'src')

test.write(['com', 'Example1.java'], """\
package com;

public class Example1
{

     public static void main(String[] args)
     {

     }

}
""")

test.write(['com', 'Example2.java'], """\
package com;

public class Example2
{

     public static void main(String[] args)
     {

     }

}
""")

test.write(['com', 'Example3.java'], """\
package com;

public class Example3
{

     public static void main(String[] args)
     {

     }

}
""")

test.write(['com', 'Example4.java'], """\
package com;

public class Example4
{

     public static void main(String[] args)
     {

     }

}
""")

test.run(arguments = '.')

test.must_exist    (['class1', 'com', 'Example1.class'])
test.must_not_exist(['class1', 'com', 'Example2.class'])
test.must_not_exist(['class1', 'com', 'Example3.class'])
test.must_not_exist(['class1', 'com', 'Example4.class'])

test.must_not_exist(['class2', 'com', 'Example1.class'])
test.must_exist    (['class2', 'com', 'Example2.class'])
test.must_exist    (['class2', 'com', 'Example3.class'])
test.must_not_exist(['class2', 'com', 'Example4.class'])

test.up_to_date(arguments = '.')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
