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
Verify the Jar() behavior when we have no JARCHDIR set (it should
automatically use the classdir that was deduced from the Java() call)
and when we explicity set it to None (it should not use the Java()
classdir attribute at all).
"""

import TestSCons

test = TestSCons.TestSCons()

# will skip tests when needed tools not present.
where_javac, java_version = test.java_where_javac()
where_jar = test.java_where_jar()

test.subdir('src')

test.write(['src', 'a.java'], """\
package foo.bar;
public class a {}
""")

test.write(['src', 'b.java'], """\
package foo.bar;
public class b {}
""")

test.write('SConstruct', """\
env = Environment(tools    = ['javac', 'jar'])

jar = env.Jar('x.jar', env.Java(target = 'classes', source = 'src'))
""" % locals())

test.run(arguments = '.')
test.run(program = where_jar, arguments = 'tf x.jar')

expect = """\
foo/bar/a.class
foo/bar/b.class
"""

test.must_contain_all_lines(test.stdout(), [expect])

test.run(arguments = '-c')

test.write('SConstruct', """\
env = Environment(tools    = ['javac', 'jar'],
                  JARCHDIR = None)

jar = env.Jar('x.jar', env.Java(target = 'classes', source = 'src'))
""" % locals())

test.run(arguments = '.')

test.run(program = where_jar, arguments = 'tf x.jar')

expect = """\
classes/foo/bar/a.class
classes/foo/bar/b.class
"""

test.must_contain_all_lines(test.stdout(), [expect])
test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
