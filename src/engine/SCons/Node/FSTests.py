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

scanner_count = 0

class Scanner:
    def __init__(self):
        global scanner_count
        scanner_count = scanner_count + 1
        self.hash = scanner_count
    def scan(self, filename, env):
        return [SCons.Node.FS.default_fs.File(filename)]
    def __hash__(self):
        return self.hash

class Environment:
    def __init__(self):
        self.scanner = Scanner()
    def Dictionary(self, *args):
	pass
    def get_scanner(self, skey):
        return self.scanner


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
        f1.scanner = Scanner()
        f1.scan()
        assert f1.depends[0].path_ == os.path.join("d1", "f1")
	f1.scanner = None
	f1.scanned = None
        f1.scan()
        assert f1.depends[0].path_ == os.path.join("d1", "f1")
	f1.scanner = None
	f1.scanned = None
	f1.depends = []
        f1.scan()
        assert not f1.depends

        # Test building a file whose directory is not there yet...
        f1 = fs.File(test.workpath("foo/bar/baz/ack"))
        assert not f1.dir.exists()
        f1.build()
        assert f1.dir.exists()

        # Test comparison of FS objects
        fs1 = SCons.Node.FS.FS()
        fs2 = SCons.Node.FS.FS()
        os.chdir('..')
        fs3 = SCons.Node.FS.FS()
        assert fs1 == fs2
        assert fs1 == fs3

        # Test comparison of Entry objects
        e1 = fs3.Entry('cmp/entry')
        e2 = fs3.Entry('cmp/../cmp/entry')
        e3 = fs3.Entry('entry')
        assert e1 == e2
        assert e1 != e3
        assert e1 == os.path.normpath("cmp/entry"), e1
        assert e1 != os.path.normpath("c/entry"), e1

        # Test comparison of Dir objects
        d1 = fs3.Dir('cmp/dir')
        d2 = fs3.Dir('cmp/../cmp/dir')
        d3 = fs3.Dir('dir')
        assert d1 == d2
        assert d1 != d3
        assert d1 == os.path.normpath("cmp/dir"), d1
        assert d1 != os.path.normpath("c/dir"), d1

        # Test comparison of File objects
        f1 = fs3.File('cmp/file')
        f2 = fs3.File('cmp/../cmp/file')
        f3 = fs3.File('file')
        assert f1 == f2
        assert f1 != f3
        assert f1 == os.path.normpath("cmp/file"), f1
        assert f1 != os.path.normpath("c/file"), f1

        # Test comparison of different type objects
        f1 = fs1.File('cmp/xxx')
        d2 = fs2.Dir('cmp/xxx')
        assert f1 != d2, "%s == %s" % (f1.__class__, d2.__class__)

        # Test hashing FS nodes
        f = fs1.File('hash/f')
        d = fs1.Dir('hash/d')
        e = fs1.Entry('hash/e')
        val = {}
        val[f] = 'f'
        val[d] = 'd'
        val[e] = 'e'
        for k, v in val.items():
             assert k == "hash/" + v
        
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
