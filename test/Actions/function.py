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

import sys

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
    ('literal_in_listcomp', 'Literal inside list comprehension', '2'),
)

DefaultEnvironment(tools=[])
optEnv = Environment(options=options, tools=[])

r = re.compile(optEnv['regexp'])

withClosure = \
r'''
def toto(header='%(header)s', trailer='%(trailer)s'):
    xxx = %(closure_cell_value)s
    def writeDeps(target, source, env, b=%(b)s, r=r %(extraarg)s , header=header, trailer=trailer):
        """+'"""%(docstring)s"""'+"""
        def foo(b=b):
            return %(nestedfuncexp)s

        with open(str(target[0]), 'wb') as f:
            f.write(bytearray(header, 'utf-8'))
            for d in env['ENVDEPS']:
                f.write(bytearray(d+'%(separator)s', 'utf-8'))
            f.write(bytearray(trailer+'\\n', 'utf-8'))
            f.write(bytearray(str(foo())+'\\n', 'utf-8'))
            f.write(bytearray(r.match('aaaa').group(1)+'\\n', 'utf-8'))
            f.write(bytearray(str(sum([x*%(literal_in_listcomp)s for x in [1, 2]]))+'\\n', 'utf-8'))
            %(extracode)s
            try:
               f.write(bytearray(str(xarg), 'utf-8')+b'\\n')
            except NameError:
               pass

    return writeDeps
'''

exec(withClosure % optEnv)

genHeaderBld = SCons.Builder.Builder(
    action=SCons.Action.Action(toto(), 'Generating $TARGET', varlist=['ENVDEPS']),
    suffix='.gen.h',
)

DefaultEnvironment(tools=[])
env = Environment(tools=[])
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

def runtest(arguments, expectedOutFile, expectedRebuild=True, stderr=""):
    test.run(
        arguments=arguments,
        stdout=expectedRebuild and rebuildstr or nobuildstr,
        stderr="",
    )

    sys.stdout.write('First Build.\n')

    test.must_match('Out.gen.h', expectedOutFile, message="First Build")

    # Should not be rebuild when run a second time with the same arguments.
    sys.stdout.write('Rebuild.\n')

    test.run(arguments=arguments, stdout=nobuildstr, stderr="")
    test.must_match('Out.gen.h', expectedOutFile, message="Should not rebuild")

# We're making this script chatty to prevent timeouts on really really
# slow buildbot slaves (*cough* Solaris *cough*).

sys.stdout.write('Original build.\n')
runtest('', """Head:0:1:Tail\n18\naaa\n6\n""")

sys.stdout.write('Changing a docstring should not cause a rebuild.\n')
runtest('docstring=ThisBuilderDoesXAndY', """Head:0:1:Tail\n18\naaa\n6\n""", False)
runtest('docstring=SuperBuilder', """Head:0:1:Tail\n18\naaa\n6\n""", False)
runtest('docstring=', """Head:0:1:Tail\n18\naaa\n6\n""", False)

sys.stdout.write('Changing a variable in the varlist should cause a rebuild.\n')
runtest('NbDeps=3', """Head:0:1:2:Tail\n18\naaa\n6\n""")
runtest('NbDeps=4', """Head:0:1:2:3:Tail\n18\naaa\n6\n""")
runtest('', """Head:0:1:Tail\n18\naaa\n6\n""")

sys.stdout.write('Changing the function code should cause a rebuild.\n')
runtest('extracode=f.write(bytearray("XX\\n","utf-8"))', """Head:0:1:Tail\n18\naaa\n6\nXX\n""")
runtest('extracode=a=2', """Head:0:1:Tail\n18\naaa\n6\n""")
runtest('', """Head:0:1:Tail\n18\naaa\n6\n""")

sys.stdout.write('Changing a constant in the function code should cause a rebuild.\n')
runtest('separator=,', """Head:0,1,Tail\n18\naaa\n6\n""")
runtest('separator=;', """Head:0;1;Tail\n18\naaa\n6\n""")
runtest('', """Head:0:1:Tail\n18\naaa\n6\n""")

sys.stdout.write('Changing the code of a nested function should cause a rebuild.\n')
runtest('nestedfuncexp=b-xxx', """Head:0:1:Tail\n-18\naaa\n6\n""")
runtest('nestedfuncexp=b+xxx', """Head:0:1:Tail\n32\naaa\n6\n""")
runtest('', """Head:0:1:Tail\n18\naaa\n6\n""")

sys.stdout.write('Adding an extra argument should cause a rebuild.\n')
runtest('extraarg=,xarg=2', """Head:0:1:Tail\n18\naaa\n6\n2\n""")
runtest('extraarg=,xarg=5', """Head:0:1:Tail\n18\naaa\n6\n5\n""")
runtest('', """Head:0:1:Tail\n18\naaa\n6\n""")

sys.stdout.write('Changing the value of a default argument should cause a rebuild:  a value.\n')
runtest('b=0', """Head:0:1:Tail\n25\naaa\n6\n""")
runtest('b=9', """Head:0:1:Tail\n16\naaa\n6\n""")
runtest('', """Head:0:1:Tail\n18\naaa\n6\n""")

sys.stdout.write('Changing the value of a default argument should cause a rebuild:  an object.\n')
runtest('regexp=(aaaa)', """Head:0:1:Tail\n18\naaaa\n6\n""")
runtest('regexp=aa(a+)', """Head:0:1:Tail\n18\naa\n6\n""")
runtest('', """Head:0:1:Tail\n18\naaa\n6\n""")

sys.stdout.write('Changing the value of a closure cell value should cause a rebuild:  a value.\n')
runtest('closure_cell_value=32', """Head:0:1:Tail\n25\naaa\n6\n""")
runtest('closure_cell_value=7', """Head:0:1:Tail\n0\naaa\n6\n""")
runtest('', """Head:0:1:Tail\n18\naaa\n6\n""")

sys.stdout.write('Changing the value of a closure cell value should cause a rebuild:  a default argument.\n')
runtest('header=MyHeader:', """MyHeader:0:1:Tail\n18\naaa\n6\n""")
runtest('trailer=MyTrailer', """Head:0:1:MyTrailer\n18\naaa\n6\n""")
runtest('', """Head:0:1:Tail\n18\naaa\n6\n""")

sys.stdout.write('Changing the value of a literal in a list comprehension should cause a rebuild.\n')
runtest('literal_in_listcomp=3', """Head:0:1:Tail\n18\naaa\n9\n""")
runtest('literal_in_listcomp=4', """Head:0:1:Tail\n18\naaa\n12\n""")
runtest('', """Head:0:1:Tail\n18\naaa\n6\n""")


test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
