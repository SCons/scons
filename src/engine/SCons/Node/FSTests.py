#
# Copyright (c) 2001 Steven Knight
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
import sys
import unittest

import SCons.Node.FS



built_it = None

class Builder:
    def execute(self, **kw):
        global built_it
        built_it = 1
        return 0

class Environment:
    def Dictionary(self, *args):
	pass



class FSTestCase(unittest.TestCase):
    def runTest(self):
        """Test FS (file system) Node operations
        
        This test case handles all of the file system node
        tests in one environment, so we don't have to set up a
        complicated directory structure for each test individually.
        """
        from TestCmd import TestCmd

        test = TestCmd(workdir = '')
        test.subdir('sub', ['sub', 'dir'])

        wp = test.workpath('')
        sub = test.workpath('sub', '')
        sub_dir = test.workpath('sub', 'dir', '')
        sub_dir_foo = test.workpath('sub', 'dir', 'foo', '')
        sub_dir_foo_bar = test.workpath('sub', 'dir', 'foo', 'bar', '')
        sub_foo = test.workpath('sub', 'foo', '')

        os.chdir(sub_dir)

        fs = SCons.Node.FS.FS()

        def Dir_test(lpath, path, abspath, up_path, fileSys=fs):
            dir = fileSys.Dir(lpath)
            assert dir.path == path, "Dir.path %s != expected path %s" % \
                   (dir.path, path)
            assert str(dir) == path, "str(dir) %s != expected path %s" % \
                   (str(dir), path)
            assert dir.abspath == abspath, "Dir.abspath %s != expected abs. path %s" % \
                   (dir.abspath, path)
            assert dir.up().path == up_path, "Dir.up().path %s != expected parent path %s" % \
                   (dir.up().path, up_path)

        Dir_test('foo',         'foo/',         sub_dir_foo,            '.')
        Dir_test('foo/bar',     'foo/bar/',     sub_dir_foo_bar,        'foo/')
        Dir_test('/foo',        '/foo/',        '/foo/',                '/')
        Dir_test('/foo/bar',    '/foo/bar/',    '/foo/bar/',            '/foo/')
        Dir_test('..',          sub,            sub,                    wp)
        Dir_test('foo/..',      '.',            sub_dir,                sub)
        Dir_test('../foo',      sub_foo,        sub_foo,                sub)
        Dir_test('.',           '.',            sub_dir,                sub)
        Dir_test('./.',         '.',            sub_dir,                sub)
        Dir_test('foo/./bar',   'foo/bar/',     sub_dir_foo_bar,        'foo/')

        d1 = fs.Dir('d1')

        f1 = fs.File('f1', directory = d1)

        assert f1.path == 'd1/f1', "f1.path %s != d1/f1" % f1.path
        assert str(f1) == 'd1/f1', "str(f1) %s != d1/f1" % str(f1)

        try:
            f2 = fs.File('f1/f2', directory = d1)
        except TypeError, x:
	    assert str(x) == "Tried to lookup File 'd1/f1' as a Dir.", x
        except:
            raise

        try:
            dir = fs.Dir('d1/f1')
        except TypeError, x:
	    assert str(x) == "Tried to lookup File 'd1/f1' as a Dir.", x
        except:
            raise

	try:
	    f2 = fs.File('d1')
	except TypeError, x:
	    assert str(x) == "Tried to lookup Dir 'd1/' as a File.", x
	except:
	    raise

	# Test Dir.children()
	dir = fs.Dir('ddd')
	fs.File('ddd/f1')
	fs.File('ddd/f2')
	fs.File('ddd/f3')
	fs.Dir('ddd/d1')
	fs.Dir('ddd/d1/f4')
	fs.Dir('ddd/d1/f5')
	kids = map(lambda x: x.path, dir.children())
	kids.sort()
	assert kids == ['ddd/d1/', 'ddd/f1', 'ddd/f2', 'ddd/f3']

        # Test for sub-classing of node building.
        global built_it

        built_it = None
        assert not built_it
        d1.add_source(["d"])    # XXX FAKE SUBCLASS ATTRIBUTE
        d1.builder_set(Builder())
        d1.env_set(Environment())
        d1.build()
        assert built_it

        built_it = None
        assert not built_it
        f1.add_source(["f"])    # XXX FAKE SUBCLASS ATTRIBUTE
        f1.builder_set(Builder())
        f1.env_set(Environment())
        f1.build()
        assert built_it

	e1 = fs.Entry("d1")
	assert e1.__class__.__name__ == 'Dir'
	assert e1.path == "d1/", e1.path

	e2 = fs.Entry("d1/f1")
	assert e2.__class__.__name__ == 'File'
	assert e2.path == "d1/f1", e2.path

	e3 = fs.Entry("e3")
	assert e3.__class__.__name__ == 'Entry'
	assert e3.path == "e3", e3.path

	e4 = fs.Entry("d1/e4")
	assert e4.__class__.__name__ == 'Entry'
	assert e4.path == "d1/e4", e4.path

	e5 = fs.Entry("e3/e5")
	assert e3.__class__.__name__ == 'Dir'
	assert e3.path == "e3/", e3.path
	assert e5.__class__.__name__ == 'Entry'
	assert e5.path == "e3/e5", e5.path

	e6 = fs.Dir("d1/e4")
	assert e6 is e4
	assert e4.__class__.__name__ == 'Dir'
	assert e4.path == "d1/e4/", e4.path

	e7 = fs.File("e3/e5")
	assert e7 is e5
	assert e5.__class__.__name__ == 'File'
	assert e5.path == "e3/e5", e5.path



if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(FSTestCase())
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
        sys.exit(1)
