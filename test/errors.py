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

import TestCmd
import TestSCons
import string
import sys

python = TestSCons.python

test = TestSCons.TestSCons(match = TestCmd.match_re_dotall)



test.write('foo.in', 'foo\n')

test.write('exit.in', 'exit\n')

test.write('SConstruct', """\
import sys

def foo(env, target, source):
    print str(target[0])
    open(str(target[0]), 'wt').write('foo')

def exit(env, target, source):
    raise 'exit'

env = Environment(BUILDERS = { 'foo'  : Builder(action=foo),
                               'exit' : Builder(action=exit) })

env.foo('foo.out', 'foo.in')
env.exit('exit.out', 'exit.in')
""")

# print_exception doesn't always show a source line if the source file
# no longer exists or that line in the source file no longer exists,
# so make sure the proper variations are supported in the following
# regexp.
stderr = """scons: \*\*\* \[exit.out\] Exception
Traceback \((most recent call|innermost) last\):
(  File ".+", line \d+, in \S+
    [^\n]+
)*(  File ".+", line \d+, in \S+
)*(  File ".+", line \d+, in \S+
    [^\n]+
)*\S.+
"""

test.run(arguments='foo.out exit.out', stderr=stderr, status=2)

test.run(arguments='foo.out exit.out', stderr=stderr, status=2)
assert string.find(test.stdout(), "scons: `foo.out' is up to date.") != -1, test.stdout()



# Test AttributeError.
test.write('SConstruct', """\
a = 1
a.append(2)
""")

test.run(status = 2, stderr = """\
AttributeError: 'int' object has no attribute 'append':
  File "SConstruct", line 2:
    a.append\(2\)
""")



# Test NameError.
test.write('SConstruct', """\
a == 1
""")

test.run(status = 2, stderr = """\
NameError: [^\n]*
  File "SConstruct", line 1:
    a == 1
""")



# Test SyntaxError.
test.write('SConstruct', """
a ! x
""")

test.run(stdout = "scons: Reading SConscript files ...\n",
	 stderr = """  File "SConstruct", line 2

    a ! x

      \^

SyntaxError: invalid syntax

""", status=2)



# Test TypeError.
test.write('SConstruct', """\
a = 1
a[2] = 3
""")

test.run(status = 2, stderr = """\
TypeError: object does not support item assignment:
  File "SConstruct", line 2:
    a\[2\] = 3
""")



# Test UserError.
test.write('SConstruct', """
assert not globals().has_key("UserError")
import SCons.Errors
raise SCons.Errors.UserError, 'Depends() require both sources and targets.'
""")

test.run(stdout = "scons: Reading SConscript files ...\n",
	 stderr = """
scons: \*\*\* Depends\(\) require both sources and targets.
File "SConstruct", line 4, in \?
""", status=2)



# Test InternalError.
test.write('SConstruct', """
assert not globals().has_key("InternalError")
from SCons.Errors import InternalError
raise InternalError, 'error inside'
""")

test.run(stdout = "scons: Reading SConscript files ...\ninternal error\n",
	 stderr = r"""Traceback \((most recent call|innermost) last\):
  File ".+", line \d+, in .+
  File ".+", line \d+, in .+
  File ".+", line \d+, in .+
  File "SConstruct", line \d+, in \?
    raise InternalError, 'error inside'
InternalError: error inside
""", status=2)

test.write('build.py', '''
import sys
sys.exit(2)
''')



# Test ...
test.write('SConstruct', """
env=Environment()
Default(env.Command(['one.out', 'two.out'], ['foo.in'], action=r'%s build.py'))
"""%python)

test.run(status=2, stderr="scons: \\*\\*\\* \\[one.out\\] Error 2\n")



# Test syntax errors when trying to expand construction variables.
test.write('SConstruct', """\
env = Environment()
env.subst('$foo.bar.3.0')
""")

test.run(status=2, stderr="""
scons: \*\*\* Syntax error `invalid syntax( \(line 1\))?' trying to evaluate `\$foo\.bar\.3\.0'
File "[^"]+", line \d+, in \S+
""")

test.write('SConstruct', """\
env = Environment()
env.subst_list('$foo.3.0.x')
""")

test.run(status=2, stderr="""
scons: \*\*\* Syntax error `invalid syntax( \(line 1\))?' trying to evaluate `\$foo\.3\.0\.x'
File "[^"]+", line \d+, in \S+
""")

#Test syntax errors when trying to expand construction variables at build time:
test.write('SConstruct', """\
env = Environment()
env.Command('foo.bar', [], '$foo.bar.3.0')
""")

test.run(status=2, stderr=r"""scons: \*\*\* \[foo\.bar\] Syntax error `invalid syntax( \(line 1\))?' trying to evaluate `\$foo\.bar\.3\.0'
""")





test.pass_test()
