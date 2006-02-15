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

import os
import os.path
import stat
import string
import sys
import TestSCons

python = TestSCons.python

test = TestSCons.TestSCons()

try:
    import zipfile
except ImportError:
    zip = test.where_is('zip')
    if not zip:
        x = "Python version has no 'ziplib' module nor 'zip' utility; skipping tests.\n"
        test.skip_test(x)

test.subdir('sub1')

test.write('myzip.py', r"""\
import os
import os.path
import sys
def process(outfile, name):
    if os.path.isdir(name):
        list = os.listdir(name)
        list.sort()
        for entry in list:
            process(outfile, os.path.join(name, entry))
    else:
        outfile.write(open(name, 'rb').read())
outfile = open(sys.argv[1], 'wb')
for infile in sys.argv[2:]:
    process(outfile, infile)
outfile.close()
sys.exit(0)
""")

test.write('SConstruct', """
env = Environment(tools = ['zip'],
                  ZIPCOM = r'%s myzip.py $TARGET $SOURCES')
env.Zip(target = 'aaa.zip', source = ['file1', 'file2'])
env.Zip(target = 'aaa.zip', source = 'file3')
env.Zip(target = 'bbb', source = 'sub1')
env.Zip(target = 'bbb', source = 'file4')
""" % python)

test.write('file1', "file1\n")
test.write('file2', "file2\n")
test.write('file3', "file3\n")
test.write('file4', "file4\n")

test.write(['sub1', 'file5'], "sub1/file5\n")
test.write(['sub1', 'file6'], "sub1/file6\n")

test.run(arguments = 'aaa.zip', stderr = None)

test.fail_test(test.read('aaa.zip') != "file1\nfile2\nfile3\n")

test.run(arguments = 'bbb.zip', stderr = None)

test.fail_test(test.read('bbb.zip') != "sub1/file5\nsub1/file6\nfile4\n")

try:
    import zipfile
    internal_zip = 1
    zip = 1

    def files(fname):
        zf = zipfile.ZipFile(fname, 'r')
        return map(lambda x: x.filename, zf.infolist())

except ImportError:
    internal_zip = 0
    zip = test.detect('ZIP', 'zip')
    unzip = test.where_is('unzip')

    def files(fname, test=test, unzip=unzip):
        test.run(program = unzip, arguments = "-l -qq %s" % fname)
        lines = string.split(test.stdout(), "\n")[:-1]
        def lastword(line):
            return string.split(line)[-1]
        return map(lastword, lines)

if zip:

    marker_out = string.replace(test.workpath('marker.out'), '\\', '\\\\')

    test.write('SConstruct', """\
def marker(target, source, env):
    open(r'%s', 'wb').write("marker\\n")
import types
f1 = Environment()
zipcom = f1.Dictionary('ZIPCOM')
if not type(zipcom) is types.ListType:
    zipcom = [zipcom]
f2 = Environment(ZIPCOM = [Action(marker)] + zipcom)
f3 = Environment(ZIPSUFFIX = '.xyzzy')
f1.Zip(target = 'f1.zip', source = ['file10', 'file11'])
f1.Zip(target = 'f1.zip', source = 'file12')
f2.Zip(target = 'f2.zip', source = ['file13', 'file14'])
f2.Zip(target = 'f2.zip', source = 'file15')
f3.Zip(target = 'f3', source = 'file16')
f3.Zip(target = 'f3', source = ['file17', 'file18'])
try:
    import zipfile
    sources = ['file10', 'file11', 'file12', 'file13', 'file14', 'file15']
    f1.Zip(target = 'f4.zip', source = sources)
    f1.Zip(target = 'f4stored.zip', source = sources,
           ZIPCOMPRESSION = zipfile.ZIP_STORED)
    f1.Zip(target = 'f4deflated.zip', source = sources,
           ZIPCOMPRESSION = zipfile.ZIP_DEFLATED)
except ImportError:
    pass
""" % marker_out)

    for f in ['file10', 'file11', 'file12',
              'file13', 'file14', 'file15',
              'file16', 'file17', 'file18']:
        test.write(f, f + "\n")

    test.run(arguments = 'f1.zip', stderr = None)

    test.fail_test(os.path.exists(test.workpath('marker.out')))

    test.fail_test(not os.path.exists(test.workpath('f1.zip')))

    test.run(arguments = 'f2.zip', stderr = None)

    test.fail_test(test.read('marker.out') != 'marker\n')

    test.fail_test(not os.path.exists(test.workpath('f2.zip')))

    test.run(arguments = '.', stderr = None)

    test.fail_test(os.path.exists(test.workpath('f3.zip')))
    test.fail_test(not os.path.exists(test.workpath('f3.xyzzy')))

    test.fail_test(files("f1.zip") != ['file10', 'file11', 'file12'])

    test.fail_test(files("f2.zip") != ['file13', 'file14', 'file15'])

    test.fail_test(files("f3.xyzzy") != ['file16', 'file17', 'file18'])

    if internal_zip:
        f4_size = os.stat('f4.zip')[stat.ST_SIZE]
        f4stored_size = os.stat('f4stored.zip')[stat.ST_SIZE]
        f4deflated_size = os.stat('f4deflated.zip')[stat.ST_SIZE]

        test.fail_test(f4_size != f4deflated_size)
        test.fail_test(f4stored_size == f4deflated_size)

test.pass_test()
