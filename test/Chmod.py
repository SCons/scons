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
Verify that the Chmod() Action works.
"""

import os
import stat

import TestSCons

test = TestSCons.TestSCons()

# Note:  Windows basically has two modes that it can os.chmod() files to
# 0o444 and 0o666, and directories to 0o555 and 0o777, so we can only really
# oscillate between those values.
test.write('SConstruct', """
Execute(Chmod('f1', 0o666))
Execute(Chmod(('f1-File'), 0o666))
Execute(Chmod('d2', 0o777))
Execute(Chmod(Dir('d2-Dir'), 0o777))
def cat(env, source, target):
    target = str(target[0])
    with open(target, "wb") as f:
        for src in source:
            with open(str(src), "rb") as infp:
                f.write(infp.read())
Cat = Action(cat)
env = Environment()
env.Command('bar.out', 'bar.in', [Cat,
                                  Chmod("f3", 0o666),
                                  Chmod("d4", 0o777)])
env = Environment(FILE = 'f5')
env.Command('f6.out', 'f6.in', [Chmod('$FILE', 0o666), Cat])
env.Command('f7.out', 'f7.in', [Cat,
                                Chmod('Chmod-$SOURCE', 0o666),
                                Chmod('${TARGET}-Chmod', 0o666)])

# Make sure Chmod works with a list of arguments
env = Environment(FILE = 'f9')
env.Command('f8.out', 'f8.in', [Chmod(['$FILE', File('f10')], 0o666), Cat])
Execute(Chmod(['d11', Dir('d12')], 0o777))
Execute(Chmod('f13', "a=r"))
Execute(Chmod('f14', "ogu+w"))
Execute(Chmod('f15', "ug=rw, go+ rw"))
Execute(Chmod('d16', "0777"))
Execute(Chmod(['d17', 'd18'], "ogu = rwx"))
""")

test.write('f1', "f1\n")
test.write('f1-File', "f1-File\n")
test.subdir('d2')
test.write(['d2', 'file'], "d2/file\n")
test.subdir('d2-Dir')
test.write(['d2-Dir', 'file'], "d2-Dir/file\n")
test.write('bar.in', "bar.in\n")
test.write('f3', "f3\n")
test.subdir('d4')
test.write(['d4', 'file'], "d4/file\n")
test.write('f5', "f5\n")
test.write('f6.in', "f6.in\n")
test.write('f7.in', "f7.in\n")
test.write('Chmod-f7.in', "Chmod-f7.in\n")
test.write('f7.out-Chmod', "f7.out-Chmod\n")
test.write('f8.in', "f8.in\n")
test.write('f9', "f9\n")
test.write('f10', "f10\n")
test.subdir('d11')
test.subdir('d12')
test.write('f13', "f13\n")
test.write('f14', "f14\n")
test.write('f15', "f15\n")
test.subdir('d16')
test.subdir('d17')
test.subdir('d18')

os.chmod(test.workpath('f1'), 0o444)
os.chmod(test.workpath('f1-File'), 0o444)
os.chmod(test.workpath('d2'), 0o555)
os.chmod(test.workpath('d2-Dir'), 0o555)
os.chmod(test.workpath('f3'), 0o444)
os.chmod(test.workpath('d4'), 0o555)
os.chmod(test.workpath('f5'), 0o444)
os.chmod(test.workpath('Chmod-f7.in'), 0o444)
os.chmod(test.workpath('f7.out-Chmod'), 0o444)
os.chmod(test.workpath('f9'), 0o444)
os.chmod(test.workpath('f10'), 0o444)
os.chmod(test.workpath('d11'), 0o555)
os.chmod(test.workpath('d12'), 0o555)
os.chmod(test.workpath('f13'), 0o444)
os.chmod(test.workpath('f14'), 0o444)
os.chmod(test.workpath('f15'), 0o444)
os.chmod(test.workpath('d16'), 0o555)
os.chmod(test.workpath('d17'), 0o555)
os.chmod(test.workpath('d18'), 0o555)
expect = test.wrap_stdout(read_str = """\
Chmod("f1", 0666)
Chmod("f1-File", 0666)
Chmod("d2", 0777)
Chmod("d2-Dir", 0777)
Chmod(["d11", "d12"], 0777)
Chmod("f13", "a=r")
Chmod("f14", "ogu+w")
Chmod("f15", "ug=rw, go+ rw")
Chmod("d16", "0777")
Chmod(["d17", "d18"], "ogu = rwx")
""",
                          build_str = """\
cat(["bar.out"], ["bar.in"])
Chmod("f3", 0666)
Chmod("d4", 0777)
Chmod("f5", 0666)
cat(["f6.out"], ["f6.in"])
cat(["f7.out"], ["f7.in"])
Chmod("Chmod-f7.in", 0666)
Chmod("f7.out-Chmod", 0666)
Chmod(["f9", "f10"], 0666)
cat(["f8.out"], ["f8.in"])
""")
test.run(options = '-n', arguments = '.', stdout = expect)

s = stat.S_IMODE(os.stat(test.workpath('f1'))[stat.ST_MODE])
test.fail_test(s != 0o444)
s = stat.S_IMODE(os.stat(test.workpath('f1-File'))[stat.ST_MODE])
test.fail_test(s != 0o444)
s = stat.S_IMODE(os.stat(test.workpath('d2'))[stat.ST_MODE])
test.fail_test(s != 0o555)
s = stat.S_IMODE(os.stat(test.workpath('d2-Dir'))[stat.ST_MODE])
test.fail_test(s != 0o555)
test.must_not_exist('bar.out')
s = stat.S_IMODE(os.stat(test.workpath('f3'))[stat.ST_MODE])
test.fail_test(s != 0o444)
s = stat.S_IMODE(os.stat(test.workpath('d4'))[stat.ST_MODE])
test.fail_test(s != 0o555)
s = stat.S_IMODE(os.stat(test.workpath('f5'))[stat.ST_MODE])
test.fail_test(s != 0o444)
test.must_not_exist('f6.out')
test.must_not_exist('f7.out')
s = stat.S_IMODE(os.stat(test.workpath('Chmod-f7.in'))[stat.ST_MODE])
test.fail_test(s != 0o444)
s = stat.S_IMODE(os.stat(test.workpath('f7.out-Chmod'))[stat.ST_MODE])
test.fail_test(s != 0o444)
test.must_not_exist('f8.out')
s = stat.S_IMODE(os.stat(test.workpath('f9'))[stat.ST_MODE])
test.fail_test(s != 0o444)
s = stat.S_IMODE(os.stat(test.workpath('f10'))[stat.ST_MODE])
test.fail_test(s != 0o444)
s = stat.S_IMODE(os.stat(test.workpath('d11'))[stat.ST_MODE])
test.fail_test(s != 0o555)
s = stat.S_IMODE(os.stat(test.workpath('d12'))[stat.ST_MODE])
test.fail_test(s != 0o555)
s = stat.S_IMODE(os.stat(test.workpath('f13'))[stat.ST_MODE])
test.fail_test(s != 0o444)
s = stat.S_IMODE(os.stat(test.workpath('f14'))[stat.ST_MODE])
test.fail_test(s != 0o444)
s = stat.S_IMODE(os.stat(test.workpath('f15'))[stat.ST_MODE])
test.fail_test(s != 0o444)
s = stat.S_IMODE(os.stat(test.workpath('d16'))[stat.ST_MODE])
test.fail_test(s != 0o555)
s = stat.S_IMODE(os.stat(test.workpath('d17'))[stat.ST_MODE])
test.fail_test(s != 0o555)
s = stat.S_IMODE(os.stat(test.workpath('d18'))[stat.ST_MODE])
test.fail_test(s != 0o555)

test.run()

s = stat.S_IMODE(os.stat(test.workpath('f1'))[stat.ST_MODE])
test.fail_test(s != 0o666)
s = stat.S_IMODE(os.stat(test.workpath('f1-File'))[stat.ST_MODE])
test.fail_test(s != 0o666)
s = stat.S_IMODE(os.stat(test.workpath('d2'))[stat.ST_MODE])
test.fail_test(s != 0o777)
s = stat.S_IMODE(os.stat(test.workpath('d2-Dir'))[stat.ST_MODE])
test.fail_test(s != 0o777)
test.must_match('bar.out', "bar.in\n")
s = stat.S_IMODE(os.stat(test.workpath('f3'))[stat.ST_MODE])
test.fail_test(s != 0o666)
s = stat.S_IMODE(os.stat(test.workpath('d4'))[stat.ST_MODE])
test.fail_test(s != 0o777)
s = stat.S_IMODE(os.stat(test.workpath('f5'))[stat.ST_MODE])
test.fail_test(s != 0o666)
test.must_match('f6.out', "f6.in\n")
test.must_match('f7.out', "f7.in\n")
s = stat.S_IMODE(os.stat(test.workpath('Chmod-f7.in'))[stat.ST_MODE])
test.fail_test(s != 0o666)
s = stat.S_IMODE(os.stat(test.workpath('f7.out-Chmod'))[stat.ST_MODE])
test.fail_test(s != 0o666)
test.must_match('f8.out', "f8.in\n")
s = stat.S_IMODE(os.stat(test.workpath('f9'))[stat.ST_MODE])
test.fail_test(s != 0o666)
s = stat.S_IMODE(os.stat(test.workpath('f10'))[stat.ST_MODE])
test.fail_test(s != 0o666)
s = stat.S_IMODE(os.stat(test.workpath('d11'))[stat.ST_MODE])
test.fail_test(s != 0o777)
s = stat.S_IMODE(os.stat(test.workpath('d12'))[stat.ST_MODE])
test.fail_test(s != 0o777)
s = stat.S_IMODE(os.stat(test.workpath('f13'))[stat.ST_MODE])
test.fail_test(s != 0o444)
s = stat.S_IMODE(os.stat(test.workpath('f14'))[stat.ST_MODE])
test.fail_test(s != 0o666)
s = stat.S_IMODE(os.stat(test.workpath('f15'))[stat.ST_MODE])
test.fail_test(s != 0o666)
s = stat.S_IMODE(os.stat(test.workpath('d16'))[stat.ST_MODE])
test.fail_test(s != 0o777)
s = stat.S_IMODE(os.stat(test.workpath('d17'))[stat.ST_MODE])
test.fail_test(s != 0o777)
s = stat.S_IMODE(os.stat(test.workpath('d18'))[stat.ST_MODE])
test.fail_test(s != 0o777)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
