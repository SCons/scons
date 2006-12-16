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
Verify the ability to "check out" an SCons delta from a fake
Aegis utility.
"""

import re

import TestSCons_time

test = TestSCons_time.TestSCons_time()

test.write_sample_project('foo.tar')

my_aegis_py = test.write_fake_aegis_py('my_aegis.py')

test.write('config', """\
aegis = r'%(my_aegis_py)s'
""" % locals())

test.run(arguments = 'run -f config --aegis xyzzy.0.1 --number 321,329 foo.tar')

test.must_exist('foo-321-0.log',
                'foo-321-0.prof',
                'foo-321-1.log',
                'foo-321-1.prof',
                'foo-321-2.log',
                'foo-321-2.prof')

test.must_exist('foo-329-0.log',
                'foo-329-0.prof',
                'foo-329-1.log',
                'foo-329-1.prof',
                'foo-329-2.log',
                'foo-329-2.prof')

def tempdir_re(*args):
    import os
    import os.path
    import string
    import tempfile

    sep = re.escape(os.sep)
    args = (tempfile.gettempdir(), 'scons-time-aegis-',) + args
    x = apply(os.path.join, args)
    x = re.escape(x)
    x = string.replace(x, 'aegis\\-', 'aegis\\-[^%s]*' % sep)
    return x

expect = [
    tempdir_re('src', 'script', 'scons.py'),
    'SCONS_LIB_DIR = %s' % tempdir_re('src', 'engine'),
]

content = test.read(test.workpath('foo-321-2.log'))

test.must_contain_all_lines('foo-617-2.log', content, expect, re.search)

test.pass_test()
