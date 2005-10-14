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
Test how using strfunction() to report different types of
"""

import TestSCons

python = TestSCons.python

test = TestSCons.TestSCons()

test.write('cat.py', """\
import sys
open(sys.argv[2], "wb").write(open(sys.argv[1], "rb").read())
sys.exit(0)
""")

test.write('SConstruct', """\
def strfunction(target, source, env):
    t = str(target[0])
    s = str(source[0])
    return "Building %%s from %%s" %% (t, s)
def func(target, source, env):
    t = str(target[0])
    s = str(source[0])
    open(t, 'w').write(open(s, 'r').read())
funcaction = Action(func, strfunction=strfunction)
cmd = r"%s cat.py $SOURCE $TARGET"
cmdaction = Action(cmd, strfunction=strfunction)
list = [ r"%s cat.py $SOURCE .temp", r"%s cat.py .temp $TARGET" ]
listaction = Action(list, strfunction=strfunction)
lazy = '$LAZY'
lazyaction = Action(lazy, strfunction=strfunction)
dict = {
    '.cmd'      : cmd,
    '.cmdstr'   : cmdaction,
    '.func'     : func,
    '.funcstr'  : funcaction,
    '.list'     : list,
    '.liststr'  : listaction,
    '.lazy'     : lazy,
    '.lazystr'  : lazyaction,
}
env = Environment(BUILDERS = {
                        'Cmd'           : Builder(action=cmd),
                        'CmdStr'        : Builder(action=cmdaction),
                        'Func'          : Builder(action=func),
                        'FuncStr'       : Builder(action=funcaction),
                        'Lazy'          : Builder(action=lazy),
                        'LazyStr'       : Builder(action=lazyaction),
                        'List'          : Builder(action=list),
                        'ListStr'       : Builder(action=listaction),

                        'Dict'          : Builder(action=dict),
                  },
                  LAZY = r"%s cat.py $SOURCE $TARGET")
env.Cmd('cmd.out', 'cmd.in')
env.CmdStr('cmdstr.out', 'cmdstr.in')
env.Func('func.out', 'func.in')
env.FuncStr('funcstr.out', 'funcstr.in')
env.Lazy('lazy.out', 'lazy.in')
env.LazyStr('lazystr.out', 'lazystr.in')
env.List('list.out', 'list.in')
env.ListStr('liststr.out', 'liststr.in')

env.Dict('dict1.out', 'dict1.cmd')
env.Dict('dict2.out', 'dict2.cmdstr')
env.Dict('dict3.out', 'dict3.func')
env.Dict('dict4.out', 'dict4.funcstr')
env.Dict('dict5.out', 'dict5.lazy')
env.Dict('dict6.out', 'dict6.lazystr')
env.Dict('dict7.out', 'dict7.list')
env.Dict('dict8.out', 'dict8.liststr')
""" % (python, python, python, python))

test.write('func.in',           "func.in\n")
test.write('funcstr.in',        "funcstr.in\n")
test.write('cmd.in',            "cmd.in\n")
test.write('cmdstr.in',         "cmdstr.in\n")
test.write('lazy.in',           "lazy.in\n")
test.write('lazystr.in',        "lazystr.in\n")
test.write('list.in',           "list.in\n")
test.write('liststr.in',        "liststr.in\n")

test.write('dict1.cmd',         "dict1.cmd\n")
test.write('dict2.cmdstr',      "dict2.cmdstr\n")
test.write('dict3.func',        "dict3.func\n")
test.write('dict4.funcstr',     "dict4.funcstr\n")
test.write('dict5.lazy',        "dict4.lazy\n")
test.write('dict6.lazystr',     "dict6.lazystr\n")
test.write('dict7.list',        "dict7.list\n")
test.write('dict8.liststr',     "dict8.liststr\n")

test.run(arguments = '.', stdout=test.wrap_stdout("""\
%s cat.py cmd.in cmd.out
Building cmdstr.out from cmdstr.in
%s cat.py dict1.cmd dict1.out
Building dict2.out from dict2.cmdstr
func(["dict3.out"], ["dict3.func"])
Building dict4.out from dict4.funcstr
%s cat.py dict5.lazy dict5.out
Building dict6.out from dict6.lazystr
%s cat.py dict7.list .temp
%s cat.py .temp dict7.out
Building dict8.out from dict8.liststr
Building dict8.out from dict8.liststr
func(["func.out"], ["func.in"])
Building funcstr.out from funcstr.in
%s cat.py lazy.in lazy.out
Building lazystr.out from lazystr.in
%s cat.py list.in .temp
%s cat.py .temp list.out
Building liststr.out from liststr.in
Building liststr.out from liststr.in
""") % (python, python, python, python, python, python, python, python))

test.pass_test()
