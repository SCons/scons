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
            node = x.args[0]
            assert node.path == 'd1/f1', "node.path %s != d1/f1" % node.path
            assert str(node) == 'd1/f1', "str(node) %s != d1/f1" % str(node)
            assert node.__class__.__name__ == 'File'
        except:
            raise

        try:
            dir = fs.Dir('d1/f1')
        except TypeError, x:
            node = x.args[0]
            assert node.path == 'd1/f1', "node.path %s != d1/f1" % node.path
            assert str(node) == 'd1/f1', "str(node) %s != d1/f1" % str(node)
            assert node.__class__.__name__ == 'File'
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
        d1.path = "d"           # XXX FAKE SUBCLASS ATTRIBUTE
        d1.add_source(["d"])    # XXX FAKE SUBCLASS ATTRIBUTE
        d1.builder_set(Builder())
        d1.env_set(Environment())
        d1.build()
        assert built_it

        built_it = None
        assert not built_it
        f1.path = "f"           # XXX FAKE SUBCLASS ATTRIBUTE
        f1.add_source(["f"])    # XXX FAKE SUBCLASS ATTRIBUTE
        f1.builder_set(Builder())
        f1.env_set(Environment())
        f1.build()
        assert built_it


if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(FSTestCase())
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
        sys.exit(1)
