__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import os
import sys
import unittest

import SCons.Node.FS

built_it = None

class Builder:
    def execute(self, target = None, source = None):
        global built_it
        built_it = 1

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

        try:
            f2 = fs.File('f1/f2', directory = d1)
        except TypeError, x:
            node = x.args[0]
            assert node.path == 'd1/f1', "node.path %s != d1/f1" % node.path
            assert node.__class__.__name__ == 'File'
        except:
            raise

        try:
            dir = fs.Dir('d1/f1')
        except TypeError, x:
            node = x.args[0]
            assert node.path == 'd1/f1', "node.path %s != d1/f1" % node.path
            assert node.__class__.__name__ == 'File'
        except:
            raise

        # Test for sub-classing of node building.
        global built_it

        built_it = None
        assert not built_it
        d1.path = "d"           # XXX FAKE SUBCLASS ATTRIBUTE
        d1.sources = "d"        # XXX FAKE SUBCLASS ATTRIBUTE
        d1.builder_set(Builder())
        d1.build()
        assert built_it

        built_it = None
        assert not built_it
        f1.path = "f"           # XXX FAKE SUBCLASS ATTRIBUTE
        f1.sources = "f"        # XXX FAKE SUBCLASS ATTRIBUTE
        f1.builder_set(Builder())
        f1.build()
        assert built_it


if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(FSTestCase())
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
        sys.exit(1)
