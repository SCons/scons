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
import string
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

        d1 = fs.Dir('d1')

        f1 = fs.File('f1', directory = d1)

        d1_f1 = os.path.join('d1', 'f1')
        assert f1.path == d1_f1, "f1.path %s != %s" % (f1.path, d1_f1)
        assert str(f1) == d1_f1, "str(f1) %s != %s" % (str(f1), d1_f1)

        seps = [os.sep]
        if os.sep != '/':
            seps = seps + ['/']

        for sep in seps:

            def Dir_test(lpath, path_, abspath_, up_path_, fileSys=fs, s=sep):
                dir = fileSys.Dir(string.replace(lpath, '/', s))

                def strip_slash(p):
                    if p[-1] == '/' and len(p) > 1:
                        p = p[:-1]
                    return p
                path = strip_slash(path_)
                abspath = strip_slash(abspath_)
                up_path = strip_slash(up_path_)
		name = string.split(abspath, '/')[-1]

		if os.sep != '/':
                    path = string.replace(path, '/', os.sep)
                    path_ = string.replace(path_, '/', os.sep)
                    abspath = string.replace(abspath, '/', os.sep)
                    abspath_ = string.replace(abspath_, '/', os.sep)
                    up_path = string.replace(up_path, '/', os.sep)
                    up_path_ = string.replace(up_path_, '/', os.sep)

		assert dir.name == name, \
                       "dir.name %s != expected name %s" % \
                       (dir.name, name)
                assert dir.path == path, \
                       "dir.path %s != expected path %s" % \
                       (dir.path, path)
                assert str(dir) == path, \
                       "str(dir) %s != expected path %s" % \
                       (str(dir), path)
                assert dir.path_ == path_, \
                       "dir.path_ %s != expected path_ %s" % \
                       (dir.path_, path_)
                assert dir.abspath == abspath, \
                       "dir.abspath %s != expected absolute path %s" % \
                       (dir.abspath, abspath)
                assert dir.abspath_ == abspath_, \
                       "dir.abspath_ %s != expected absolute path_ %s" % \
                       (dir.abspath_, abspath_)
                assert dir.up().path == up_path, \
                       "dir.up().path %s != expected parent path %s" % \
                       (dir.up().path, up_path)
                assert dir.up().path_ == up_path_, \
                       "dir.up().path_ %s != expected parent path_ %s" % \
                       (dir.up().path_, up_path_)

            Dir_test('foo',         'foo/',        sub_dir_foo,       './')
            Dir_test('foo/bar',     'foo/bar/',    sub_dir_foo_bar,   'foo/')
            Dir_test('/foo',        '/foo/',       '/foo/',           '/')
            Dir_test('/foo/bar',    '/foo/bar/',   '/foo/bar/',       '/foo/')
            Dir_test('..',          sub,           sub,               wp)
            Dir_test('foo/..',      './',          sub_dir,           sub)
            Dir_test('../foo',      sub_foo,       sub_foo,           sub)
            Dir_test('.',           './',          sub_dir,           sub)
            Dir_test('./.',         './',          sub_dir,           sub)
            Dir_test('foo/./bar',   'foo/bar/',    sub_dir_foo_bar,   'foo/')

            try:
                f2 = fs.File(string.join(['f1', 'f2'], sep), directory = d1)
            except TypeError, x:
	        assert str(x) == ("Tried to lookup File '%s' as a Dir." %
		                  d1_f1), x
            except:
                raise

            try:
                dir = fs.Dir(string.join(['d1', 'f1'], sep))
            except TypeError, x:
	        assert str(x) == ("Tried to lookup File '%s' as a Dir." %
		                  d1_f1), x
            except:
                raise

            try:
                f2 = fs.File('d1')
            except TypeError, x:
                assert str(x) == ("Tried to lookup Dir '%s' as a File." %
                                  'd1'), x
            except:
	        raise

            # Test Dir.children()
            dir = fs.Dir('ddd')
            fs.File(string.join(['ddd', 'f1'], sep))
            fs.File(string.join(['ddd', 'f2'], sep))
            fs.File(string.join(['ddd', 'f3'], sep))
            fs.Dir(string.join(['ddd', 'd1'], sep))
            fs.Dir(string.join(['ddd', 'd1', 'f4'], sep))
            fs.Dir(string.join(['ddd', 'd1', 'f5'], sep))
            kids = map(lambda x: x.path, dir.children())
            kids.sort()
            assert kids == [os.path.join('ddd', 'd1'),
	                    os.path.join('ddd', 'f1'),
			    os.path.join('ddd', 'f2'),
			    os.path.join('ddd', 'f3')]
            kids = map(lambda x: x.path_, dir.children())
            kids.sort()
            assert kids == [os.path.join('ddd', 'd1', ''),
                            os.path.join('ddd', 'f1'),
                            os.path.join('ddd', 'f2'),
                            os.path.join('ddd', 'f3')]

        # Test for sub-classing of node building.
        global built_it

        built_it = None
        assert not built_it
        d1.add_source([SCons.Node.Node()])    # XXX FAKE SUBCLASS ATTRIBUTE
        d1.builder_set(Builder())
        d1.env_set(Environment())
        d1.build()
        assert not built_it

        assert d1.get_parents() == [] 

        built_it = None
        assert not built_it
        f1.add_source([SCons.Node.Node()])    # XXX FAKE SUBCLASS ATTRIBUTE
        f1.builder_set(Builder())
        f1.env_set(Environment())
        f1.build()
        assert built_it

	e1 = fs.Entry("d1")
	assert e1.__class__.__name__ == 'Dir'
        assert e1.path == "d1", e1.path
        assert e1.path_ == "d1/", e1.path_
	assert e1.dir.path == ".", e1.dir.path

	e2 = fs.Entry("d1/f1")
	assert e2.__class__.__name__ == 'File'
	assert e2.path == "d1/f1", e2.path
        assert e2.path_ == "d1/f1", e2.path_
	assert e2.dir.path == "d1", e2.dir.path

	e3 = fs.Entry("e3")
	assert e3.__class__.__name__ == 'Entry'
	assert e3.path == "e3", e3.path
        assert e3.path_ == "e3", e3.path_
	assert e3.dir.path == ".", e3.dir.path

	e4 = fs.Entry("d1/e4")
	assert e4.__class__.__name__ == 'Entry'
	assert e4.path == "d1/e4", e4.path
        assert e4.path_ == "d1/e4", e4.path_
	assert e4.dir.path == "d1", e4.dir.path

	e5 = fs.Entry("e3/e5")
	assert e3.__class__.__name__ == 'Dir'
        assert e3.path == "e3", e3.path
        assert e3.path_ == "e3/", e3.path_
	assert e3.dir.path == ".", e3.dir.path
	assert e5.__class__.__name__ == 'Entry'
	assert e5.path == "e3/e5", e5.path
        assert e5.path_ == "e3/e5", e5.path_
	assert e5.dir.path == "e3", e5.dir.path

	e6 = fs.Dir("d1/e4")
	assert e6 is e4
	assert e4.__class__.__name__ == 'Dir'
        assert e4.path == "d1/e4", e4.path
        assert e4.path_ == "d1/e4/", e4.path_
	assert e4.dir.path == "d1", e4.dir.path

	e7 = fs.File("e3/e5")
	assert e7 is e5
	assert e5.__class__.__name__ == 'File'
	assert e5.path == "e3/e5", e5.path
        assert e5.path_ == "e3/e5", e5.path_
	assert e5.dir.path == "e3", e5.dir.path

        e8 = fs.Entry("e8")
        assert e8.get_bsig() is None, e8.get_bsig()
        assert e8.get_csig() is None, e8.get_csig()
        e8.set_bsig('xxx')
        e8.set_csig('yyy')
        assert e8.get_bsig() == 'xxx', e8.get_bsig()
        assert e8.get_csig() == 'yyy', e8.get_csig()

        f9 = fs.File("f9")
        assert f9.get_bsig() is None, f9.get_bsig()
        assert f9.get_csig() is None, f9.get_csig()
        f9.set_bsig('xxx')
        f9.set_csig('yyy')
        assert f9.get_bsig() == 'xxx', f9.get_bsig()
        assert f9.get_csig() == 'yyy', f9.get_csig()

        d10 = fs.Dir("d10")
        assert d10.get_bsig() is None, d10.get_bsig()
        assert d10.get_csig() is None, d10.get_csig()
        d10.set_bsig('xxx')
        d10.set_csig('yyy')
        assert d10.get_bsig() is None, d10.get_bsig()
        assert d10.get_csig() is None, d10.get_csig()

        #XXX test exists()

        #XXX test current() for directories

        #XXX test sconsign() for directories

        #XXX test set_signature() for directories

        #XXX test build() for directories

        #XXX test root()

        #XXX test get_contents()

        #XXX test get_timestamp()

        #XXX test get_prevsiginfo()



if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(FSTestCase())
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
        sys.exit(1)
