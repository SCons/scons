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
Test that SCons supports use of a home-brew ToolSurrogate class
like we use in our bin/sconsexamples.py script.
"""

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """\
class Curry:
    def __init__(self, fun, *args, **kwargs):
        self.fun = fun
        self.pending = args[:]
        self.kwargs = kwargs.copy()

    def __call__(self, *args, **kwargs):
        if kwargs and self.kwargs:
            kw = self.kwargs.copy()
            kw.update(kwargs)
        else:
            kw = kwargs or self.kwargs

        return apply(self.fun, self.pending + args, kw)

def Str(target, source, env, cmd=""):
    return env.subst(cmd, target=target, source=source)

class ToolSurrogate:
    def __init__(self, tool, variable, func):
        self.tool = tool
        self.variable = variable
        self.func = func
    def __call__(self, env):
        t = Tool(self.tool)
        t.generate(env)
        orig = env[self.variable]
        env[self.variable] = Action(self.func, strfunction=Curry(Str, cmd=orig))

def Cat(target, source, env):
    target = str(target[0])
    f = open(target, "wb")
    for src in map(str, source):
        f.write(open(src, "rb").read())
    f.close()

ToolList = {
    'posix' :   [('cc', 'CCCOM', Cat),
                 ('link', 'LINKCOM', Cat)],
    'win32' :   [('msvc', 'CCCOM', Cat),
                 ('mslink', 'LINKCOM', Cat)]
}

platform = ARGUMENTS['platform']
tools = map(lambda t: apply(ToolSurrogate, t), ToolList[platform])

env = Environment(tools=tools, PROGSUFFIX='.exe', OBJSUFFIX='.obj')
env.Program('foo.c')
""")

test.write('foo.c', "foo.c posix\n")

test.run(arguments = '. platform=posix', stdout = test.wrap_stdout("""\
cc -c -o foo.obj foo.c
cc -o foo.exe foo.obj
"""))

test.write('foo.c', "foo.c win32\n")

test.run(arguments = '. platform=win32', stdout = test.wrap_stdout("""\
cl /nologo /c foo.c /Fofoo.obj
link /nologo /OUT:foo.exe foo.obj
"""))

test.pass_test()
