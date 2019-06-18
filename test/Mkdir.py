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
Verify that the Mkdir() Action works.
"""

import os.path

import TestSCons

test = TestSCons.TestSCons()

test.subdir('work1', 'work2', 'work3')

test.write(['work1', 'SConstruct'], """
Execute(Mkdir('d1'))
Execute(Mkdir(Dir('#d1-Dir')))
def cat(env, source, target):
    target = str(target[0])
    with open(target, "wb") as f:
        for src in source:
            with open(str(src), "rb") as ifp:
                f.write(ifp.read())
Cat = Action(cat)
env = Environment()
env.Command('f2.out', 'f2.in', [Cat, Mkdir("d3")])
env = Environment(DIR = 'd4')
env.Command('f5.out', 'f5.in', [Mkdir("$DIR"), Cat])
env.Command('f6.out', 'f6.in', [Cat,
                                Mkdir("Mkdir-$SOURCE"),
                                Mkdir("$TARGET-Mkdir")])
# Make sure that a user-defined Mkdir builder on a directory
# doesn't get executed twice if it has to get called to create
# directory for another target.
env.Command(Dir('hello'), None, [Mkdir('$TARGET')])
env.Command('hello/world', None, [Touch('$TARGET')])

# Make sure Mkdir works with a list of arguments
Execute(Mkdir(['d7', Dir('d8')]))
""")

test.write(['work1', 'f2.in'], "f2.in\n")
test.write(['work1', 'f5.in'], "f5.in\n")
test.write(['work1', 'f6.in'], "f6.in\n")

expect = test.wrap_stdout(read_str = """\
Mkdir("d1")
Mkdir("d1-Dir")
Mkdir(["d7", "d8"])
""",
                          build_str = """\
cat(["f2.out"], ["f2.in"])
Mkdir("d3")
Mkdir("d4")
cat(["f5.out"], ["f5.in"])
cat(["f6.out"], ["f6.in"])
Mkdir("Mkdir-f6.in")
Mkdir("f6.out-Mkdir")
Mkdir("hello")
Touch("%s")
""" % (os.path.join('hello', 'world')))
test.run(chdir = 'work1', options = '-n', arguments = '.', stdout = expect)

test.must_not_exist(['work1', 'd1'])
test.must_not_exist(['work1', 'd1-Dir'])
test.must_not_exist(['work1', 'f2.out'])
test.must_not_exist(['work1', 'd3'])
test.must_not_exist(['work1', 'd4'])
test.must_not_exist(['work1', 'f5.out'])
test.must_not_exist(['work1', 'f6.out'])
test.must_not_exist(['work1', 'Mkdir-f6.in'])
test.must_not_exist(['work1', 'f6.out-Mkdir'])
test.must_not_exist(['work1', 'd7'])
test.must_not_exist(['work1', 'd8'])

test.run(chdir = 'work1')

test.must_exist(['work1', 'd1'])
test.must_exist(['work1', 'd1-Dir'])
test.must_match(['work1', 'f2.out'], "f2.in\n")
test.must_exist(['work1', 'd3'])
test.must_exist(['work1', 'd4'])
test.must_match(['work1', 'f5.out'], "f5.in\n")
test.must_exist(['work1', 'f6.out'])
test.must_exist(['work1', 'Mkdir-f6.in'])
test.must_exist(['work1', 'f6.out-Mkdir'])
test.must_exist(['work1', 'hello'])
test.must_exist(['work1', 'hello/world'])
test.must_exist(['work1', 'd7'])
test.must_exist(['work1', 'd8'])

test.write(['work1', 'd1', 'file'], "d1/file\n")
test.write(['work1', 'd3', 'file'], "d3/file\n")
test.write(['work1', 'Mkdir-f6.in', 'file'], "Mkdir-f6.in/file\n")
test.write(['work1', 'f6.out-Mkdir', 'file'], "f6.out-Mkdir/file\n")
test.write(['work1', 'hello', 'file'], "hello/file\n")




test.write(['work2', 'SConstruct'], """\
import os
def catdir(env, source, target):
    target = str(target[0])
    with open(target, "wb") as outfp:
        for src in source:
            s = str(src)
            for f in sorted(os.listdir(s)):
                f = os.path.join(s, f)
                if os.path.isfile(f):
                    with open(f, "rb") as infp:
                        outfp.write(infp.read())
CatDir = Builder(action = catdir)
env = Environment(BUILDERS = {'CatDir' : CatDir})
env.Command(Dir('hello'), None, [Mkdir('$TARGET')])
env.Command('hello/file1.out', 'file1.in', [Copy('$TARGET', '$SOURCE')])
env.Command('hello/file2.out', 'file2.in', [Copy('$TARGET', '$SOURCE')])
env.CatDir('output', Dir('hello'))
""")

test.write(['work2', 'file1.in'], "work2/file1.in\n")
test.write(['work2', 'file2.in'], "work2/file2.in\n")

test.run(chdir = 'work2', arguments = 'hello/file2.out output')

test.must_match(['work2', 'output'], "work2/file1.in\nwork2/file2.in\n")


#----------------------------------------
# Regression test for bug #1249

test.subdir(['work3', 'sub1'], ['work3', 'sub1', 'sub11'])

test.write(['work3', 'SConstruct'], """\
#/SConstruct ------------------------------------------
import os
env = Environment(ENV = os.environ)
VariantDir('build', 'sub1', duplicate=0)
base = '#build/sub1'
Export('env base')
SConscript('sub1/SConscript', exports='env')
""")

test.write(['work3', 'sub1', 'SConscript'], """\
#/sub1/SConscript ----------------------------------
Import ('env base')
test1 = base + '/test1'
Export ('env test1')
env.Command(Dir(test1), '', Mkdir('$TARGET'))
SConscript('sub11/SConscript')
""")

test.write(['work3', 'sub1', 'sub11', 'SConscript'], """\
#/sub1/sub11/SConscript-------------------------
Import('env test1')
test11 = test1 + '/test11'
print('test11 = ' + test11)
env.Command(Dir(test11), '', Mkdir('$TARGET'))
""")

test.run(chdir = 'work3', arguments = '')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
