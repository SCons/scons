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
Test that SConstruct, SConscript, site_init.py and variables files are not
compiled with the future flags of the SCons modules that run them.

SCons/Script/SConscript.py has "from __future__ import annotations". If a
script inherits that flag, its annotations become strings, which among
other things stops dataclasses from recognising InitVar fields.
"""

import TestSCons

test = TestSCons.TestSCons()

# reports whether an annotation in the script is a type or a string
CHECK = """\
def _f(x: int):
    pass
print("%s:", type(_f.__annotations__['x']).__name__)
"""

INITVAR = """\
from dataclasses import InitVar, dataclass

@dataclass
class _C:
    env: InitVar[int]
    name: str

    def __post_init__(self, env):
        self.seen = env

print("InitVar:", _C(env=1, name="n").seen)
"""

test.subdir('site_scons', 'sub')
test.write(['site_scons', 'site_init.py'], CHECK % "site_init")
test.write('vars.py', CHECK % "variables")
test.write(['sub', 'SConscript'], CHECK % "SConscript" + INITVAR)
test.write('SConstruct', CHECK % "SConstruct" + """\
Environment(tools=[], variables=Variables('vars.py'))
SConscript('sub/SConscript')
""")

# site_init.py is read before the SConscript files
expect = "site_init: type\n" + test.wrap_stdout(
    read_str="SConstruct: type\n"
    "variables: type\n"
    "SConscript: type\n"
    "InitVar: 1\n",
    build_str="scons: `.' is up to date.\n",
)
test.run(arguments='.', stdout=expect)

# an SConstruct read from standard input
expect = "site_init: type\n" + test.wrap_stdout(
    read_str="stdin: type\n",
    build_str="scons: `.' is up to date.\n",
)
test.run(arguments='-f - .', stdin=CHECK % "stdin", stdout=expect)

test.pass_test()
