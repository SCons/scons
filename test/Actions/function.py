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

#
# Test that the signature of function action includes all the
# necessary pieces.
# 

test.write('SConstruct', r"""
import re

import SCons.Action
import SCons.Builder

options = Variables()
options.AddVariables(
    ('header', 'Header string (default cell argument)', 'Head:'),
    ('trailer', 'Trailer string (default cell argument)', 'Tail'),
    ('NbDeps', 'Number of dependencies', '2'),
    ('separator', 'Separator for the dependencies (function constant)', ':'),
    ('closure_cell_value', 'Value of a closure cell', '25'),
    ('b', 'Value of b (value default argument', '7'),
    ('regexp', 'Regexp (object as a default argument', 'a(a*)'),
    ('docstring', 'Docstring', 'docstring'),
    ('extracode', 'Extra code for the builder function', ''),
    ('extraarg', 'Extra arg builder function', ''),
    ('nestedfuncexp', 'Expression for the nested function', 'xxx - b'),
)

optEnv = Environment(options=options, tools=[])

r = re.compile(optEnv['regexp'])

withClosure = \
r'''
def toto(header='%(header)s', trailer='%(trailer)s'):
    xxx = %(closure_cell_value)s
    def writeDeps(target, source, env, b=%(b)s, r=r %(extraarg)s ,
                  header=header, trailer=trailer):
        """+'"""%(docstring)s"""'+"""
        def foo(b=b):
            return %(nestedfuncexp)s
        f = open(str(target[0]),'wb')
        f.write(header)
        for d in env['ENVDEPS']:
            f.write(d+'%(separator)s')
        f.write(trailer+'\\n')
        f.write(str(foo())+'\\n')
        f.write(r.match('aaaa').group(1)+'\\n')
        %(extracode)s
        try:
           f.write(str(xarg)+'\\n')
        except NameError:
           pass
        f.close()

    return writeDeps
'''

NoClosure = \
r'''
def toto(header='%(header)s', trailer='%(trailer)s'):
    xxx = %(closure_cell_value)s
    def writeDeps(target, source, env, b=%(b)s, r=r %(extraarg)s ,
                  header=header, trailer=trailer, xxx=xxx):
        """+'"""%(docstring)s"""'+"""
        def foo(b=b, xxx=xxx):
            return %(nestedfuncexp)s
        f = open(str(target[0]),'wb')
        f.write(header)
        for d in env['ENVDEPS']:
            f.write(d+'%(separator)s')
        f.write(trailer+'\\n')
        f.write(str(foo())+'\\n')
        f.write(r.match('aaaa').group(1)+'\\n')
        %(extracode)s
        try:
           f.write(str(xarg)+'\\n')
        except NameError:
           pass
        f.close()

    return writeDeps
'''

try:
    # Check that lexical closure are supported
    def a():
        x = 0
        def b():
            return x
        return b
    a().func_closure[0].cell_contents
    exec( withClosure % optEnv )
except (AttributeError, TypeError):
    exec( NoClosure % optEnv )

genHeaderBld = SCons.Builder.Builder(
    action = SCons.Action.Action(
        toto(), 
        'Generating $TARGET',
        varlist=['ENVDEPS']
        ),
    suffix = '.gen.h'
    )

env = Environment()
env.Append(BUILDERS = {'GenHeader' : genHeaderBld})

envdeps = list(map(str, range(int(optEnv['NbDeps']))))

env.GenHeader('Out', None, ENVDEPS=envdeps)
""")


rebuildstr = """\
scons: Reading SConscript files ...
scons: done reading SConscript files.
scons: Building targets ...
Generating Out.gen.h
scons: done building targets.
"""

nobuildstr = """\
scons: Reading SConscript files ...
scons: done reading SConscript files.
scons: Building targets ...
scons: `.' is up to date.
scons: done building targets.
"""

import sys
if sys.version[:3] == '2.1':
    expectedStderr = """\
%s:79: SyntaxWarning: local name 'x' in 'a' shadows use of 'x' as global in nested scope 'b'
  def a():
""" % test.workpath('SConstruct')
else:
    expectedStderr = ""

def runtest(arguments, expectedOutFile, expectedRebuild=True, stderr=expectedStderr):
    test.run(arguments=arguments,
             stdout=expectedRebuild and rebuildstr or nobuildstr,
             stderr=expectedStderr)
    test.must_match('Out.gen.h', expectedOutFile)

    # Should not be rebuild when ran a second time with the same
    # arguments.

    test.run(arguments = arguments, stdout=nobuildstr, stderr=expectedStderr)
    test.must_match('Out.gen.h', expectedOutFile)


# Original build. 
runtest('', """Head:0:1:Tail\n18\naaa\n""")

# Changing a docstring should not cause a rebuild
runtest('docstring=ThisBuilderDoesXAndY', """Head:0:1:Tail\n18\naaa\n""", False)
runtest('docstring=SuperBuilder', """Head:0:1:Tail\n18\naaa\n""", False)
runtest('docstring=', """Head:0:1:Tail\n18\naaa\n""", False)

# Changing a variable listed in the varlist should cause a rebuild
runtest('NbDeps=3', """Head:0:1:2:Tail\n18\naaa\n""")
runtest('NbDeps=4', """Head:0:1:2:3:Tail\n18\naaa\n""")
runtest('', """Head:0:1:Tail\n18\naaa\n""")

# Changing the function code should cause a rebuild
runtest('extracode=f.write("XX\\n")', """Head:0:1:Tail\n18\naaa\nXX\n""")
runtest('extracode=a=2', """Head:0:1:Tail\n18\naaa\n""")
runtest('', """Head:0:1:Tail\n18\naaa\n""")

# Changing a constant used in the function code should cause a rebuild
runtest('separator=,', """Head:0,1,Tail\n18\naaa\n""")
runtest('separator=;', """Head:0;1;Tail\n18\naaa\n""")
runtest('', """Head:0:1:Tail\n18\naaa\n""")

# Changing the code of a nested function should cause a rebuild
runtest('nestedfuncexp=b-xxx', """Head:0:1:Tail\n-18\naaa\n""")
runtest('nestedfuncexp=b+xxx', """Head:0:1:Tail\n32\naaa\n""")
runtest('', """Head:0:1:Tail\n18\naaa\n""")

# Adding an extra argument should cause a rebuild.
runtest('extraarg=,xarg=2', """Head:0:1:Tail\n18\naaa\n2\n""")
runtest('extraarg=,xarg=5', """Head:0:1:Tail\n18\naaa\n5\n""")
runtest('', """Head:0:1:Tail\n18\naaa\n""")

# Changing the value of a default argument should cause a rebuild
# case 1: a value
runtest('b=0', """Head:0:1:Tail\n25\naaa\n""")
runtest('b=9', """Head:0:1:Tail\n16\naaa\n""")
runtest('', """Head:0:1:Tail\n18\naaa\n""")

# case 2: an object
runtest('regexp=(aaaa)', """Head:0:1:Tail\n18\naaaa\n""")
runtest('regexp=aa(a+)', """Head:0:1:Tail\n18\naa\n""")
runtest('', """Head:0:1:Tail\n18\naaa\n""")

# Changing the value of a closure cell value should cause a rebuild
# case 1: a value
runtest('closure_cell_value=32', """Head:0:1:Tail\n25\naaa\n""")
runtest('closure_cell_value=7', """Head:0:1:Tail\n0\naaa\n""")
runtest('', """Head:0:1:Tail\n18\naaa\n""")

# case 2: a default argument
runtest('header=MyHeader:', """MyHeader:0:1:Tail\n18\naaa\n""")
runtest('trailer=MyTrailer', """Head:0:1:MyTrailer\n18\naaa\n""")
runtest('', """Head:0:1:Tail\n18\naaa\n""")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
