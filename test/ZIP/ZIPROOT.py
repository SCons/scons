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

import zipfile

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
test.subdir(['sub1', 'sub2'])

test.write('SConstruct', """
env = Environment(tools = ['zip'])
env.Zip(target = 'aaa.zip', source = ['sub1/file1'], ZIPROOT='sub1')
env.Zip(target = 'bbb.zip', source = ['sub1/file2', 'sub1/sub2/file2'], ZIPROOT='sub1')
""" % locals())

test.write(['sub1', 'file1'], "file1\n")
test.write(['sub1', 'file2'], "file2a\n")
test.write(['sub1', 'sub2', 'file2'], "file2b\n")

test.run(arguments = 'aaa.zip', stderr = None)

test.must_exist('aaa.zip')

# TEST: Zip file should contain 'file1', not 'sub1/file1', because of ZIPROOT.
zf=zipfile.ZipFile('aaa.zip', 'r')
test.fail_test(zf.testzip() is not None)
zf.close()

files=zipfile_files('aaa.zip')
test.fail_test(zipfile_files('aaa.zip') != ['file1'],
               message='Zip file aaa.zip has wrong files: %s'%repr(files))

###

test.run(arguments = 'bbb.zip', stderr = None)

test.must_exist('bbb.zip')

# TEST: Zip file should contain 'sub2/file2', not 'sub1/sub2/file2', because of ZIPROOT.
zf=zipfile.ZipFile('bbb.zip', 'r')
test.fail_test(zf.testzip() is not None)
zf.close()

files=zipfile_files('bbb.zip')
test.fail_test(zipfile_files('bbb.zip') != ['file2', 'sub2/file2'],
               message='Zip file bbb.zip has wrong files: %s'%repr(files))


test.pass_test()
