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
import stat

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

try:
    import zipfile
except ImportError:
    x = "Python version has no 'ziplib' module; skipping tests.\n"
    test.skip_test(x)

def zipfile_contains(zipfilename, names):
    """Returns True if zipfilename contains all the names, False otherwise."""
    zf=zipfile.ZipFile(zipfilename, 'r')
    if type(names)==type(''):
        names=[names]
    for name in names:
        try:
            info=zf.getinfo(name)
        except KeyError as e:     # name not found
            zf.close()
            return False
    return True

def zipfile_files(fname):
    """Returns all the filenames in zip file fname."""
    zf = zipfile.ZipFile(fname, 'r')
    return [x.filename for x in zf.infolist()]

test.subdir('sub1')

test.write('SConstruct', """
env = Environment(tools = ['zip'])
env.Zip(target = 'aaa.zip', source = ['file1', 'file2'])
env.Zip(target = 'aaa.zip', source = 'file3')
env.Zip(target = 'bbb', source = 'sub1')
env.Zip(target = 'bbb', source = 'file4')
""" % locals())

test.write('file1', "file1\n")
test.write('file2', "file2\n")
test.write('file3', "file3\n")
test.write('file4', "file4\n")

test.write(['sub1', 'file5'], "sub1/file5\n")
test.write(['sub1', 'file6'], "sub1/file6\n")

test.run(arguments = 'aaa.zip', stderr = None)

test.must_exist('aaa.zip')
test.fail_test(not zipfile_contains('aaa.zip', ['file1', 'file2', 'file3']))

test.run(arguments = 'bbb.zip', stderr = None)

test.must_exist('bbb.zip')
test.fail_test(not zipfile_contains('bbb.zip', ['sub1/file5', 'sub1/file6', 'file4']))

######

marker_out = test.workpath('marker.out').replace('\\', '\\\\')

test.write('SConstruct', """\
def marker(target, source, env):
    open(r'%s', 'wb').write(b"marker\\n")
f1 = Environment()
zipcom = f1.Dictionary('ZIPCOM')
if not isinstance(zipcom, list):
    zipcom = [zipcom]
f2 = Environment(ZIPCOM = [Action(marker)] + zipcom)
f3 = Environment(ZIPSUFFIX = '.xyzzy')
f1.Zip(target = 'f1.zip', source = ['file10', 'file11'])
f1.Zip(target = 'f1.zip', source = 'file12')
f2.Zip(target = 'f2.zip', source = ['file13', 'file14'])
f2.Zip(target = 'f2.zip', source = 'file15')
f3.Zip(target = 'f3', source = 'file16')
f3.Zip(target = 'f3', source = ['file17', 'file18'])

import zipfile
sources = ['file10', 'file11', 'file12', 'file13', 'file14', 'file15']
f1.Zip(target = 'f4.zip', source = sources)
f1.Zip(target = 'f4stored.zip', source = sources,
       ZIPCOMPRESSION = zipfile.ZIP_STORED)
f1.Zip(target = 'f4deflated.zip', source = sources,
       ZIPCOMPRESSION = zipfile.ZIP_DEFLATED)
""" % marker_out)

for f in ['file10', 'file11', 'file12',
          'file13', 'file14', 'file15',
          'file16', 'file17', 'file18']:
    test.write(f, (f + "\n").encode())

test.run(arguments = 'f1.zip', stderr = None)

test.must_not_exist(test.workpath('marker.out'))

test.must_exist(test.workpath('f1.zip'))

test.run(arguments = 'f2.zip', stderr = None)

test.must_match('marker.out', 'marker\n')

test.must_exist(test.workpath('f2.zip'))

test.run(arguments = '.', stderr = None)

test.must_not_exist(test.workpath('f3.zip'))
test.must_exist(test.workpath('f3.xyzzy'))

test.fail_test(zipfile_files("f1.zip") != ['file10', 'file11', 'file12'])

test.fail_test(zipfile_files("f2.zip") != ['file13', 'file14', 'file15'])

test.fail_test(zipfile_files("f3.xyzzy") != ['file16', 'file17', 'file18'])

f4_size = os.stat('f4.zip')[stat.ST_SIZE]
f4stored_size = os.stat('f4stored.zip')[stat.ST_SIZE]
f4deflated_size = os.stat('f4deflated.zip')[stat.ST_SIZE]

test.fail_test(f4_size != f4deflated_size)
test.fail_test(f4stored_size == f4deflated_size)

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
