#
# Copyright (c) 2001, 2002 Steven Knight
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
import string
import sys
import unittest
import SCons.Node.FS
from TestCmd import TestCmd
from SCons.Errors import UserError
import stat

built_it = None

class Builder:
    def execute(self, **kw):
        global built_it
        built_it = 1
        return 0

scanner_count = 0

class Scanner:
    def __init__(self):
        global scanner_count
        scanner_count = scanner_count + 1
        self.hash = scanner_count
    def scan(self, node, env):
        return [node]
    def __hash__(self):
        return self.hash

class Environment:
    def __init__(self):
        self.scanner = Scanner()
    def Dictionary(self, *args):
	pass
    def get_scanner(self, skey):
        return self.scanner

class BuildDirTestCase(unittest.TestCase):
    def runTest(self):
        """Test build dir functionality"""
        fs = SCons.Node.FS.FS()
        f1 = fs.File('build/test1')
        fs.BuildDir('build', 'src')
        f2 = fs.File('build/test2')
        assert f1.srcpath == os.path.normpath('src/test1'), f1.srcpath
        assert f2.srcpath == os.path.normpath('src/test2'), f2.srcpath

        fs = SCons.Node.FS.FS()
        f1 = fs.File('build/test1')
        fs.BuildDir('build', '.')
        f2 = fs.File('build/test2')
        assert f1.srcpath == 'test1', f1.srcpath
        assert f2.srcpath == 'test2', f2.srcpath

        fs = SCons.Node.FS.FS()
        fs.BuildDir('build/var1', 'src')
        fs.BuildDir('build/var2', 'src')
        f1 = fs.File('build/var1/test1')
        f2 = fs.File('build/var2/test1')
        assert f1.srcpath == os.path.normpath('src/test1'), f1.srcpath
        assert f2.srcpath == os.path.normpath('src/test1'), f2.srcpath

        fs = SCons.Node.FS.FS()
        fs.BuildDir('build/var1', 'src', duplicate=0)
        fs.BuildDir('build/var2', 'src')
        f1 = fs.File('build/var1/test1')
        f1out = fs.File('build/var1/test1.out')
        f1out.builder = 1
        f2 = fs.File('build/var2/test1')
        assert f1.srcpath == os.path.normpath('src/test1'), f1.srcpath
        assert f1out.srcpath == os.path.normpath('src/test1.out'), f1out.srcpath
        assert str(f1) == os.path.normpath('src/test1'), str(f1)
        assert str(f1out) == os.path.normpath('build/var1/test1.out'), str(f1out)
        assert f2.srcpath == os.path.normpath('src/test1'), str(f2)
        assert str(f2) == os.path.normpath('build/var2/test1'), str(f2)

        # Test to see if file_link() works...
        test=TestCmd(workdir='')
        test.subdir('src','build')
        test.write('src/foo', 'foo\n')
        os.chmod(test.workpath('src/foo'), stat.S_IRUSR)
        SCons.Node.FS.file_link(test.workpath('src/foo'),
                                test.workpath('build/foo'))
        os.chmod(test.workpath('src/foo'), stat.S_IRUSR | stat.S_IWRITE)
        st=os.stat(test.workpath('build/foo'))
        assert (stat.S_IMODE(st[stat.ST_MODE]) & stat.S_IWRITE), \
               stat.S_IMODE(st[stat.ST_MODE])

        exc_caught = 0
        try:
            fs = SCons.Node.FS.FS()
            fs.BuildDir('/test/foo', '.')
        except UserError:
            exc_caught = 1
        assert exc_caught, "Should have caught a UserError."

        exc_caught = 0
        try:
            fs = SCons.Node.FS.FS()
            fs.BuildDir('build', '/test/foo')
        except UserError:
            exc_caught = 1
        assert exc_caught, "Should have caught a UserError."

        exc_caught = 0
        try:
            fs = SCons.Node.FS.FS()
            fs.BuildDir('build', 'build/src')
        except UserError:
            exc_caught = 1
        assert exc_caught, "Should have caught a UserError."

class FSTestCase(unittest.TestCase):
    def runTest(self):
        """Test FS (file system) Node operations
        
        This test case handles all of the file system node
        tests in one environment, so we don't have to set up a
        complicated directory structure for each test individually.
        """
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

                if os.sep != '/':
                    path_ = string.replace(path_, '/', os.sep)
                    abspath_ = string.replace(abspath_, '/', os.sep)
                    up_path_ = string.replace(up_path_, '/', os.sep)

                def strip_slash(p):
                    if p[-1] == os.sep and len(p) > 1:
                        p = p[:-1]
                    return p
                path = strip_slash(path_)
                abspath = strip_slash(abspath_)
                up_path = strip_slash(up_path_)
                name = string.split(abspath, os.sep)[-1]

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

        # Test for a bug in 0.04 that did not like looking up
        # dirs with a trailing slash on Win32.
        d=fs.Dir('./')
        assert d.path_ == '.' + os.sep, d.abspath_
        d=fs.Dir('foo/')
        assert d.path_ == 'foo' + os.sep, d.path_

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

        def match(path, expect):
            expect = string.replace(expect, '/', os.sep)
            assert path == expect, "path %s != expected %s" % (path, expect)

	e1 = fs.Entry("d1")
	assert e1.__class__.__name__ == 'Dir'
        match(e1.path, "d1")
        match(e1.path_, "d1/")
        match(e1.dir.path, ".")

	e2 = fs.Entry("d1/f1")
	assert e2.__class__.__name__ == 'File'
        match(e2.path, "d1/f1")
        match(e2.path_, "d1/f1")
        match(e2.dir.path, "d1")

	e3 = fs.Entry("e3")
	assert e3.__class__.__name__ == 'Entry'
        match(e3.path, "e3")
        match(e3.path_, "e3")
        match(e3.dir.path, ".")

	e4 = fs.Entry("d1/e4")
	assert e4.__class__.__name__ == 'Entry'
        match(e4.path, "d1/e4")
        match(e4.path_, "d1/e4")
        match(e4.dir.path, "d1")

	e5 = fs.Entry("e3/e5")
	assert e3.__class__.__name__ == 'Dir'
        match(e3.path, "e3")
        match(e3.path_, "e3/")
        match(e3.dir.path, ".")
	assert e5.__class__.__name__ == 'Entry'
        match(e5.path, "e3/e5")
        match(e5.path_, "e3/e5")
        match(e5.dir.path, "e3")

	e6 = fs.Dir("d1/e4")
	assert e6 is e4
	assert e4.__class__.__name__ == 'Dir'
        match(e4.path, "d1/e4")
        match(e4.path_, "d1/e4/")
        match(e4.dir.path, "d1")

	e7 = fs.File("e3/e5")
	assert e7 is e5
	assert e5.__class__.__name__ == 'File'
        match(e5.path, "e3/e5")
        match(e5.path_, "e3/e5")
        match(e5.dir.path, "e3")

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

        fs.chdir(fs.Dir('subdir'))
        f11 = fs.File("f11")
        match(f11.path, "subdir/f11")
        d12 = fs.Dir("d12")
        match(d12.path_, "subdir/d12/")
        e13 = fs.Entry("subdir/e13")
        match(e13.path, "subdir/subdir/e13")

        # Test scanning
        scn = Scanner()
        f1.scanners = [ scn ]
        f1.scan()
        assert f1.implicit[scn][0].path_ == os.path.join("d1", "f1")
        del f1.implicit[scn]
        f1.scan()
        assert len(f1.implicit) == 0, f1.implicit
        del f1.scanned[scn]
        f1.scan()
        assert f1.implicit[scn][0].path_ == os.path.join("d1", "f1")

        # Test building a file whose directory is not there yet...
        f1 = fs.File(test.workpath("foo/bar/baz/ack"))
        assert not f1.dir.exists()
        f1.prepare()
        f1.build()
        assert f1.dir.exists()

        os.chdir('..')

	# Test getcwd()
        fs = SCons.Node.FS.FS()
	assert str(fs.getcwd()) == ".", str(fs.getcwd())
	fs.chdir(fs.Dir('subdir'))
	assert str(fs.getcwd()) == "subdir", str(fs.getcwd())
	fs.chdir(fs.Dir('../..'))
	assert str(fs.getcwd()) == test.workdir, str(fs.getcwd())
        
        f1 = fs.File(test.workpath("do_i_exist"))
        assert not f1.exists()
        test.write("do_i_exist","\n")
        assert f1.exists()
        assert f1.cached_exists()
        test.unlink("do_i_exist")
        assert not f1.exists()
        assert f1.cached_exists()
        f1.build()
        assert not f1.cached_exists()

        # For some reason, in Win32, the \x1a character terminates
        # the reading of files in text mode.  This tests that
        # get_contents() returns the binary contents.
        test.write("binary_file", "Foo\x1aBar")
        f1 = SCons.Node.FS.default_fs.File(test.workpath("binary_file"))
        assert f1.get_contents() == "Foo\x1aBar", f1.get_contents()

        def nonexistent(method, str):
            try:
                x = method(str, create = 0)
            except UserError:
                pass
            else:
                raise TestFailed, "did not catch expected UserError"

        nonexistent(fs.Entry, 'nonexistent')
        nonexistent(fs.Entry, 'nonexistent/foo')

        nonexistent(fs.File, 'nonexistent')
        nonexistent(fs.File, 'nonexistent/foo')

        nonexistent(fs.Dir, 'nonexistent')
        nonexistent(fs.Dir, 'nonexistent/foo')

        test.write("remove_me", "\n")
        assert os.path.exists(test.workpath("remove_me"))
        f1 = fs.File(test.workpath("remove_me"))
        f1.prepare()
        assert not os.path.exists(test.workpath("remove_me"))

        #XXX test current() for directories

        #XXX test sconsign() for directories

        #XXX test set_signature() for directories

        #XXX test build() for directories

        #XXX test root()

        #XXX test get_contents()

        #XXX test get_timestamp()

        #XXX test get_prevsiginfo()


class find_fileTestCase(unittest.TestCase):
    def runTest(self):
        """Testing find_file function"""
        test = TestCmd(workdir = '')
        test.write('./foo', 'Some file\n')
        fs = SCons.Node.FS.FS(test.workpath(""))
        os.chdir(test.workpath("")) # FS doesn't like the cwd to be something other than it's root
        node_derived = fs.File(test.workpath('bar/baz'))
        node_derived.builder_set(1) # Any non-zero value.
        paths = map(fs.Dir, ['.', './bar'])
        nodes = [SCons.Node.FS.find_file('foo', paths, fs.File), 
                 SCons.Node.FS.find_file('baz', paths, fs.File)] 
        file_names = map(str, nodes)
        file_names = map(os.path.normpath, file_names)
        assert os.path.normpath('./foo') in file_names, file_names
        assert os.path.normpath('./bar/baz') in file_names, file_names



if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(FSTestCase())
    suite.addTest(BuildDirTestCase())
    suite.addTest(find_fileTestCase())
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
        sys.exit(1)
