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
import time
import unittest
import SCons.Node.FS
from TestCmd import TestCmd
from SCons.Errors import UserError
import stat

built_it = None

class Builder:
    def __init__(self, factory):
        self.factory = factory

    def execute(self, target, source, env):
        global built_it
        built_it = 1
        return 0
    
    def source_factory(self, name):
        return self.factory(name)

scanner_count = 0

class Scanner:
    def __init__(self):
        global scanner_count
        scanner_count = scanner_count + 1
        self.hash = scanner_count
    def scan(self, node, env, target):
        return [node]
    def __hash__(self):
        return self.hash

class Environment:
    def __init__(self):
        self.scanner = Scanner()
    def Dictionary(self, *args):
        return {}
    def autogenerate(self, **kw):
        return {}
    def get_scanner(self, skey):
        return self.scanner
    def Override(self, overrides):
        return self

class BuildDirTestCase(unittest.TestCase):
    def runTest(self):
        """Test build dir functionality"""
        test=TestCmd(workdir='')
        os.chdir(test.workdir)

        fs = SCons.Node.FS.FS()
        f1 = fs.File('build/test1')
        fs.BuildDir('build', 'src')
        f2 = fs.File('build/test2')
        assert f1.srcnode().path == os.path.normpath('src/test1'), f1.srcnode().path
        assert f2.srcnode().path == os.path.normpath('src/test2'), f2.srcnode().path

        fs = SCons.Node.FS.FS()
        f1 = fs.File('build/test1')
        fs.BuildDir('build', '.')
        f2 = fs.File('build/test2')
        assert f1.srcnode().path == 'test1', f1.srcnode().path
        assert f2.srcnode().path == 'test2', f2.srcnode().path

        fs = SCons.Node.FS.FS()
        fs.BuildDir('build/var1', 'src')
        fs.BuildDir('build/var2', 'src')
        f1 = fs.File('build/var1/test1')
        f2 = fs.File('build/var2/test1')
        assert f1.srcnode().path == os.path.normpath('src/test1'), f1.srcnode().path
        assert f2.srcnode().path == os.path.normpath('src/test1'), f2.srcnode().path

        fs = SCons.Node.FS.FS()
        fs.BuildDir('../var1', 'src')
        fs.BuildDir('../var2', 'src')
        f1 = fs.File('../var1/test1')
        f2 = fs.File('../var2/test1')
        assert hasattr(f1, 'overrides')
        assert f1.srcnode().path == os.path.normpath('src/test1'), f1.srcnode().path
        assert f2.srcnode().path == os.path.normpath('src/test1'), f2.srcnode().path

        # Set up some files
        test.subdir('work', ['work', 'src'])
        test.subdir(['work', 'build'], ['work', 'build', 'var1'])
        test.subdir(['work', 'build', 'var2'])
        test.subdir('rep1', ['rep1', 'src'])
        test.subdir(['rep1', 'build'], ['rep1', 'build', 'var1'])
        test.subdir(['rep1', 'build', 'var2'])

        # A source file in the source directory
        test.write([ 'work', 'src', 'test.in' ], 'test.in')

        # A source file in the repository
        test.write([ 'rep1', 'src', 'test2.in' ], 'test2.in')
        
        # Some source files in the build directory
        test.write([ 'work', 'build', 'var2', 'test.in' ], 'test.old')
        test.write([ 'work', 'build', 'var2', 'test2.in' ], 'test2.old')

        # An old derived file in the build directories
        test.write([ 'work', 'build', 'var1', 'test.out' ], 'test.old')
        test.write([ 'work', 'build', 'var2', 'test.out' ], 'test.old')

        # And just in case we are weird, a derived file in the source
        # dir.
        test.write([ 'work', 'src', 'test.out' ], 'test.out.src')
        
        # A derived file in the repository
        test.write([ 'rep1', 'build', 'var1', 'test2.out' ], 'test2.out_rep')
        test.write([ 'rep1', 'build', 'var2', 'test2.out' ], 'test2.out_rep')

        fs = SCons.Node.FS.FS(test.workpath('work'))
        fs.BuildDir('build/var1', 'src', duplicate=0)
        fs.BuildDir('build/var2', 'src')
        f1 = fs.File('build/var1/test.in')
        f1out = fs.File('build/var1/test.out')
        f1out.builder = 1
        f1out_2 = fs.File('build/var1/test2.out')
        f1out_2.builder = 1
        f2 = fs.File('build/var2/test.in')
        f2out = fs.File('build/var2/test.out')
        f2out.builder = 1
        f2out_2 = fs.File('build/var2/test2.out')
        f2out_2.builder = 1
        fs.Repository(test.workpath('rep1'))
        
        assert f1.srcnode().path == os.path.normpath('src/test.in'),\
               f1.srcnode().path
        # str(node) returns source path for duplicate = 0
        assert str(f1) == os.path.normpath('src/test.in'), str(f1)
        # Build path does not exist
        assert not f1.exists()
        # But source path does
        assert f1.srcnode().exists()
        # And duplicate=0 should also work just like a Repository
        assert f1.rexists()
        # rfile() should point to the source path
        assert f1.rfile().path == os.path.normpath('src/test.in'),\
               f1.rfile().path

        assert f2.srcnode().path == os.path.normpath('src/test.in'),\
               f2.srcnode().path
        # str(node) returns build path for duplicate = 1
        assert str(f2) == os.path.normpath('build/var2/test.in'), str(f2)
        # Build path exists
        assert f2.exists()
        # ...and should copy the file from src to build path
        assert test.read(['work', 'build', 'var2', 'test.in']) == 'test.in',\
               test.read(['work', 'build', 'var2', 'test.in'])
        # Since exists() is true, so should rexists() be
        assert f2.rexists()

        f3 = fs.File('build/var1/test2.in')
        f4 = fs.File('build/var2/test2.in')

        assert f3.srcnode().path == os.path.normpath('src/test2.in'),\
               f3.srcnode().path
        # str(node) returns source path for duplicate = 0
        assert str(f3) == os.path.normpath('src/test2.in'), str(f3)
        # Build path does not exist
        assert not f3.exists()
        # Source path does not either
        assert not f3.srcnode().exists()
        # But we do have a file in the Repository
        assert f3.rexists()
        # rfile() should point to the source path
        assert f3.rfile().path == test.workpath('rep1/src/test2.in'),\
               f3.rfile().path

        assert f4.srcnode().path == os.path.normpath('src/test2.in'),\
               f4.srcnode().path
        # str(node) returns build path for duplicate = 1
        assert str(f4) == os.path.normpath('build/var2/test2.in'), str(f4)
        # Build path should exist
        assert f4.exists()
        # ...and copy over the file into the local build path
        assert test.read(['work', 'build', 'var2', 'test2.in']) == 'test2.in'
        # should exist in repository, since exists() is true
        assert f4.rexists()
        # rfile() should point to ourselves
        assert f4.rfile().path == os.path.normpath('build/var2/test2.in'),\
               f4.rfile().path

        f5 = fs.File('build/var1/test.out')
        f6 = fs.File('build/var2/test.out')

        assert f5.exists()
        # We should not copy the file from the source dir, since this is
        # a derived file.
        assert test.read(['work', 'build', 'var1', 'test.out']) == 'test.old'

        assert f6.exists()
        # We should not copy the file from the source dir, since this is
        # a derived file.
        assert test.read(['work', 'build', 'var2', 'test.out']) == 'test.old'
        f7 = fs.File('build/var1/test2.out')
        f8 = fs.File('build/var2/test2.out')

        assert not f7.exists()
        assert f7.rexists()
        assert f7.rfile().path == test.workpath('rep1/build/var1/test2.out'),\
               f7.rfile().path

        assert not f8.exists()
        assert f8.rexists()
        assert f8.rfile().path == test.workpath('rep1/build/var2/test2.out'),\
               f8.rfile().path
        
        # Test to see if file_link() works...
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
        assert d1.cwd is d1, d1

        f1 = fs.File('f1', directory = d1)

        d1_f1 = os.path.join('d1', 'f1')
        assert f1.path == d1_f1, "f1.path %s != %s" % (f1.path, d1_f1)
        assert str(f1) == d1_f1, "str(f1) %s != %s" % (str(f1), d1_f1)

        x1 = d1.File('x1')
        assert str(x1) == os.path.join('d1', 'x1')

        x2 = d1.Dir('x2')
        assert str(x2) == os.path.join('d1', 'x2')

        assert d1.File(x1) == x1
        assert d1.Dir(x2) == x2

        x1.cwd = d1

        x3 = x1.File('x3')
        assert str(x3) == os.path.join('d1', 'x3')

        x4 = x1.Dir('x4')
        assert str(x4) == os.path.join('d1', 'x4')

        assert x1.File(x3) == x3
        assert x1.Dir(x4) == x4

        try:
            x1.File(x4)
        except TypeError:
            pass
        else:
            assert 0

        try:
            x1.Dir(x3)
        except TypeError:
            pass
        else:
            assert 0

        
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
            Dir_test('#../foo',     sub_foo,       sub_foo,           sub)
            Dir_test('#/../foo',    sub_foo,       sub_foo,           sub)
            Dir_test('#foo/bar',    'foo/bar/',    sub_dir_foo_bar,   'foo/')
            Dir_test('#/foo/bar',   'foo/bar/',    sub_dir_foo_bar,   'foo/')
            Dir_test('#',           './',          sub_dir,           sub)

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
            kids = map(lambda x: x.path, dir.children(None))
            kids.sort()
            assert kids == [os.path.join('ddd', 'd1'),
                            os.path.join('ddd', 'f1'),
                            os.path.join('ddd', 'f2'),
                            os.path.join('ddd', 'f3')]
            kids = map(lambda x: x.path_, dir.children(None))
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
        d1.builder_set(Builder(fs.File))
        d1.env_set(Environment())
        d1.build()
        assert not built_it

        built_it = None
        assert not built_it
        f1.add_source([SCons.Node.Node()])    # XXX FAKE SUBCLASS ATTRIBUTE
        f1.builder_set(Builder(fs.File))
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
        fs.chdir(fs.Dir('..'))

        # Test scanning
        f1.target_scanner = Scanner()
        f1.scan()
        assert f1.implicit[0].path_ == os.path.join("d1", "f1")
        f1.implicit = []
        f1.scan()
        assert f1.implicit == []
        f1.implicit = None
        f1.scan()
        assert f1.implicit[0].path_ == os.path.join("d1", "f1"), f1.implicit[0].path_
        f1.store_implicit()
        assert f1.get_stored_implicit()[0] == os.path.join("d1", "f1")

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
        assert not f1.exists()
        f1.built()
        assert f1.exists()
        test.unlink("do_i_exist")
        assert f1.exists()
        f1.built()
        assert not f1.exists()

        # For some reason, in Win32, the \x1a character terminates
        # the reading of files in text mode.  This tests that
        # get_contents() returns the binary contents.
        test.write("binary_file", "Foo\x1aBar")
        f1 = SCons.Node.FS.default_fs.File(test.workpath("binary_file"))
        assert f1.get_contents() == "Foo\x1aBar", f1.get_contents()

        def nonexistent(method, s):
            try:
                x = method(s, create = 0)
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

        test.write("preserve_me", "\n")
        assert os.path.exists(test.workpath("preserve_me"))
        f1 = fs.File(test.workpath("preserve_me"))
        f1.prepare()
        assert os.path.exists(test.workpath("preserve_me"))

        test.write("remove_me", "\n")
        assert os.path.exists(test.workpath("remove_me"))
        f1 = fs.File(test.workpath("remove_me"))
        f1.builder = 1
        f1.prepare()
        assert not os.path.exists(test.workpath("remove_me"))

        #XXX test current() for directories

        #XXX test sconsign() for directories

        #XXX test set_signature() for directories

        #XXX test build() for directories

        #XXX test root()

        # test Entry.get_contents()
        e = fs.Entry('does_not_exist')
        exc_caught = 0
        try:
            e.get_contents()
        except AttributeError:
            exc_caught = 1
        assert exc_caught, "Should have caught an AttributError"

        test.write("file", "file\n")
        e = fs.Entry('file')
        c = e.get_contents()
        assert c == "file\n", c
        assert e.__class__ == SCons.Node.FS.File
        test.unlink("file")

        test.subdir("dir")
        e = fs.Entry('dir')
        c = e.get_contents()
        assert c == "", c
        assert e.__class__ == SCons.Node.FS.Dir

        test.write("tstamp", "tstamp\n")
        # Okay, *this* manipulation accomodates Windows FAT file systems
        # that only have two-second granularity on their timestamps.
        # We round down the current time to the nearest even integer
        # value, subtract two to make sure the timestamp is not "now,"
        # and then convert it back to a float.
        tstamp = float(int(time.time() / 2) * 2) - 2
        os.utime(test.workpath("tstamp"), (tstamp - 2.0, tstamp))
        f = fs.File("tstamp")
        t = f.get_timestamp()
        assert t == tstamp, "expected %f, got %f" % (tstamp, t)
        test.unlink("tstamp")

        #XXX test get_prevsiginfo()

        assert fs.File('foo.x').scanner_key() == '.x'
        assert fs.File('foo.xyz').scanner_key() == '.xyz'

        d1 = fs.Dir('dir')
        f1 = fs.File('dir/file')
        assert f1.dir == d1, f1.dir
        parents = f1.get_parents()
        assert parents == [ d1 ], parents

        test.write("i_am_not_a_directory", "\n")
        exc_caught = 0        
        try:
            fs.Dir(test.workpath("i_am_not_a_directory"))
        except TypeError:
            exc_caught = 1
        assert exc_caught, "Should have caught a TypeError"
        test.unlink("i_am_not_a_directory")

        exc_caught = 0
        try:
            fs.File(sub_dir)
        except TypeError:
            exc_caught = 1
        assert exc_caught, "Should have caught a TypeError"

        # XXX test calc_signature()

        # XXX test current()

        d = fs.Dir('dir')
        r = d.remove()
        assert r is None, r

        f = fs.File('does_not_exist')
        r = f.remove()
        assert r == None, r

        test.write('exists', "exists\n")
        f = fs.File('exists')
        r = f.remove()
        assert r, r

        test.write('can_not_remove', "can_not_remove\n")
        test.writable(test.workpath('.'), 0)
        fp = open(test.workpath('can_not_remove'))

        f = fs.File('can_not_remove')
        exc_caught = 0 
        try:
            r = f.remove()
        except OSError:
            exc_caught = 1

        fp.close()

        assert exc_caught, "Should have caught an OSError, r = " + str(r)


class RepositoryTestCase(unittest.TestCase):
    def runTest(self):
        """Test FS (file system) Repository operations

        """
        fs = SCons.Node.FS.FS()

        fs.Repository('foo')
        fs.Repository(os.path.join('foo', 'bar'))
        fs.Repository(os.path.join('bar', 'foo'))
        fs.Repository('bar')

        rep = fs.Dir('#').getRepositories()
        assert len(rep) == 4, map(str, rep)
        r = map(lambda x, np=os.path.normpath: np(str(x)), rep)
        assert r == ['foo',
                     os.path.join('foo', 'bar'),
                     os.path.join('bar', 'foo'),
                     'bar'], r

        test = TestCmd(workdir = '')
        test.subdir('rep1', 'rep2', 'rep3', 'work')

        rep1 = test.workpath('rep1')
        rep2 = test.workpath('rep2')
        rep3 = test.workpath('rep3')

        os.chdir(test.workpath('work'))

        fs = SCons.Node.FS.FS()
        fs.Repository(rep1, rep2, rep3)

        f1 = fs.File(os.path.join('f1'))
        assert f1.rfile() is f1

        test.write([rep1, 'f2'], "")

        f2 = fs.File('f2')
        assert not f2.rfile() is f2, f2.rfile()
        assert str(f2.rfile()) == os.path.join(rep1, 'f2'), str(f2.rfile())

        test.subdir([rep2, 'f3'])
        test.write([rep3, 'f3'], "")

        f3 = fs.File('f3')
        assert not f3.rfile() is f3, f3.rfile()
        assert f3.rstr() == os.path.join(rep3, 'f3'), f3.rstr()

        assert fs.Rsearch('f1') is None
        assert fs.Rsearch('f2')
        assert fs.Rsearch(f3) is f3

        list = fs.Rsearchall(fs.Dir('d1'))
        assert len(list) == 1, list
        assert list[0].path == 'd1', list[0].path

        list = fs.Rsearchall([fs.Dir('d1')])
        assert len(list) == 1, list
        assert list[0].path == 'd1', list[0].path

        list = fs.Rsearchall('d2')
        assert list == [], list

        list = fs.Rsearchall('#d2')
        assert list == [], list

        test.subdir(['work', 'd2'])
        fs.File('d2').built() # Clear exists cache
        list = fs.Rsearchall('d2')
        assert map(str, list) == ['d2'], list

        test.subdir(['rep2', 'd2'])
        fs.File('../rep2/d2').built() # Clear exists cache
        list = fs.Rsearchall('d2')
        assert map(str, list) == ['d2', test.workpath('rep2', 'd2')], list

        test.subdir(['rep1', 'd2'])
        fs.File('../rep1/d2').built() # Clear exists cache
        list = fs.Rsearchall('d2')
        assert map(str, list) == ['d2',
                                  test.workpath('rep1', 'd2'),
                                  test.workpath('rep2', 'd2')], list

        list = fs.Rsearchall(['d3', 'd4'])
        assert list == [], list

        test.subdir(['work', 'd3'])
        fs.File('d3').built() # Clear exists cache
        list = map(str, fs.Rsearchall(['d3', 'd4']))
        assert list == ['d3'], list

        test.subdir(['rep3', 'd4'])
        fs.File('../rep3/d4').built() # Clear exists cache
        list = map(str, fs.Rsearchall(['d3', 'd4']))
        assert list == ['d3', test.workpath('rep3', 'd4')], list

        list = map(str, fs.Rsearchall(string.join(['d3', 'd4'], os.pathsep)))
        assert list == ['d3', test.workpath('rep3', 'd4')], list

        work_d4 = fs.File(os.path.join('work', 'd4'))
        list = map(str, fs.Rsearchall(['d3', work_d4]))
        assert list == ['d3', str(work_d4)], list

        fs.BuildDir('build', '.')
        
        f = fs.File(test.workpath("work", "i_do_not_exist"))
        assert not f.rexists()
        
        test.write(["rep2", "i_exist"], "\n")
        f = fs.File(test.workpath("work", "i_exist"))
        assert f.rexists()
        
        test.write(["work", "i_exist_too"], "\n")
        f = fs.File(test.workpath("work", "i_exist_too"))
        assert f.rexists()

        f1 = fs.File(os.path.join('build', 'f1'))
        assert not f1.rexists()

        f2 = fs.File(os.path.join('build', 'f2'))
        assert f2.rexists()

        test.write(["rep2", "tstamp"], "tstamp\n")
        # Okay, *this* manipulation accomodates Windows FAT file systems
        # that only have two-second granularity on their timestamps.
        # We round down the current time to the nearest even integer
        # value, subtract two to make sure the timestamp is not "now,"
        # and then convert it back to a float.
        tstamp = float(int(time.time() / 2) * 2) - 2
        os.utime(test.workpath("rep2", "tstamp"), (tstamp - 2.0, tstamp))
        f = fs.File("tstamp")
        t = f.get_timestamp()
        assert t == tstamp, "expected %f, got %f" % (tstamp, t)
        test.unlink(["rep2", "tstamp"])

        # Make sure get_contents() returns the binary contents.
        test.write(["rep3", "contents"], "Con\x1aTents\n")
        c = fs.File("contents").get_contents()
        assert c == "Con\x1aTents\n", "got '%s'" % c
        test.unlink(["rep3", "contents"])

        # XXX test calc_signature()

        # XXX test current()

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
    suite.addTest(RepositoryTestCase())
    suite.addTest(find_fileTestCase())
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
        sys.exit(1)
