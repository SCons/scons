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


import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

import zipfile


def zipfile_get_file_datetime(zipfilename, fname):
    """Returns the date_time of the given file with the archive."""
    with zipfile.ZipFile(zipfilename, 'r') as zf:
        for info in zf.infolist():
            if info.filename == fname:
                return info.date_time
    
    raise Exception("Unable to find %s" % fname)


test.write('SConstruct', """
env = Environment(tools = ['zip'])
env.Zip(target = 'aaa.zip', source = ['file1'], ZIP_OVERRIDE_TIMESTAMP=(1983,3,11,1,2,2))
""" % locals())

test.write(['file1'], "file1\n")

test.run(arguments = 'aaa.zip', stderr = None)

test.must_exist('aaa.zip')

with zipfile.ZipFile('aaa.zip', 'r') as zf:
    test.fail_test(zf.testzip() is not None)

files = test.zipfile_files('aaa.zip')
test.fail_test(files != ['file1'],
               message='Zip file aaa.zip has wrong files: %s' % repr(files))

date_time = zipfile_get_file_datetime('aaa.zip', 'file1')
test.fail_test(date_time != (1983, 3, 11, 1, 2, 2),
               message="Zip file aaa.zip#file1 has wrong date_time: %s" % repr(date_time))

test.pass_test()
