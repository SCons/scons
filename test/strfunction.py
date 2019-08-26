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

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.write('cat.py', """\
import sys
with open(sys.argv[2], "wb") as f, open(sys.argv[1], "rb") as ifp:
    f.write(ifp.read())
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
    with open(t, 'w') as f, open(s, 'r') as ifp:
        f.write(ifp.read())
func1action = Action(func, strfunction)
func2action = Action(func, strfunction=strfunction)

cmd = r'%(_python_)s cat.py $SOURCE $TARGET'
cmd1action = Action(cmd, strfunction)
cmd2action = Action(cmd, strfunction=strfunction)

list = [ r'%(_python_)s cat.py $SOURCE .temp',
         r'%(_python_)s cat.py .temp $TARGET' ]
listaction = Action(list, strfunction=strfunction)

lazy = '$LAZY'
lazy1action = Action(lazy, strfunction)
lazy2action = Action(lazy, strfunction=strfunction)

targetaction = Action(func, '$TARGET')

dict = {
    '.cmd'      : cmd,
    '.cmdstr'   : cmd2action,
    '.func'     : func,
    '.funcstr'  : func2action,
    '.list'     : list,
    '.liststr'  : listaction,
    '.lazy'     : lazy,
    '.lazystr'  : lazy2action,
}

env = Environment(BUILDERS = {
                        'Cmd'           : Builder(action=cmd),
                        'Cmd1Str'       : Builder(action=cmd1action),
                        'Cmd2Str'       : Builder(action=cmd2action),
                        'Func'          : Builder(action=func),
                        'Func1Str'      : Builder(action=func1action),
                        'Func2Str'      : Builder(action=func2action),
                        'Lazy'          : Builder(action=lazy),
                        'Lazy1Str'      : Builder(action=lazy1action),
                        'Lazy2Str'      : Builder(action=lazy2action),
                        'List'          : Builder(action=list),
                        'ListStr'       : Builder(action=listaction),
                        'Target'        : Builder(action=targetaction),

                        'Dict'          : Builder(action=dict),
                  },
                  LAZY = r'%(_python_)s cat.py $SOURCE $TARGET')

env.Cmd('cmd.out', 'cmd.in')
env.Cmd1Str('cmd1str.out', 'cmdstr.in')
env.Cmd2Str('cmd2str.out', 'cmdstr.in')
env.Func('func.out', 'func.in')
env.Func1Str('func1str.out', 'funcstr.in')
env.Func2Str('func2str.out', 'funcstr.in')
env.Lazy('lazy.out', 'lazy.in')
env.Lazy1Str('lazy1str.out', 'lazystr.in')
env.Lazy2Str('lazy2str.out', 'lazystr.in')
env.List('list.out', 'list.in')
env.ListStr('liststr.out', 'liststr.in')
env.Target('target.out', 'target.in')

env.Dict('dict1.out', 'dict1.cmd')
env.Dict('dict2.out', 'dict2.cmdstr')
env.Dict('dict3.out', 'dict3.func')
env.Dict('dict4.out', 'dict4.funcstr')
env.Dict('dict5.out', 'dict5.lazy')
env.Dict('dict6.out', 'dict6.lazystr')
env.Dict('dict7.out', 'dict7.list')
env.Dict('dict8.out', 'dict8.liststr')
""" % locals())

test.write('func.in',           "func.in\n")
test.write('funcstr.in',        "funcstr.in\n")
test.write('cmd.in',            "cmd.in\n")
test.write('cmdstr.in',         "cmdstr.in\n")
test.write('lazy.in',           "lazy.in\n")
test.write('lazystr.in',        "lazystr.in\n")
test.write('list.in',           "list.in\n")
test.write('liststr.in',        "liststr.in\n")
test.write('target.in',         "target.in\n")

test.write('dict1.cmd',         "dict1.cmd\n")
test.write('dict2.cmdstr',      "dict2.cmdstr\n")
test.write('dict3.func',        "dict3.func\n")
test.write('dict4.funcstr',     "dict4.funcstr\n")
test.write('dict5.lazy',        "dict4.lazy\n")
test.write('dict6.lazystr',     "dict6.lazystr\n")
test.write('dict7.list',        "dict7.list\n")
test.write('dict8.liststr',     "dict8.liststr\n")

expect = test.wrap_stdout("""\
%(_python_)s cat.py cmd.in cmd.out
Building cmd1str.out from cmdstr.in
Building cmd2str.out from cmdstr.in
%(_python_)s cat.py dict1.cmd dict1.out
Building dict2.out from dict2.cmdstr
func(["dict3.out"], ["dict3.func"])
Building dict4.out from dict4.funcstr
%(_python_)s cat.py dict5.lazy dict5.out
Building dict6.out from dict6.lazystr
%(_python_)s cat.py dict7.list .temp
%(_python_)s cat.py .temp dict7.out
Building dict8.out from dict8.liststr
Building dict8.out from dict8.liststr
func(["func.out"], ["func.in"])
Building func1str.out from funcstr.in
Building func2str.out from funcstr.in
%(_python_)s cat.py lazy.in lazy.out
Building lazy1str.out from lazystr.in
Building lazy2str.out from lazystr.in
%(_python_)s cat.py list.in .temp
%(_python_)s cat.py .temp list.out
Building liststr.out from liststr.in
Building liststr.out from liststr.in
target.out
""" % locals())

test.run(arguments = '.', stdout=expect)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
