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

import os

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.subdir('sub1')

test.write('mytar.py', r"""
import getopt
import os
import os.path
import sys
opts, args = getopt.getopt(sys.argv[1:], 'cf:')
for opt, arg in opts:
    if opt == '-f': out = arg

def process(outfile, name):
    if os.path.isdir(name):
        for entry in sorted(os.listdir(name)):
            process(outfile, os.path.join(name, entry))
    else:
        with open(name, 'r') as ifp:
            outfile.write(ifp.read())

with open(out, 'w') as ofp:
    for infile in args:
        process(ofp, infile)
sys.exit(0)
""")

test.write('SConstruct', """
DefaultEnvironment(tools=[])  # test speedup
env = Environment(tools = ['tar'], TAR = r'%(_python_)s mytar.py')
env.Tar(target = 'aaa.tar', source = ['file1', 'file2'])
env.Tar(target = 'aaa.tar', source = 'file3')
env.Tar(target = 'bbb', source = 'sub1')
env.Tar(target = 'bbb', source = 'file4')
""" % locals())

test.write('file1', "file1\n")
test.write('file2', "file2\n")
test.write('file3', "file3\n")
test.write('file4', "file4\n")

test.write(['sub1', 'file5'], "sub1/file5\n")
test.write(['sub1', 'file6'], "sub1/file6\n")

test.run(arguments = 'aaa.tar', stderr = None)

test.must_match('aaa.tar', "file1\nfile2\nfile3\n", mode='r')

test.run(arguments = 'bbb.tar', stderr = None)

test.must_match('bbb.tar', "sub1/file5\nsub1/file6\nfile4\n", mode='r')


tar = test.detect('TAR', 'tar')

if tar:

    test.file_fixture('wrapper.py')

    test.write('SConstruct', """
DefaultEnvironment(tools=[])  # test speedup
foo = Environment()
tar = foo.Dictionary('TAR')
bar = Environment(TAR = r'%(_python_)s wrapper.py ' + tar)
f3 = Environment(TARFLAGS = '-c -z', TARSUFFIX = '.tar.gz')
f4 = Environment(TARFLAGS = '-c -z', TARSUFFIX = '.tgz')
f5 = Environment(TARFLAGS = '-c -z')
foo.Tar(target = 'foo.tar', source = ['file10', 'file11'])
foo.Tar(target = 'foo.tar', source = 'file12')
bar.Tar(target = 'bar.tar', source = ['file13', 'file14'])
bar.Tar(target = 'bar.tar', source = 'file15')
f3.Tar(target = 'f3', source = 'file16')
f3.Tar(target = 'f3', source = ['file17', 'file18'])
f4.Tar(target = 'f4', source = 'file19')
f4.Tar(target = 'f4', source = ['file20', 'file21'])
f5.Tar(target = 'f5.tgz', source = 'file22')
f5.Tar(target = 'f5.tgz', source = ['file23', 'file24'])
""" % locals())

    for f in ['file10', 'file11', 'file12',
              'file13', 'file14', 'file15',
              'file16', 'file17', 'file18',
              'file19', 'file20', 'file21',
              'file22', 'file23', 'file24']:
        test.write(f, f + "\n")

    test.run(arguments = 'foo.tar', stderr = None)

    test.fail_test(os.path.exists(test.workpath('wrapper.out')))

    test.fail_test(not os.path.exists(test.workpath('foo.tar')))

    test.run(arguments = 'bar.tar', stderr = None)

    test.fail_test(not os.path.exists(test.workpath('wrapper.out')))

    test.fail_test(not os.path.exists(test.workpath('bar.tar')))

    test.run(arguments = '.', stderr = None)

    test.fail_test(os.path.exists(test.workpath('f3.tar')))
    test.fail_test(not os.path.exists(test.workpath('f3.tar.gz')))

    test.fail_test(os.path.exists(test.workpath('f4.tar')))
    test.fail_test(os.path.exists(test.workpath('f4.tar.gz')))
    test.fail_test(not os.path.exists(test.workpath('f4.tgz')))

    test.fail_test(os.path.exists(test.workpath('f5.tar')))
    test.fail_test(os.path.exists(test.workpath('f5.tar.gz')))
    test.fail_test(not os.path.exists(test.workpath('f5.tgz')))

    test.run(program = tar, arguments = "-t -f foo.tar", stderr = None)
    test.fail_test(test.stdout() != "file10\nfile11\nfile12\n")

    test.run(program = tar, arguments = "-t -f bar.tar", stderr = None)
    test.fail_test(test.stdout() != "file13\nfile14\nfile15\n")

    test.run(program = tar, arguments = "-t -z -f f3.tar.gz", stderr = None)
    test.fail_test(test.stdout() != "file16\nfile17\nfile18\n")

    test.run(program = tar, arguments = "-t -z -f f4.tgz", stderr = None)
    test.fail_test(test.stdout() != "file19\nfile20\nfile21\n")

    test.run(program = tar, arguments = "-t -z -f f5.tgz", stderr = None)
    test.fail_test(test.stdout() != "file22\nfile23\nfile24\n")

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
