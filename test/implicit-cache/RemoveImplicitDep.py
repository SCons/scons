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
A weird case with implicit_cache not working with multiple targets
"""

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.subdir(['src'])

SConstruct_contents = """\
DefaultEnvironment(tools=[])
import SCons.Script

SetOption( 'implicit_cache', 1 )

env = Environment(tools=[])
act = Action([Touch('${TARGETS[0]}'),Touch('${TARGETS[1]}')])
env.Append(BUILDERS = {'BuildMe':Builder(action=act,source_scanner=SCons.Script.SourceFileScanner)} )

env.BuildMe( source='inc.c', target=['a','b'] )
"""

test.write(['src', 'SConstruct'], SConstruct_contents)

test.write(['src', 'inc.c'], """\
#include <f1.h>
#include <f2.h>
""")
test.write(['src', 'f1.h'], 'blah' )
test.write(['src', 'f2.h'], 'blah' )
        
expect = test.wrap_stdout("""\
Touch("a")
Touch("b")
""")

test.run(chdir='src', arguments='', stdout=expect)

test.write(['src', 'inc.c'], """\
#include <f2.h>
""")
test.unlink( ['src', 'f1.h'] )

test.run(chdir='src', arguments='', stdout=expect)

test.pass_test()
