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
from __future__ import division, print_function

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import SCons.compat

import os
import os.path
import sys
import time
import unittest
import shutil
import stat

from TestCmd import TestCmd
import TestUnit

import SCons.Errors
import SCons.Node.FS
import SCons.Util
import SCons.Warnings
import SCons.Environment

built_it = None

scanner_count = 0

class Scanner(object):
    def __init__(self, node=None):
        global scanner_count
        scanner_count = scanner_count + 1
        self.hash = scanner_count
        self.node = node
    def path(self, env, dir, target=None, source=None):
        return ()
    def __call__(self, node, env, path):
        return [self.node]
    def __hash__(self):
        return self.hash
    def select(self, node):
        return self
    def recurse_nodes(self, nodes):
        return nodes

class Environment(object):
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
    def _update(self, dict):
        pass

class Action(object):
    def __call__(self, targets, sources, env, **kw):
        global built_it
        if kw.get('execute', 1):
            built_it = 1
        return 0
    def show(self, string):
        pass
    def get_contents(self, target, source, env):
        return bytearray("",'utf-8')
    def genstring(self, target, source, env):
        return ""
    def strfunction(self, targets, sources, env):
        return ""
    def get_implicit_deps(self, target, source, env):
        return []

class Builder(object):
    def __init__(self, factory, action=Action()):
        self.factory = factory
        self.env = Environment()
        self.overrides = {}
        self.action = action
        self.target_scanner = None
        self.source_scanner = None

    def targets(self, t):
        return [t]

    def source_factory(self, name):
        return self.factory(name)

class _tempdirTestCase(unittest.TestCase):
    def setUp(self):
        self.save_cwd = os.getcwd()
        self.test = TestCmd(workdir='')
        # FS doesn't like the cwd to be something other than its root.
        os.chdir(self.test.workpath(""))
        self.fs = SCons.Node.FS.FS()

    def tearDown(self):
        os.chdir(self.save_cwd)

class VariantDirTestCase(unittest.TestCase):
    def runTest(self):
        """Test variant dir functionality"""
        test=TestCmd(workdir='')

        fs = SCons.Node.FS.FS()
        f1 = fs.File('build/test1')
        fs.VariantDir('build', 'src')
        f2 = fs.File('build/test2')
        d1 = fs.Dir('build')
        assert f1.srcnode().get_internal_path() == os.path.normpath('src/test1'), f1.srcnode().get_internal_path()
        assert f2.srcnode().get_internal_path() == os.path.normpath('src/test2'), f2.srcnode().get_internal_path()
        assert d1.srcnode().get_internal_path() == 'src', d1.srcnode().get_internal_path()

        fs = SCons.Node.FS.FS()
        f1 = fs.File('build/test1')
        fs.VariantDir('build', '.')
        f2 = fs.File('build/test2')
        d1 = fs.Dir('build')
        assert f1.srcnode().get_internal_path() == 'test1', f1.srcnode().get_internal_path()
        assert f2.srcnode().get_internal_path() == 'test2', f2.srcnode().get_internal_path()
        assert d1.srcnode().get_internal_path() == '.', d1.srcnode().get_internal_path()

        fs = SCons.Node.FS.FS()
        fs.VariantDir('build/var1', 'src')
        fs.VariantDir('build/var2', 'src')
        f1 = fs.File('build/var1/test1')
        f2 = fs.File('build/var2/test1')
        assert f1.srcnode().get_internal_path() == os.path.normpath('src/test1'), f1.srcnode().get_internal_path()
        assert f2.srcnode().get_internal_path() == os.path.normpath('src/test1'), f2.srcnode().get_internal_path()

        fs = SCons.Node.FS.FS()
        fs.VariantDir('../var1', 'src')
        fs.VariantDir('../var2', 'src')
        f1 = fs.File('../var1/test1')
        f2 = fs.File('../var2/test1')
        assert f1.srcnode().get_internal_path() == os.path.normpath('src/test1'), f1.srcnode().get_internal_path()
        assert f2.srcnode().get_internal_path() == os.path.normpath('src/test1'), f2.srcnode().get_internal_path()

        # Set up some files
        test.subdir('work', ['work', 'src'])
        test.subdir(['work', 'build'], ['work', 'build', 'var1'])
        test.subdir(['work', 'build', 'var2'])
        test.subdir('rep1', ['rep1', 'src'])
        test.subdir(['rep1', 'build'], ['rep1', 'build', 'var1'])
        test.subdir(['rep1', 'build', 'var2'])

        # A source file in the source directory
        test.write([ 'work', 'src', 'test.in' ], 'test.in')

        # A source file in a subdir of the source directory
        test.subdir([ 'work', 'src', 'new_dir' ])
        test.write([ 'work', 'src', 'new_dir', 'test9.out' ], 'test9.out\n')

        # A source file in the repository
        test.write([ 'rep1', 'src', 'test2.in' ], 'test2.in')

        # Some source files in the variant directory
        test.write([ 'work', 'build', 'var2', 'test.in' ], 'test.old')
        test.write([ 'work', 'build', 'var2', 'test2.in' ], 'test2.old')

        # An old derived file in the variant directories
        test.write([ 'work', 'build', 'var1', 'test.out' ], 'test.old')
        test.write([ 'work', 'build', 'var2', 'test.out' ], 'test.old')

        # And just in case we are weird, a derived file in the source
        # dir.
        test.write([ 'work', 'src', 'test.out' ], 'test.out.src')

        # A derived file in the repository
        test.write([ 'rep1', 'build', 'var1', 'test2.out' ], 'test2.out_rep')
        test.write([ 'rep1', 'build', 'var2', 'test2.out' ], 'test2.out_rep')

        os.chdir(test.workpath('work'))

        fs = SCons.Node.FS.FS(test.workpath('work'))
        fs.VariantDir('build/var1', 'src', duplicate=0)
        fs.VariantDir('build/var2', 'src')
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

        assert f1.srcnode().get_internal_path() == os.path.normpath('src/test.in'),\
               f1.srcnode().get_internal_path()
        # str(node) returns source path for duplicate = 0
        assert str(f1) == os.path.normpath('src/test.in'), str(f1)
        # Build path does not exist
        assert not f1.exists()
        # ...but the actual file is not there...
        assert not os.path.exists(f1.get_abspath())
        # And duplicate=0 should also work just like a Repository
        assert f1.rexists()
        # rfile() should point to the source path
        assert f1.rfile().get_internal_path() == os.path.normpath('src/test.in'),\
               f1.rfile().get_internal_path()

        assert f2.srcnode().get_internal_path() == os.path.normpath('src/test.in'),\
               f2.srcnode().get_internal_path()
        # str(node) returns build path for duplicate = 1
        assert str(f2) == os.path.normpath('build/var2/test.in'), str(f2)
        # Build path exists
        assert f2.exists()
        # ...and exists() should copy the file from src to build path
        assert test.read(['work', 'build', 'var2', 'test.in']) == bytearray('test.in','utf-8'),\
               test.read(['work', 'build', 'var2', 'test.in'])
        # Since exists() is true, so should rexists() be
        assert f2.rexists()

        f3 = fs.File('build/var1/test2.in')
        f4 = fs.File('build/var2/test2.in')

        assert f3.srcnode().get_internal_path() == os.path.normpath('src/test2.in'),\
               f3.srcnode().get_internal_path()
        # str(node) returns source path for duplicate = 0
        assert str(f3) == os.path.normpath('src/test2.in'), str(f3)
        # Build path does not exist
        assert not f3.exists()
        # Source path does not either
        assert not f3.srcnode().exists()
        # But we do have a file in the Repository
        assert f3.rexists()
        # rfile() should point to the source path
        assert f3.rfile().get_internal_path() == os.path.normpath(test.workpath('rep1/src/test2.in')),\
               f3.rfile().get_internal_path()

        assert f4.srcnode().get_internal_path() == os.path.normpath('src/test2.in'),\
               f4.srcnode().get_internal_path()
        # str(node) returns build path for duplicate = 1
        assert str(f4) == os.path.normpath('build/var2/test2.in'), str(f4)
        # Build path should exist
        assert f4.exists()
        # ...and copy over the file into the local build path
        assert test.read(['work', 'build', 'var2', 'test2.in']) == bytearray('test2.in','utf-8')
        # should exist in repository, since exists() is true
        assert f4.rexists()
        # rfile() should point to ourselves
        assert f4.rfile().get_internal_path() == os.path.normpath('build/var2/test2.in'),\
               f4.rfile().get_internal_path()

        f5 = fs.File('build/var1/test.out')
        f6 = fs.File('build/var2/test.out')

        assert f5.exists()
        # We should not copy the file from the source dir, since this is
        # a derived file.
        assert test.read(['work', 'build', 'var1', 'test.out']) == bytearray('test.old','utf-8')

        assert f6.exists()
        # We should not copy the file from the source dir, since this is
        # a derived file.
        assert test.read(['work', 'build', 'var2', 'test.out']) == bytearray('test.old','utf-8')

        f7 = fs.File('build/var1/test2.out')
        f8 = fs.File('build/var2/test2.out')

        assert not f7.exists()
        assert f7.rexists()
        r = f7.rfile().get_internal_path()
        expect = os.path.normpath(test.workpath('rep1/build/var1/test2.out'))
        assert r == expect, (repr(r), repr(expect))

        assert not f8.exists()
        assert f8.rexists()
        assert f8.rfile().get_internal_path() == os.path.normpath(test.workpath('rep1/build/var2/test2.out')),\
               f8.rfile().get_internal_path()

        # Verify the Mkdir and Link actions are called
        d9 = fs.Dir('build/var2/new_dir')
        f9 = fs.File('build/var2/new_dir/test9.out')

        class MkdirAction(Action):
            def __init__(self, dir_made):
                self.dir_made = dir_made
            def __call__(self, target, source, env, executor=None):
                if executor:
                    target = executor.get_all_targets()
                    source = executor.get_all_sources()
                self.dir_made.extend(target)

        save_Link = SCons.Node.FS.Link
        link_made = []
        def link_func(target, source, env, link_made=link_made):
            link_made.append(target)
        SCons.Node.FS.Link = link_func

        try:
            dir_made = []
            d9.builder = Builder(fs.Dir, action=MkdirAction(dir_made))
            d9.reset_executor()
            f9.exists()
            expect = os.path.join('build', 'var2', 'new_dir')
            assert dir_made[0].get_internal_path() == expect, dir_made[0].get_internal_path()
            expect = os.path.join('build', 'var2', 'new_dir', 'test9.out')
            assert link_made[0].get_internal_path() == expect, link_made[0].get_internal_path()
            assert f9.linked
        finally:
            SCons.Node.FS.Link = save_Link

        # Test for an interesting pathological case...we have a source
        # file in a build path, but not in a source path.  This can
        # happen if you switch from duplicate=1 to duplicate=0, then
        # delete a source file.  At one time, this would cause exists()
        # to return a 1 but get_contents() to throw.
        test.write([ 'work', 'build', 'var1', 'asourcefile' ], 'stuff')
        f10 = fs.File('build/var1/asourcefile')
        assert f10.exists()
        assert f10.get_contents() == bytearray('stuff','utf-8'), f10.get_contents()

        f11 = fs.File('src/file11')
        t, m = f11.alter_targets()
        bdt = [n.get_internal_path() for n in t]
        var1_file11 = os.path.normpath('build/var1/file11')
        var2_file11 = os.path.normpath('build/var2/file11')
        assert bdt == [var1_file11, var2_file11], bdt

        f12 = fs.File('src/file12')
        f12.builder = 1
        bdt, m = f12.alter_targets()
        assert bdt == [], [n.get_internal_path() for n in bdt]

        d13 = fs.Dir('src/new_dir')
        t, m = d13.alter_targets()
        bdt = [n.get_internal_path() for n in t]
        var1_new_dir = os.path.normpath('build/var1/new_dir')
        var2_new_dir = os.path.normpath('build/var2/new_dir')
        assert bdt == [var1_new_dir, var2_new_dir], bdt

        # Test that an IOError trying to Link a src file
        # into a VariantDir ends up throwing a StopError.
        fIO = fs.File("build/var2/IOError")

        save_Link = SCons.Node.FS.Link
        def Link_IOError(target, source, env):
            raise IOError(17, "Link_IOError")
        SCons.Node.FS.Link = SCons.Action.Action(Link_IOError, None)

        test.write(['work', 'src', 'IOError'], "work/src/IOError\n")

        try:
            exc_caught = 0
            try:
                fIO.exists()
            except SCons.Errors.StopError:
                exc_caught = 1
            assert exc_caught, "Should have caught a StopError"

        finally:
            SCons.Node.FS.Link = save_Link

        # Test to see if Link() works...
        test.subdir('src','build')
        test.write('src/foo', 'src/foo\n')
        os.chmod(test.workpath('src/foo'), stat.S_IRUSR)
        SCons.Node.FS.Link(fs.File(test.workpath('build/foo')),
                           fs.File(test.workpath('src/foo')),
                           None)
        os.chmod(test.workpath('src/foo'), stat.S_IRUSR | stat.S_IWRITE)
        st=os.stat(test.workpath('build/foo'))
        assert (stat.S_IMODE(st[stat.ST_MODE]) & stat.S_IWRITE), \
               stat.S_IMODE(st[stat.ST_MODE])

        # This used to generate a UserError when we forbid the source
        # directory from being outside the top-level SConstruct dir.
        fs = SCons.Node.FS.FS()
        fs.VariantDir('build', '/test/foo')

        exc_caught = 0
        try:
            try:
                fs = SCons.Node.FS.FS()
                fs.VariantDir('build', 'build/src')
            except SCons.Errors.UserError:
                exc_caught = 1
            assert exc_caught, "Should have caught a UserError."
        finally:
            test.unlink( "src/foo" )
            test.unlink( "build/foo" )

        fs = SCons.Node.FS.FS()
        fs.VariantDir('build', 'src1')

        # Calling the same VariantDir twice should work fine.
        fs.VariantDir('build', 'src1')

        # Trying to move a variant dir to a second source dir
        # should blow up
        try:
            fs.VariantDir('build', 'src2')
        except SCons.Errors.UserError:
            pass
        else:
            assert 0, "Should have caught a UserError."

        # Test against a former bug.  Make sure we can get a repository
        # path for the variant directory itself!
        fs=SCons.Node.FS.FS(test.workpath('work'))
        test.subdir('work')
        fs.VariantDir('build/var3', 'src', duplicate=0)
        d1 = fs.Dir('build/var3')
        r = d1.rdir()
        assert r == d1, "%s != %s" % (r, d1)

        # verify the link creation attempts in file_link()
        class LinkSimulator (object):
            """A class to intercept os.[sym]link() calls and track them."""

            def __init__( self, duplicate, link, symlink, copy ) :
                self.duplicate = duplicate
                self.have = {}
                self.have['hard'] = link
                self.have['soft'] = symlink
                self.have['copy'] = copy

                self.links_to_be_called = []
                for link in self.duplicate.split('-'):
                    if self.have[link]:
                        self.links_to_be_called.append(link)

            def link_fail( self , src , dest ) :
                next_link = self.links_to_be_called.pop(0)
                assert next_link == "hard", \
                       "Wrong link order: expected %s to be called "\
                       "instead of hard" % next_link
                raise OSError( "Simulating hard link creation error." )

            def symlink_fail( self , src , dest ) :
                next_link = self.links_to_be_called.pop(0)
                assert next_link == "soft", \
                       "Wrong link order: expected %s to be called "\
                       "instead of soft" % next_link
                raise OSError( "Simulating symlink creation error." )

            def copy( self , src , dest ) :
                next_link = self.links_to_be_called.pop(0)
                assert next_link == "copy", \
                       "Wrong link order: expected %s to be called "\
                       "instead of copy" % next_link
                # copy succeeds, but use the real copy
                self.have['copy'](src, dest)
        # end class LinkSimulator

        try:
            SCons.Node.FS.set_duplicate("no-link-order")
            assert 0, "Expected exception when passing an invalid duplicate to set_duplicate"
        except SCons.Errors.InternalError:
            pass

        for duplicate in SCons.Node.FS.Valid_Duplicates:
            # save the real functions for later restoration
            try:
                real_link = os.link
            except AttributeError:
                real_link = None
            try:
                real_symlink = os.symlink
            except AttributeError:
                real_symlink = None

            # Disable symlink and link for now in win32.
            # We don't have a consistant plan to make these work as yet
            # They are only supported with PY3
            if sys.platform == 'win32':
                real_symlink = None
                real_link = None

            real_copy = shutil.copy2

            simulator = LinkSimulator(duplicate, real_link, real_symlink, real_copy)

            # override the real functions with our simulation
            os.link = simulator.link_fail
            os.symlink = simulator.symlink_fail
            shutil.copy2 = simulator.copy

            try:

                SCons.Node.FS.set_duplicate(duplicate)

                src_foo = test.workpath('src', 'foo')
                build_foo = test.workpath('build', 'foo')

                test.write(src_foo, 'src/foo\n')
                os.chmod(src_foo, stat.S_IRUSR)
                try:
                    SCons.Node.FS.Link(fs.File(build_foo),
                                       fs.File(src_foo),
                                       None)
                finally:
                    os.chmod(src_foo, stat.S_IRUSR | stat.S_IWRITE)
                    test.unlink(src_foo)
                    test.unlink(build_foo)

            finally:
                # restore the real functions
                if real_link:
                    os.link = real_link
                else:
                    delattr(os, 'link')
                if real_symlink:
                    os.symlink = real_symlink
                else:
                    delattr(os, 'symlink')
                shutil.copy2 = real_copy

        # Test VariantDir "reflection," where a same-named subdirectory
        # exists underneath a variant_dir.
        fs = SCons.Node.FS.FS()
        fs.VariantDir('work/src/b1/b2', 'work/src')

        dir_list = [
                'work/src',
                'work/src/b1',
                'work/src/b1/b2',
                'work/src/b1/b2/b1',
                'work/src/b1/b2/b1/b2',
                'work/src/b1/b2/b1/b2/b1',
                'work/src/b1/b2/b1/b2/b1/b2',
        ]

        srcnode_map = {
                'work/src/b1/b2' : 'work/src',
                'work/src/b1/b2/f' : 'work/src/f',
                'work/src/b1/b2/b1' : 'work/src/b1/',
                'work/src/b1/b2/b1/f' : 'work/src/b1/f',
                'work/src/b1/b2/b1/b2' : 'work/src/b1/b2',
                'work/src/b1/b2/b1/b2/f' : 'work/src/b1/b2/f',
                'work/src/b1/b2/b1/b2/b1' : 'work/src/b1/b2/b1',
                'work/src/b1/b2/b1/b2/b1/f' : 'work/src/b1/b2/b1/f',
                'work/src/b1/b2/b1/b2/b1/b2' : 'work/src/b1/b2/b1/b2',
                'work/src/b1/b2/b1/b2/b1/b2/f' : 'work/src/b1/b2/b1/b2/f',
        }

        alter_map = {
                'work/src' : 'work/src/b1/b2',
                'work/src/f' : 'work/src/b1/b2/f',
                'work/src/b1' : 'work/src/b1/b2/b1',
                'work/src/b1/f' : 'work/src/b1/b2/b1/f',
        }

        errors = 0

        for dir in dir_list:
            dnode = fs.Dir(dir)
            f = dir + '/f'
            fnode = fs.File(dir + '/f')

            dp = dnode.srcnode().get_internal_path()
            expect = os.path.normpath(srcnode_map.get(dir, dir))
            if dp != expect:
                print("Dir `%s' srcnode() `%s' != expected `%s'" % (dir, dp, expect))
                errors = errors + 1

            fp = fnode.srcnode().get_internal_path()
            expect = os.path.normpath(srcnode_map.get(f, f))
            if fp != expect:
                print("File `%s' srcnode() `%s' != expected `%s'" % (f, fp, expect))
                errors = errors + 1

        for dir in dir_list:
            dnode = fs.Dir(dir)
            f = dir + '/f'
            fnode = fs.File(dir + '/f')

            t, m = dnode.alter_targets()
            tp = t[0].get_internal_path()
            expect = os.path.normpath(alter_map.get(dir, dir))
            if tp != expect:
                print("Dir `%s' alter_targets() `%s' != expected `%s'" % (dir, tp, expect))
                errors = errors + 1

            t, m = fnode.alter_targets()
            tp = t[0].get_internal_path()
            expect = os.path.normpath(alter_map.get(f, f))
            if tp != expect:
                print("File `%s' alter_targets() `%s' != expected `%s'" % (f, tp, expect))
                errors = errors + 1

        self.assertFalse(errors)

class BaseTestCase(_tempdirTestCase):
    def test_stat(self):
        """Test the Base.stat() method"""
        test = self.test
        test.write("e1", "e1\n")
        fs = SCons.Node.FS.FS()

        e1 = fs.Entry('e1')
        s = e1.stat()
        assert s is not None, s

        e2 = fs.Entry('e2')
        s = e2.stat()
        assert s is None, s

    def test_getmtime(self):
        """Test the Base.getmtime() method"""
        test = self.test
        test.write("file", "file\n")
        fs = SCons.Node.FS.FS()

        file = fs.Entry('file')
        assert file.getmtime()

        file = fs.Entry('nonexistent')
        mtime = file.getmtime()
        assert mtime is None, mtime

    def test_getsize(self):
        """Test the Base.getsize() method"""
        test = self.test
        test.write("file", "file\n")
        fs = SCons.Node.FS.FS()

        file = fs.Entry('file')
        size = file.getsize()
        assert size == 5, size

        file = fs.Entry('nonexistent')
        size = file.getsize()
        assert size is None, size

    def test_isdir(self):
        """Test the Base.isdir() method"""
        test = self.test
        test.subdir('dir')
        test.write("file", "file\n")
        fs = SCons.Node.FS.FS()

        dir = fs.Entry('dir')
        assert dir.isdir()

        file = fs.Entry('file')
        assert not file.isdir()

        nonexistent = fs.Entry('nonexistent')
        assert not nonexistent.isdir()

    def test_isfile(self):
        """Test the Base.isfile() method"""
        test = self.test
        test.subdir('dir')
        test.write("file", "file\n")
        fs = SCons.Node.FS.FS()

        dir = fs.Entry('dir')
        assert not dir.isfile()

        file = fs.Entry('file')
        assert file.isfile()

        nonexistent = fs.Entry('nonexistent')
        assert not nonexistent.isfile()

    if sys.platform != 'win32' and hasattr(os, 'symlink'):
        def test_islink(self):
            """Test the Base.islink() method"""
            test = self.test
            test.subdir('dir')
            test.write("file", "file\n")
            test.symlink("symlink", "symlink")
            fs = SCons.Node.FS.FS()

            dir = fs.Entry('dir')
            assert not dir.islink()

            file = fs.Entry('file')
            assert not file.islink()

            symlink = fs.Entry('symlink')
            assert symlink.islink()

            nonexistent = fs.Entry('nonexistent')
            assert not nonexistent.islink()

class DirNodeInfoTestCase(_tempdirTestCase):
    def test___init__(self):
        """Test DirNodeInfo initialization"""
        ddd = self.fs.Dir('ddd')
        ni = SCons.Node.FS.DirNodeInfo()

class DirBuildInfoTestCase(_tempdirTestCase):
    def test___init__(self):
        """Test DirBuildInfo initialization"""
        ddd = self.fs.Dir('ddd')
        bi = SCons.Node.FS.DirBuildInfo()

class FileNodeInfoTestCase(_tempdirTestCase):
    def test___init__(self):
        """Test FileNodeInfo initialization"""
        fff = self.fs.File('fff')
        ni = SCons.Node.FS.FileNodeInfo()
        assert isinstance(ni, SCons.Node.FS.FileNodeInfo)

    def test_update(self):
        """Test updating a File.NodeInfo with on-disk information"""
        test = self.test
        fff = self.fs.File('fff')

        ni = SCons.Node.FS.FileNodeInfo()

        test.write('fff', "fff\n")

        st = os.stat('fff')

        ni.update(fff)

        assert hasattr(ni, 'timestamp')
        assert hasattr(ni, 'size')

        ni.timestamp = 0
        ni.size = 0

        ni.update(fff)

        mtime = st[stat.ST_MTIME]
        assert ni.timestamp == mtime, (ni.timestamp, mtime)
        size = st[stat.ST_SIZE]
        assert ni.size == size, (ni.size, size)

        import time
        time.sleep(2)

        test.write('fff', "fff longer size, different time stamp\n")

        st = os.stat('fff')

        mtime = st[stat.ST_MTIME]
        assert ni.timestamp != mtime, (ni.timestamp, mtime)
        size = st[stat.ST_SIZE]
        assert ni.size != size, (ni.size, size)

class FileBuildInfoTestCase(_tempdirTestCase):
    def test___init__(self):
        """Test File.BuildInfo initialization"""
        fff = self.fs.File('fff')
        bi = SCons.Node.FS.FileBuildInfo()
        assert bi, bi

    def test_convert_to_sconsign(self):
        """Test converting to .sconsign file format"""
        fff = self.fs.File('fff')
        bi = SCons.Node.FS.FileBuildInfo()
        assert hasattr(bi, 'convert_to_sconsign')

    def test_convert_from_sconsign(self):
        """Test converting from .sconsign file format"""
        fff = self.fs.File('fff')
        bi = SCons.Node.FS.FileBuildInfo()
        assert hasattr(bi, 'convert_from_sconsign')

    def test_prepare_dependencies(self):
        """Test that we have a prepare_dependencies() method"""
        fff = self.fs.File('fff')
        bi = SCons.Node.FS.FileBuildInfo()
        bi.prepare_dependencies()

    def test_format(self):
        """Test the format() method"""
        f1 = self.fs.File('f1')
        bi1 = SCons.Node.FS.FileBuildInfo()

        self.fs.File('n1')
        self.fs.File('n2')
        self.fs.File('n3')

        s1sig = SCons.Node.FS.FileNodeInfo()
        s1sig.csig = 1
        d1sig = SCons.Node.FS.FileNodeInfo()
        d1sig.timestamp = 2
        i1sig = SCons.Node.FS.FileNodeInfo()
        i1sig.size = 3

        bi1.bsources = [self.fs.File('s1')]
        bi1.bdepends = [self.fs.File('d1')]
        bi1.bimplicit = [self.fs.File('i1')]
        bi1.bsourcesigs = [s1sig]
        bi1.bdependsigs = [d1sig]
        bi1.bimplicitsigs = [i1sig]
        bi1.bact = 'action'
        bi1.bactsig = 'actionsig'

        expect_lines = [
            's1: 1 None None',
            'd1: None 2 None',
            'i1: None None 3',
            'actionsig [action]',
        ]

        expect = '\n'.join(expect_lines)
        format = bi1.format()
        assert format == expect, (repr(expect), repr(format))

class FSTestCase(_tempdirTestCase):
    def test_needs_normpath(self):
        """Test the needs_normpath Regular expression

        This test case verifies that the regular expression used to
        determine whether a path needs normalization works as
        expected.
        """
        needs_normpath_match = SCons.Node.FS.needs_normpath_match

        do_not_need_normpath = [
            ".",
            "/",
            "/a",
            "/aa",
            "/a/",
            "/aa/",
            "/a/b",
            "/aa/bb",
            "/a/b/",
            "/aa/bb/",

            "",
            "a",
            "aa",
            "a/",
            "aa/",
            "a/b",
            "aa/bb",
            "a/b/",
            "aa/bb/",

            "a.",
            "a..",
            "/a.",
            "/a..",
            "a./",
            "a../",
            "/a./",
            "/a../",


            ".a",
            "..a",
            "/.a",
            "/..a",
            ".a/",
            "..a/",
            "/.a/",
            "/..a/",
            ]
        for p in do_not_need_normpath:
            assert needs_normpath_match(p) is None, p

        needs_normpath = [
            "//",
            "//a",
            "//aa",
            "//a/",
            "//a/",
            "/aa//",

            "//a/b",
            "//aa/bb",
            "//a/b/",
            "//aa/bb/",

            "/a//b",
            "/aa//bb",
            "/a/b//",
            "/aa/bb//",

            "/a/b//",
            "/aa/bb//",

            "a//",
            "aa//",
            "a//b",
            "aa//bb",
            "a//b/",
            "aa//bb/",
            "a/b//",
            "aa/bb//",

            "..",
            "/.",
            "/..",
            "./",
            "../",
            "/./",
            "/../",

            "a/.",
            "a/..",
            "./a",
            "../a",
            "a/./a",
            "a/../a",
            ]
        for p in needs_normpath:
            assert needs_normpath_match(p) is not None, p

    def test_runTest(self):
        """Test FS (file system) Node operations

        This test case handles all of the file system node
        tests in one environment, so we don't have to set up a
        complicated directory structure for each test individually.
        """
        test = self.test

        test.subdir('sub', ['sub', 'dir'])

        wp = test.workpath('')
        sub = test.workpath('sub', '')
        sub_dir = test.workpath('sub', 'dir', '')
        sub_dir_foo = test.workpath('sub', 'dir', 'foo', '')
        sub_dir_foo_bar = test.workpath('sub', 'dir', 'foo', 'bar', '')
        sub_foo = test.workpath('sub', 'foo', '')

        os.chdir(sub_dir)

        fs = SCons.Node.FS.FS()

        e1 = fs.Entry('e1')
        assert isinstance(e1, SCons.Node.FS.Entry)

        d1 = fs.Dir('d1')
        assert isinstance(d1, SCons.Node.FS.Dir)
        assert d1.cwd is d1, d1

        f1 = fs.File('f1', directory = d1)
        assert isinstance(f1, SCons.Node.FS.File)

        d1_f1 = os.path.join('d1', 'f1')
        assert f1.get_internal_path() == d1_f1, "f1.path %s != %s" % (f1.get_internal_path(), d1_f1)
        assert str(f1) == d1_f1, "str(f1) %s != %s" % (str(f1), d1_f1)

        x1 = d1.File('x1')
        assert isinstance(x1, SCons.Node.FS.File)
        assert str(x1) == os.path.join('d1', 'x1')

        x2 = d1.Dir('x2')
        assert isinstance(x2, SCons.Node.FS.Dir)
        assert str(x2) == os.path.join('d1', 'x2')

        x3 = d1.Entry('x3')
        assert isinstance(x3, SCons.Node.FS.Entry)
        assert str(x3) == os.path.join('d1', 'x3')

        assert d1.File(x1) == x1
        assert d1.Dir(x2) == x2
        assert d1.Entry(x3) == x3

        x1.cwd = d1

        x4 = x1.File('x4')
        assert str(x4) == os.path.join('d1', 'x4')

        x5 = x1.Dir('x5')
        assert str(x5) == os.path.join('d1', 'x5')

        x6 = x1.Entry('x6')
        assert str(x6) == os.path.join('d1', 'x6')
        x7 = x1.Entry('x7')
        assert str(x7) == os.path.join('d1', 'x7')

        assert x1.File(x4) == x4
        assert x1.Dir(x5) == x5
        assert x1.Entry(x6) == x6
        assert x1.Entry(x7) == x7

        assert x1.Entry(x5) == x5
        try:
            x1.File(x5)
        except TypeError:
            pass
        else:
            raise Exception("did not catch expected TypeError")

        assert x1.Entry(x4) == x4
        try:
            x1.Dir(x4)
        except TypeError:
            pass
        else:
            raise Exception("did not catch expected TypeError")

        x6 = x1.File(x6)
        assert isinstance(x6, SCons.Node.FS.File)

        x7 = x1.Dir(x7)
        assert isinstance(x7, SCons.Node.FS.Dir)

        seps = [os.sep]
        if os.sep != '/':
            seps = seps + ['/']

        drive, path = os.path.splitdrive(os.getcwd())

        def _do_Dir_test(lpath, path_, abspath_, up_path_, sep, fileSys=fs, drive=drive):
            dir = fileSys.Dir(lpath.replace('/', sep))

            if os.sep != '/':
                path_ = path_.replace('/', os.sep)
                abspath_ = abspath_.replace('/', os.sep)
                up_path_ = up_path_.replace('/', os.sep)

            def strip_slash(p, drive=drive):
                if p[-1] == os.sep and len(p) > 1:
                    p = p[:-1]
                if p[0] == os.sep:
                    p = drive + p
                return p
            path = strip_slash(path_)
            abspath = strip_slash(abspath_)
            up_path = strip_slash(up_path_)

            name = abspath.split(os.sep)[-1]

            if not name:
                if drive:
                    name = drive
                else:
                    name = os.sep

            if dir.up() is None:
                dir_up_path =  dir.get_internal_path()
            else:
                dir_up_path =  dir.up().get_internal_path()

            assert dir.name == name, \
                   "dir.name %s != expected name %s" % \
                   (dir.name, name)
            assert dir.get_internal_path() == path, \
                   "dir.path %s != expected path %s" % \
                   (dir.get_internal_path(), path)
            assert str(dir) == path, \
                   "str(dir) %s != expected path %s" % \
                   (str(dir), path)
            assert dir.get_abspath() == abspath, \
                   "dir.abspath %s != expected absolute path %s" % \
                   (dir.get_abspath(), abspath)
            assert dir_up_path == up_path, \
                   "dir.up().path %s != expected parent path %s" % \
                   (dir_up_path, up_path)

        for sep in seps:

            def Dir_test(lpath, path_, abspath_, up_path_, sep=sep, func=_do_Dir_test):
                return func(lpath, path_, abspath_, up_path_, sep)
            
            Dir_test('/',           '/',           '/',               '/')
            Dir_test('',            './',          sub_dir,           sub)
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
                f2 = fs.File(sep.join(['f1', 'f2']), directory = d1)
            except TypeError as x:
                assert str(x) == ("Tried to lookup File '%s' as a Dir." %
                                  d1_f1), x
            except:
                raise

            try:
                dir = fs.Dir(sep.join(['d1', 'f1']))
            except TypeError as x:
                assert str(x) == ("Tried to lookup File '%s' as a Dir." %
                                  d1_f1), x
            except:
                raise

            try:
                f2 = fs.File('d1')
            except TypeError as x:
                assert str(x) == ("Tried to lookup Dir '%s' as a File." %
                                  'd1'), x
            except:
                raise

        # Test that just specifying the drive works to identify
        # its root directory.
        p = os.path.abspath(test.workpath('root_file'))
        drive, path = os.path.splitdrive(p)
        if drive:
            # The assert below probably isn't correct for the general
            # case, but it works for Windows, which covers a lot
            # of ground...
            dir = fs.Dir(drive)
            assert str(dir) == drive + os.sep, str(dir)

            # Make sure that lookups with and without the drive are
            # equivalent.
            p = os.path.abspath(test.workpath('some/file'))
            drive, path = os.path.splitdrive(p)

            e1 = fs.Entry(p)
            e2 = fs.Entry(path)
            assert e1 is e2, (e1, e2)
            assert str(e1) is str(e2), (str(e1), str(e2))

        # Test for a bug in 0.04 that did not like looking up
        # dirs with a trailing slash on Windows.
        d=fs.Dir('./')
        assert d.get_internal_path() == '.', d.get_abspath()
        d=fs.Dir('foo/')
        assert d.get_internal_path() == 'foo', d.get_abspath()

        # Test for sub-classing of node building.
        global built_it

        built_it = None
        assert not built_it
        d1.add_source([SCons.Node.Node()])    # XXX FAKE SUBCLASS ATTRIBUTE
        d1.builder_set(Builder(fs.File))
        d1.reset_executor()
        d1.env_set(Environment())
        d1.build()
        assert built_it

        built_it = None
        assert not built_it
        f1.add_source([SCons.Node.Node()])    # XXX FAKE SUBCLASS ATTRIBUTE
        f1.builder_set(Builder(fs.File))
        f1.reset_executor()
        f1.env_set(Environment())
        f1.build()
        assert built_it

        def match(path, expect):
            expect = expect.replace('/', os.sep)
            assert path == expect, "path %s != expected %s" % (path, expect)

        e1 = fs.Entry("d1")
        assert e1.__class__.__name__ == 'Dir'
        match(e1.get_internal_path(), "d1")
        match(e1.dir.get_internal_path(), ".")

        e2 = fs.Entry("d1/f1")
        assert e2.__class__.__name__ == 'File'
        match(e2.get_internal_path(), "d1/f1")
        match(e2.dir.get_internal_path(), "d1")

        e3 = fs.Entry("e3")
        assert e3.__class__.__name__ == 'Entry'
        match(e3.get_internal_path(), "e3")
        match(e3.dir.get_internal_path(), ".")

        e4 = fs.Entry("d1/e4")
        assert e4.__class__.__name__ == 'Entry'
        match(e4.get_internal_path(), "d1/e4")
        match(e4.dir.get_internal_path(), "d1")

        e5 = fs.Entry("e3/e5")
        assert e3.__class__.__name__ == 'Dir'
        match(e3.get_internal_path(), "e3")
        match(e3.dir.get_internal_path(), ".")
        assert e5.__class__.__name__ == 'Entry'
        match(e5.get_internal_path(), "e3/e5")
        match(e5.dir.get_internal_path(), "e3")

        e6 = fs.Dir("d1/e4")
        assert e6 is e4
        assert e4.__class__.__name__ == 'Dir'
        match(e4.get_internal_path(), "d1/e4")
        match(e4.dir.get_internal_path(), "d1")

        e7 = fs.File("e3/e5")
        assert e7 is e5
        assert e5.__class__.__name__ == 'File'
        match(e5.get_internal_path(), "e3/e5")
        match(e5.dir.get_internal_path(), "e3")

        fs.chdir(fs.Dir('subdir'))
        f11 = fs.File("f11")
        match(f11.get_internal_path(), "subdir/f11")
        d12 = fs.Dir("d12")
        e13 = fs.Entry("subdir/e13")
        match(e13.get_internal_path(), "subdir/subdir/e13")
        fs.chdir(fs.Dir('..'))

        # Test scanning
        f1.builder_set(Builder(fs.File))
        f1.env_set(Environment())
        xyz = fs.File("xyz")
        f1.builder.target_scanner = Scanner(xyz)

        f1.scan()
        assert f1.implicit[0].get_internal_path() == "xyz"
        f1.implicit = []
        f1.scan()
        assert f1.implicit == []
        f1.implicit = None
        f1.scan()
        assert f1.implicit[0].get_internal_path() == "xyz"

        # Test underlying scanning functionality in get_found_includes()
        env = Environment()
        f12 = fs.File("f12")
        t1 = fs.File("t1")

        deps = f12.get_found_includes(env, None, t1)
        assert deps == [], deps

        class MyScanner(Scanner):
            call_count = 0
            def __call__(self, node, env, path):
                self.call_count = self.call_count + 1
                return Scanner.__call__(self, node, env, path)
        s = MyScanner(xyz)

        deps = f12.get_found_includes(env, s, t1)
        assert deps == [xyz], deps
        assert s.call_count == 1, s.call_count

        f12.built()

        deps = f12.get_found_includes(env, s, t1)
        assert deps == [xyz], deps
        assert s.call_count == 2, s.call_count

        env2 = Environment()

        deps = f12.get_found_includes(env2, s, t1)
        assert deps == [xyz], deps
        assert s.call_count == 3, s.call_count



        # Make sure we can scan this file even if the target isn't
        # a file that has a scanner (it might be an Alias, e.g.).
        class DummyNode(object):
            pass

        deps = f12.get_found_includes(env, s, DummyNode())
        assert deps == [xyz], deps

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
        # The cwd's path is always "."
        assert str(fs.getcwd()) == ".", str(fs.getcwd())
        assert fs.getcwd().get_internal_path() == 'subdir', fs.getcwd().get_internal_path()
        fs.chdir(fs.Dir('../..'))
        assert fs.getcwd().get_internal_path() == test.workdir, fs.getcwd().get_internal_path()

        f1 = fs.File(test.workpath("do_i_exist"))
        assert not f1.exists()
        test.write("do_i_exist","\n")
        assert not f1.exists(), "exists() call not cached"
        f1.built()
        assert f1.exists(), "exists() call caching not reset"
        test.unlink("do_i_exist")
        assert f1.exists()
        f1.built()
        assert not f1.exists()

        # For some reason, in Windows, the \x1a character terminates
        # the reading of files in text mode.  This tests that
        # get_contents() returns the binary contents.
        test.write("binary_file", "Foo\x1aBar")
        f1 = fs.File(test.workpath("binary_file"))
        assert f1.get_contents() == bytearray("Foo\x1aBar",'utf-8'), f1.get_contents()

        # This tests to make sure we can decode UTF-8 text files.
        test_string = u"Foo\x1aBar"
        test.write("utf8_file", test_string.encode('utf-8'))
        f1 = fs.File(test.workpath("utf8_file"))
        assert eval('f1.get_text_contents() == u"Foo\x1aBar"'), \
               f1.get_text_contents()

        # Check for string which doesn't have BOM and isn't valid
        # ASCII
        test_string = b'Gan\xdfauge'
        test.write('latin1_file', test_string)
        f1 = fs.File(test.workpath("latin1_file"))
        assert f1.get_text_contents() == test_string.decode('latin-1'), \
               f1.get_text_contents()

        def nonexistent(method, s):
            try:
                x = method(s, create = 0)
            except SCons.Errors.UserError:
                pass
            else:
                raise Exception("did not catch expected UserError")

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
        f1.builder = Builder(fs.File)
        f1.env_set(Environment())
        f1.prepare()
        assert not os.path.exists(test.workpath("remove_me"))

        e = fs.Entry('e_local')
        assert not hasattr(e, '_local')
        e.set_local()
        assert e._local == 1
        f = fs.File('e_local')
        assert f._local == 1
        f = fs.File('f_local')
        assert f._local == 0

        #XXX test_is_up_to_date() for directories

        #XXX test_sconsign() for directories

        #XXX test_set_signature() for directories

        #XXX test_build() for directories

        #XXX test_root()

        # test Entry.get_contents()
        e = fs.Entry('does_not_exist')
        c = e.get_contents()
        assert c == "", c
        assert e.__class__ == SCons.Node.FS.Entry

        test.write("file", "file\n")
        try:
            e = fs.Entry('file')
            c = e.get_contents()
            assert c == bytearray("file\n",'utf-8'), c
            assert e.__class__ == SCons.Node.FS.File
        finally:
            test.unlink("file")

        # test Entry.get_text_contents()
        e = fs.Entry('does_not_exist')
        c = e.get_text_contents()
        assert c == "", c
        assert e.__class__ == SCons.Node.FS.Entry

        test.write("file", "file\n")
        try:
            e = fs.Entry('file')
            c = e.get_text_contents()
            assert c == "file\n", c
            assert e.__class__ == SCons.Node.FS.File
        finally:
            test.unlink("file")

        test.subdir("dir")
        e = fs.Entry('dir')
        c = e.get_contents()
        assert c == "", c
        assert e.__class__ == SCons.Node.FS.Dir

        c = e.get_text_contents()
        try:
            eval('assert c == u"", c')
        except SyntaxError:
            assert c == ""

        if sys.platform != 'win32' and hasattr(os, 'symlink'):
            os.symlink('nonexistent', test.workpath('dangling_symlink'))
            e = fs.Entry('dangling_symlink')
            c = e.get_contents()
            assert e.__class__ == SCons.Node.FS.Entry, e.__class__
            assert c == "", c
            c = e.get_text_contents()
            try:
                eval('assert c == u"", c')
            except SyntaxError:
                assert c == "", c

        test.write("tstamp", "tstamp\n")
        try:
            # Okay, *this* manipulation accomodates Windows FAT file systems
            # that only have two-second granularity on their timestamps.
            # We round down the current time to the nearest even integer
            # value, subtract two to make sure the timestamp is not "now,"
            # and then convert it back to a float.
            tstamp = float(int(time.time() // 2) * 2) - 2.0
            os.utime(test.workpath("tstamp"), (tstamp - 2.0, tstamp))
            f = fs.File("tstamp")
            t = f.get_timestamp()
            assert t == tstamp, "expected %f, got %f" % (tstamp, t)
        finally:
            test.unlink("tstamp")

        test.subdir('tdir1')
        d = fs.Dir('tdir1')
        t = d.get_timestamp()
        assert t == 0, "expected 0, got %s" % str(t)

        test.subdir('tdir2')
        f1 = test.workpath('tdir2', 'file1')
        f2 = test.workpath('tdir2', 'file2')
        test.write(f1, 'file1\n')
        test.write(f2, 'file2\n')
        current_time = float(int(time.time() // 2) * 2)
        t1 = current_time - 4.0
        t2 = current_time - 2.0
        os.utime(f1, (t1 - 2.0, t1))
        os.utime(f2, (t2 - 2.0, t2))
        d = fs.Dir('tdir2')
        fs.File(f1)
        fs.File(f2)
        t = d.get_timestamp()
        assert t == t2, "expected %f, got %f" % (t2, t)

        skey = fs.Entry('eee.x').scanner_key()
        assert skey == '.x', skey
        skey = fs.Entry('eee.xyz').scanner_key()
        assert skey == '.xyz', skey

        skey = fs.File('fff.x').scanner_key()
        assert skey == '.x', skey
        skey = fs.File('fff.xyz').scanner_key()
        assert skey == '.xyz', skey

        skey = fs.Dir('ddd.x').scanner_key()
        assert skey is None, skey

        test.write("i_am_not_a_directory", "\n")
        try:
            exc_caught = 0
            try:
                fs.Dir(test.workpath("i_am_not_a_directory"))
            except TypeError:
                exc_caught = 1
            assert exc_caught, "Should have caught a TypeError"
        finally:
            test.unlink("i_am_not_a_directory")

        exc_caught = 0
        try:
            fs.File(sub_dir)
        except TypeError:
            exc_caught = 1
        assert exc_caught, "Should have caught a TypeError"

        # XXX test_is_up_to_date()

        d = fs.Dir('dir')
        r = d.remove()
        assert r is None, r

        f = fs.File('does_not_exist')
        r = f.remove()
        assert r is None, r

        test.write('exists', "exists\n")
        f = fs.File('exists')
        r = f.remove()
        assert r, r
        assert not os.path.exists(test.workpath('exists')), "exists was not removed"

        if sys.platform != 'win32' and hasattr(os, 'symlink'):
            symlink = test.workpath('symlink')
            os.symlink(test.workpath('does_not_exist'), symlink)
            assert os.path.islink(symlink)
            f = fs.File('symlink')
            r = f.remove()
            assert r, r
            assert not os.path.islink(symlink), "symlink was not removed"

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

        f = fs.Entry('foo/bar/baz')
        assert f.for_signature() == 'baz', f.for_signature()
        assert f.get_string(0) == os.path.normpath('foo/bar/baz'), \
               f.get_string(0)
        assert f.get_string(1) == 'baz', f.get_string(1)

    def test_drive_letters(self):
        """Test drive-letter look-ups"""

        test = self.test

        test.subdir('sub', ['sub', 'dir'])

        def drive_workpath(dirs, test=test):
            x = test.workpath(*dirs)
            drive, path = os.path.splitdrive(x)
            return 'X:' + path

        wp              = drive_workpath([''])

        if wp[-1] in (os.sep, '/'):
            tmp         = os.path.split(wp[:-1])[0]
        else:
            tmp         = os.path.split(wp)[0]

        parent_tmp      = os.path.split(tmp)[0]
        if parent_tmp == 'X:':
            parent_tmp = 'X:' + os.sep

        tmp_foo         = os.path.join(tmp, 'foo')

        foo             = drive_workpath(['foo'])
        foo_bar         = drive_workpath(['foo', 'bar'])
        sub             = drive_workpath(['sub', ''])
        sub_dir         = drive_workpath(['sub', 'dir', ''])
        sub_dir_foo     = drive_workpath(['sub', 'dir', 'foo', ''])
        sub_dir_foo_bar = drive_workpath(['sub', 'dir', 'foo', 'bar', ''])
        sub_foo         = drive_workpath(['sub', 'foo', ''])

        fs = SCons.Node.FS.FS()

        seps = [os.sep]
        if os.sep != '/':
            seps = seps + ['/']

        def _do_Dir_test(lpath, path_, up_path_, sep, fileSys=fs):
            dir = fileSys.Dir(lpath.replace('/', sep))

            if os.sep != '/':
                path_ = path_.replace('/', os.sep)
                up_path_ = up_path_.replace('/', os.sep)

            def strip_slash(p):
                if p[-1] == os.sep and len(p) > 3:
                    p = p[:-1]
                return p
            path = strip_slash(path_)
            up_path = strip_slash(up_path_)
            name = path.split(os.sep)[-1]

            assert dir.name == name, \
                   "dir.name %s != expected name %s" % \
                   (dir.name, name)
            assert dir.get_internal_path() == path, \
                   "dir.path %s != expected path %s" % \
                   (dir.get_internal_path(), path)
            assert str(dir) == path, \
                   "str(dir) %s != expected path %s" % \
                   (str(dir), path)
            assert dir.up().get_internal_path() == up_path, \
                   "dir.up().path %s != expected parent path %s" % \
                   (dir.up().get_internal_path(), up_path)

        save_os_path = os.path
        save_os_sep = os.sep
        try:
            import ntpath
            os.path = ntpath
            os.sep = '\\'
            SCons.Node.FS.initialize_do_splitdrive()

            for sep in seps:

                def Dir_test(lpath, path_, up_path_, sep=sep, func=_do_Dir_test):
                    return func(lpath, path_, up_path_, sep)

                Dir_test('#X:',         wp,             tmp)
                Dir_test('X:foo',       foo,            wp)
                Dir_test('X:foo/bar',   foo_bar,        foo)
                Dir_test('X:/foo',      'X:/foo',       'X:/')
                Dir_test('X:/foo/bar',  'X:/foo/bar/',  'X:/foo/')
                Dir_test('X:..',        tmp,            parent_tmp)
                Dir_test('X:foo/..',    wp,             tmp)
                Dir_test('X:../foo',    tmp_foo,        tmp)
                Dir_test('X:.',         wp,             tmp)
                Dir_test('X:./.',       wp,             tmp)
                Dir_test('X:foo/./bar', foo_bar,        foo)
                Dir_test('#X:../foo',   tmp_foo,        tmp)
                Dir_test('#X:/../foo',  tmp_foo,        tmp)
                Dir_test('#X:foo/bar',  foo_bar,        foo)
                Dir_test('#X:/foo/bar', foo_bar,        foo)
                Dir_test('#X:/',        wp,             tmp)
        finally:
            os.path = save_os_path
            os.sep = save_os_sep
            SCons.Node.FS.initialize_do_splitdrive()

    def test_unc_path(self):
        """Test UNC path look-ups"""

        test = self.test

        test.subdir('sub', ['sub', 'dir'])

        def strip_slash(p):
            if p[-1] == os.sep and len(p) > 3:
                p = p[:-1]
            return p

        def unc_workpath(dirs, test=test):
            import ntpath
            x = test.workpath(*dirs)
            drive, path = ntpath.splitdrive(x)
            try:
                unc, path = ntpath.splitunc(path)
            except AttributeError:
                # could be python 3.7 or newer, make sure splitdrive can do UNC
                assert ntpath.splitdrive(r'\\split\drive\test')[0] == r'\\split\drive'
                pass
            path = strip_slash(path)
            return '//' + path[1:]

        wp              = unc_workpath([''])

        if wp[-1] in (os.sep, '/'):
            tmp         = os.path.split(wp[:-1])[0]
        else:
            tmp         = os.path.split(wp)[0]

        parent_tmp      = os.path.split(tmp)[0]

        tmp_foo         = os.path.join(tmp, 'foo')

        foo             = unc_workpath(['foo'])
        foo_bar         = unc_workpath(['foo', 'bar'])
        sub             = unc_workpath(['sub', ''])
        sub_dir         = unc_workpath(['sub', 'dir', ''])
        sub_dir_foo     = unc_workpath(['sub', 'dir', 'foo', ''])
        sub_dir_foo_bar = unc_workpath(['sub', 'dir', 'foo', 'bar', ''])
        sub_foo         = unc_workpath(['sub', 'foo', ''])

        fs = SCons.Node.FS.FS()

        seps = [os.sep]
        if os.sep != '/':
            seps = seps + ['/']

        def _do_Dir_test(lpath, path, up_path, sep, fileSys=fs):
            dir = fileSys.Dir(lpath.replace('/', sep))

            if os.sep != '/':
                path = path.replace('/', os.sep)
                up_path = up_path.replace('/', os.sep)

            if path == os.sep + os.sep:
                name = os.sep + os.sep
            else:
                name = path.split(os.sep)[-1]

            if dir.up() is None:
                dir_up_path =  dir.get_internal_path()
            else:
                dir_up_path =  dir.up().get_internal_path()

            assert dir.name == name, \
                   "dir.name %s != expected name %s" % \
                   (dir.name, name)
            assert dir.get_internal_path() == path, \
                   "dir.path %s != expected path %s" % \
                   (dir.get_internal_path(), path)
            assert str(dir) == path, \
                   "str(dir) %s != expected path %s" % \
                   (str(dir), path)
            assert dir_up_path == up_path, \
                   "dir.up().path %s != expected parent path %s" % \
                   (dir.up().get_internal_path(), up_path)

        save_os_path = os.path
        save_os_sep = os.sep
        try:
            import ntpath
            os.path = ntpath
            os.sep = '\\'
            SCons.Node.FS.initialize_do_splitdrive()

            for sep in seps:

                def Dir_test(lpath, path_, up_path_, sep=sep, func=_do_Dir_test):
                    return func(lpath, path_, up_path_, sep)

                Dir_test('//foo',           '//foo',       '//')
                Dir_test('//foo/bar',       '//foo/bar',   '//foo')
                Dir_test('//',              '//',          '//')
                Dir_test('//..',            '//',          '//')
                Dir_test('//foo/..',        '//',          '//')
                Dir_test('//../foo',        '//foo',       '//')
                Dir_test('//.',             '//',          '//')
                Dir_test('//./.',           '//',          '//')
                Dir_test('//foo/./bar',     '//foo/bar',   '//foo')
                Dir_test('//foo/../bar',    '//bar',       '//')
                Dir_test('//foo/../../bar', '//bar',       '//')
                Dir_test('//foo/bar/../..', '//',          '//')
                Dir_test('#//',         wp,            tmp)
                Dir_test('#//../foo',   tmp_foo,       tmp)
                Dir_test('#//../foo',   tmp_foo,       tmp)
                Dir_test('#//foo/bar',  foo_bar,       foo)
                Dir_test('#//foo/bar',  foo_bar,       foo)
                Dir_test('#//',         wp,            tmp)
        finally:
            os.path = save_os_path
            os.sep = save_os_sep
            SCons.Node.FS.initialize_do_splitdrive()

    def test_target_from_source(self):
        """Test the method for generating target nodes from sources"""
        fs = self.fs

        x = fs.File('x.c')
        t = x.target_from_source('pre-', '-suf')
        assert str(t) == 'pre-x-suf', str(t)
        assert t.__class__ == SCons.Node.FS.Entry

        y = fs.File('dir/y')
        t = y.target_from_source('pre-', '-suf')
        assert str(t) == os.path.join('dir', 'pre-y-suf'), str(t)
        assert t.__class__ == SCons.Node.FS.Entry

        z = fs.File('zz')
        t = z.target_from_source('pre-', '-suf', lambda x: x[:-1])
        assert str(t) == 'pre-z-suf', str(t)
        assert t.__class__ == SCons.Node.FS.Entry

        d = fs.Dir('ddd')
        t = d.target_from_source('pre-', '-suf')
        assert str(t) == 'pre-ddd-suf', str(t)
        assert t.__class__ == SCons.Node.FS.Entry

        e = fs.Entry('eee')
        t = e.target_from_source('pre-', '-suf')
        assert str(t) == 'pre-eee-suf', str(t)
        assert t.__class__ == SCons.Node.FS.Entry

    def test_same_name(self):
        """Test that a local same-named file isn't found for a Dir lookup"""
        test = self.test
        fs = self.fs

        test.subdir('subdir')
        test.write(['subdir', 'build'], "subdir/build\n")

        subdir = fs.Dir('subdir')
        fs.chdir(subdir, change_os_dir=1)
        self.fs._lookup('#build/file', subdir, SCons.Node.FS.File)

    def test_above_root(self):
        """Testing looking up a path above the root directory"""
        test = self.test
        fs = self.fs

        d1 = fs.Dir('d1')
        d2 = d1.Dir('d2')
        dirs = os.path.normpath(d2.get_abspath()).split(os.sep)
        above_path = os.path.join(*['..']*len(dirs) + ['above'])
        above = d2.Dir(above_path)

    def test_lookup_abs(self):
        """Exercise the _lookup_abs function"""
        test = self.test
        fs = self.fs

        root = fs.Dir('/')
        d = root._lookup_abs('/tmp/foo-nonexistent/nonexistent-dir', SCons.Node.FS.Dir)
        assert d.__class__ == SCons.Node.FS.Dir, str(d.__class__)

    def test_lookup_uncpath(self):
        """Testing looking up a UNC path on Windows"""
        if sys.platform not in ('win32',):
            return
        test = self.test
        fs = self.fs
        path='//servername/C$/foo'
        f = self.fs._lookup('//servername/C$/foo', fs.Dir('#'), SCons.Node.FS.File)
        # before the fix in this commit, this returned 'C:\servername\C$\foo'
        # Should be a normalized Windows UNC path as below.
        assert str(f) == r'\\servername\C$\foo', \
        'UNC path %s got looked up as %s'%(path, f)
 
    def test_unc_drive_letter(self):
        """Test drive-letter lookup for windows UNC-style directories"""
        if sys.platform not in ('win32',):
            return
        share = self.fs.Dir(r'\\SERVER\SHARE\Directory')
        assert str(share) == r'\\SERVER\SHARE\Directory', str(share)

    def test_UNC_dirs_2689(self):
        """Test some UNC dirs that printed incorrectly and/or caused
        infinite recursion errors prior to r5180 (SCons 2.1)."""
        fs = self.fs
        if sys.platform not in ('win32',):
            return
        p = fs.Dir(r"\\computername\sharename").get_abspath()
        assert p == r"\\computername\sharename", p
        p = fs.Dir(r"\\\computername\sharename").get_abspath()
        assert p == r"\\computername\sharename", p

    def test_rel_path(self):
        """Test the rel_path() method"""
        test = self.test
        fs = self.fs

        d1 = fs.Dir('d1')
        d1_f = d1.File('f')
        d1_d2 = d1.Dir('d2')
        d1_d2_f = d1_d2.File('f')

        d3 = fs.Dir('d3')
        d3_f = d3.File('f')
        d3_d4 = d3.Dir('d4')
        d3_d4_f = d3_d4.File('f')

        cases = [
                d1,             d1,             '.',
                d1,             d1_f,           'f',
                d1,             d1_d2,          'd2',
                d1,             d1_d2_f,        'd2/f',
                d1,             d3,             '../d3',
                d1,             d3_f,           '../d3/f',
                d1,             d3_d4,          '../d3/d4',
                d1,             d3_d4_f,        '../d3/d4/f',

                d1_f,           d1,             '.',
                d1_f,           d1_f,           'f',
                d1_f,           d1_d2,          'd2',
                d1_f,           d1_d2_f,        'd2/f',
                d1_f,           d3,             '../d3',
                d1_f,           d3_f,           '../d3/f',
                d1_f,           d3_d4,          '../d3/d4',
                d1_f,           d3_d4_f,        '../d3/d4/f',

                d1_d2,          d1,             '..',
                d1_d2,          d1_f,           '../f',
                d1_d2,          d1_d2,          '.',
                d1_d2,          d1_d2_f,        'f',
                d1_d2,          d3,             '../../d3',
                d1_d2,          d3_f,           '../../d3/f',
                d1_d2,          d3_d4,          '../../d3/d4',
                d1_d2,          d3_d4_f,        '../../d3/d4/f',

                d1_d2_f,        d1,             '..',
                d1_d2_f,        d1_f,           '../f',
                d1_d2_f,        d1_d2,          '.',
                d1_d2_f,        d1_d2_f,        'f',
                d1_d2_f,        d3,             '../../d3',
                d1_d2_f,        d3_f,           '../../d3/f',
                d1_d2_f,        d3_d4,          '../../d3/d4',
                d1_d2_f,        d3_d4_f,        '../../d3/d4/f',
        ]

        if sys.platform in ('win32',):
            x_d1        = fs.Dir(r'X:\d1')
            x_d1_d2     = x_d1.Dir('d2')
            y_d1        = fs.Dir(r'Y:\d1')
            y_d1_d2     = y_d1.Dir('d2')
            y_d2        = fs.Dir(r'Y:\d2')

            win32_cases = [
                x_d1,           x_d1,           '.',
                x_d1,           x_d1_d2,        'd2',
                x_d1,           y_d1,           r'Y:\d1',
                x_d1,           y_d1_d2,        r'Y:\d1\d2',
                x_d1,           y_d2,           r'Y:\d2',
            ]

            cases.extend(win32_cases)

        failed = 0
        while cases:
            dir, other, expect = cases[:3]
            expect = os.path.normpath(expect)
            del cases[:3]
            result = dir.rel_path(other)
            if result != expect:
                if failed == 0: print()
                fmt = "    dir_path(%(dir)s, %(other)s) => '%(result)s' did not match '%(expect)s'"
                print(fmt % locals())
                failed = failed + 1
        assert failed == 0, "%d rel_path() cases failed" % failed

    def test_proxy(self):
        """Test a Node.FS object wrapped in a proxy instance"""
        f1 = self.fs.File('fff')
        class MyProxy(SCons.Util.Proxy):
            __str__ = SCons.Util.Delegate('__str__')
        p = MyProxy(f1)
        f2 = self.fs.Entry(p)
        assert f1 is f2, (f1, str(f1), f2, str(f2))



class DirTestCase(_tempdirTestCase):

    def test__morph(self):
        """Test handling of actions when morphing an Entry into a Dir"""
        test = self.test
        e = self.fs.Entry('eee')
        x = e.get_executor()
        x.add_pre_action('pre')
        x.add_post_action('post')
        e.must_be_same(SCons.Node.FS.Dir)
        a = x.get_action_list()
        assert 'pre' in a, a
        assert 'post' in a, a

    def test_subclass(self):
        """Test looking up subclass of Dir nodes"""
        class DirSubclass(SCons.Node.FS.Dir):
            pass
        sd = self.fs._lookup('special_dir', None, DirSubclass, create=1)
        sd.must_be_same(SCons.Node.FS.Dir)

    def test_get_env_scanner(self):
        """Test the Dir.get_env_scanner() method
        """
        import SCons.Defaults
        d = self.fs.Dir('ddd')
        s = d.get_env_scanner(Environment())
        assert s is SCons.Defaults.DirEntryScanner, s

    def test_get_target_scanner(self):
        """Test the Dir.get_target_scanner() method
        """
        import SCons.Defaults
        d = self.fs.Dir('ddd')
        s = d.get_target_scanner()
        assert s is SCons.Defaults.DirEntryScanner, s

    def test_scan(self):
        """Test scanning a directory for in-memory entries
        """
        fs = self.fs

        dir = fs.Dir('ddd')
        fs.File(os.path.join('ddd', 'f1'))
        fs.File(os.path.join('ddd', 'f2'))
        fs.File(os.path.join('ddd', 'f3'))
        fs.Dir(os.path.join('ddd', 'd1'))
        fs.Dir(os.path.join('ddd', 'd1', 'f4'))
        fs.Dir(os.path.join('ddd', 'd1', 'f5'))
        dir.scan()
        kids = sorted([x.get_internal_path() for x in dir.children(None)])
        assert kids == [os.path.join('ddd', 'd1'),
                        os.path.join('ddd', 'f1'),
                        os.path.join('ddd', 'f2'),
                        os.path.join('ddd', 'f3')], kids

    def test_get_contents(self):
        """Test getting the contents for a directory.
        """
        test = self.test

        test.subdir('d')
        test.write(['d', 'g'], "67890\n")
        test.write(['d', 'f'], "12345\n")
        test.subdir(['d','sub'])
        test.write(['d', 'sub','h'], "abcdef\n")
        test.subdir(['d','empty'])

        d = self.fs.Dir('d')
        g = self.fs.File(os.path.join('d', 'g'))
        f = self.fs.File(os.path.join('d', 'f'))
        h = self.fs.File(os.path.join('d', 'sub', 'h'))
        e = self.fs.Dir(os.path.join('d', 'empty'))
        s = self.fs.Dir(os.path.join('d', 'sub'))

        files = d.get_contents().split('\n')

        assert e.get_contents() == '', e.get_contents()
        assert e.get_text_contents() == '', e.get_text_contents()
        assert e.get_csig()+" empty" == files[0], files
        assert f.get_csig()+" f" == files[1], files
        assert g.get_csig()+" g" == files[2], files
        assert s.get_csig()+" sub" == files[3], files

    def test_implicit_re_scans(self):
        """Test that adding entries causes a directory to be re-scanned
        """

        fs = self.fs

        dir = fs.Dir('ddd')

        fs.File(os.path.join('ddd', 'f1'))
        dir.scan()
        kids = sorted([x.get_internal_path() for x in dir.children()])
        assert kids == [os.path.join('ddd', 'f1')], kids

        fs.File(os.path.join('ddd', 'f2'))
        dir.scan()
        kids = sorted([x.get_internal_path() for x in dir.children()])
        assert kids == [os.path.join('ddd', 'f1'),
                        os.path.join('ddd', 'f2')], kids

    def test_entry_exists_on_disk(self):
        """Test the Dir.entry_exists_on_disk() method
        """
        test = self.test

        does_not_exist = self.fs.Dir('does_not_exist')
        assert not does_not_exist.entry_exists_on_disk('foo')

        test.subdir('d')
        test.write(['d', 'exists'], "d/exists\n")
        test.write(['d', 'Case-Insensitive'], "d/Case-Insensitive\n")

        d = self.fs.Dir('d')
        assert d.entry_exists_on_disk('exists')
        assert not d.entry_exists_on_disk('does_not_exist')

        if os.path.normcase("TeSt") != os.path.normpath("TeSt") or sys.platform == "cygwin":
            assert d.entry_exists_on_disk('case-insensitive')

    def test_rentry_exists_on_disk(self):
        """Test the Dir.rentry_exists_on_disk() method
        """
        test = self.test

        does_not_exist = self.fs.Dir('does_not_exist')
        assert not does_not_exist.rentry_exists_on_disk('foo')

        test.subdir('d')
        test.write(['d', 'exists'], "d/exists\n")
        test.write(['d', 'Case-Insensitive'], "d/Case-Insensitive\n")

        test.subdir('r')
        test.write(['r', 'rexists'], "r/rexists\n")

        d = self.fs.Dir('d')
        r = self.fs.Dir('r')
        d.addRepository(r)
        
        assert d.rentry_exists_on_disk('exists')
        assert d.rentry_exists_on_disk('rexists')
        assert not d.rentry_exists_on_disk('does_not_exist')

        if os.path.normcase("TeSt") != os.path.normpath("TeSt") or sys.platform == "cygwin":
            assert d.rentry_exists_on_disk('case-insensitive')

    def test_srcdir_list(self):
        """Test the Dir.srcdir_list() method
        """
        src = self.fs.Dir('src')
        bld = self.fs.Dir('bld')
        sub1 = bld.Dir('sub')
        sub2 = sub1.Dir('sub')
        sub3 = sub2.Dir('sub')
        self.fs.VariantDir(bld, src, duplicate=0)
        self.fs.VariantDir(sub2, src, duplicate=0)

        def check(result, expect):
            result = list(map(str, result))
            expect = list(map(os.path.normpath, expect))
            assert result == expect, result

        s = src.srcdir_list()
        check(s, [])

        s = bld.srcdir_list()
        check(s, ['src'])

        s = sub1.srcdir_list()
        check(s, ['src/sub'])

        s = sub2.srcdir_list()
        check(s, ['src', 'src/sub/sub'])

        s = sub3.srcdir_list()
        check(s, ['src/sub', 'src/sub/sub/sub'])

        self.fs.VariantDir('src/b1/b2', 'src')
        b1 = src.Dir('b1')
        b1_b2 = b1.Dir('b2')
        b1_b2_b1 = b1_b2.Dir('b1')
        b1_b2_b1_b2 = b1_b2_b1.Dir('b2')
        b1_b2_b1_b2_sub = b1_b2_b1_b2.Dir('sub')

        s = b1.srcdir_list()
        check(s, [])

        s = b1_b2.srcdir_list()
        check(s, ['src'])

        s = b1_b2_b1.srcdir_list()
        check(s, ['src/b1'])

        s = b1_b2_b1_b2.srcdir_list()
        check(s, ['src/b1/b2'])

        s = b1_b2_b1_b2_sub.srcdir_list()
        check(s, ['src/b1/b2/sub'])

    def test_srcdir_duplicate(self):
        """Test the Dir.srcdir_duplicate() method
        """
        test = self.test

        test.subdir('src0')
        test.write(['src0', 'exists'], "src0/exists\n")

        bld0 = self.fs.Dir('bld0')
        src0 = self.fs.Dir('src0')
        self.fs.VariantDir(bld0, src0, duplicate=0)

        n = bld0.srcdir_duplicate('does_not_exist')
        assert n is None, n
        assert not os.path.exists(test.workpath('bld0', 'does_not_exist'))

        n = bld0.srcdir_duplicate('exists')
        assert str(n) == os.path.normpath('src0/exists'), str(n)
        assert not os.path.exists(test.workpath('bld0', 'exists'))

        test.subdir('src1')
        test.write(['src1', 'exists'], "src0/exists\n")

        bld1 = self.fs.Dir('bld1')
        src1 = self.fs.Dir('src1')
        self.fs.VariantDir(bld1, src1, duplicate=1)

        n = bld1.srcdir_duplicate('does_not_exist')
        assert n is None, n
        assert not os.path.exists(test.workpath('bld1', 'does_not_exist'))

        n = bld1.srcdir_duplicate('exists')
        assert str(n) == os.path.normpath('bld1/exists'), str(n)
        assert os.path.exists(test.workpath('bld1', 'exists'))

    def test_srcdir_find_file(self):
        """Test the Dir.srcdir_find_file() method
        """
        test = self.test

        def return_true(node):
            return 1

        SCons.Node._is_derived_map[2] = return_true
        SCons.Node._exists_map[5] = return_true
        
        test.subdir('src0')
        test.write(['src0', 'on-disk-f1'], "src0/on-disk-f1\n")
        test.write(['src0', 'on-disk-f2'], "src0/on-disk-f2\n")
        test.write(['src0', 'on-disk-e1'], "src0/on-disk-e1\n")
        test.write(['src0', 'on-disk-e2'], "src0/on-disk-e2\n")

        bld0 = self.fs.Dir('bld0')
        src0 = self.fs.Dir('src0')
        self.fs.VariantDir(bld0, src0, duplicate=0)

        derived_f = src0.File('derived-f')
        derived_f._func_is_derived = 2
        exists_f = src0.File('exists-f')
        exists_f._func_exists = 5

        derived_e = src0.Entry('derived-e')
        derived_e._func_is_derived = 2
        exists_e = src0.Entry('exists-e')
        exists_e._func_exists = 5

        def check(result, expect):
            result = list(map(str, result))
            expect = list(map(os.path.normpath, expect))
            assert result == expect, result

        # First check from the source directory.
        n = src0.srcdir_find_file('does_not_exist')
        assert n == (None, None), n

        n = src0.srcdir_find_file('derived-f')
        check(n, ['src0/derived-f', 'src0'])
        n = src0.srcdir_find_file('exists-f')
        check(n, ['src0/exists-f', 'src0'])
        n = src0.srcdir_find_file('on-disk-f1')
        check(n, ['src0/on-disk-f1', 'src0'])

        n = src0.srcdir_find_file('derived-e')
        check(n, ['src0/derived-e', 'src0'])
        n = src0.srcdir_find_file('exists-e')
        check(n, ['src0/exists-e', 'src0'])
        n = src0.srcdir_find_file('on-disk-e1')
        check(n, ['src0/on-disk-e1', 'src0'])

        # Now check from the variant directory.
        n = bld0.srcdir_find_file('does_not_exist')
        assert n == (None, None), n

        n = bld0.srcdir_find_file('derived-f')
        check(n, ['src0/derived-f', 'bld0'])
        n = bld0.srcdir_find_file('exists-f')
        check(n, ['src0/exists-f', 'bld0'])
        n = bld0.srcdir_find_file('on-disk-f2')
        check(n, ['src0/on-disk-f2', 'bld0'])

        n = bld0.srcdir_find_file('derived-e')
        check(n, ['src0/derived-e', 'bld0'])
        n = bld0.srcdir_find_file('exists-e')
        check(n, ['src0/exists-e', 'bld0'])
        n = bld0.srcdir_find_file('on-disk-e2')
        check(n, ['src0/on-disk-e2', 'bld0'])

        test.subdir('src1')
        test.write(['src1', 'on-disk-f1'], "src1/on-disk-f1\n")
        test.write(['src1', 'on-disk-f2'], "src1/on-disk-f2\n")
        test.write(['src1', 'on-disk-e1'], "src1/on-disk-e1\n")
        test.write(['src1', 'on-disk-e2'], "src1/on-disk-e2\n")

        bld1 = self.fs.Dir('bld1')
        src1 = self.fs.Dir('src1')
        self.fs.VariantDir(bld1, src1, duplicate=1)

        derived_f = src1.File('derived-f')
        derived_f._func_is_derived = 2
        exists_f = src1.File('exists-f')
        exists_f._func_exists = 5

        derived_e = src1.Entry('derived-e')
        derived_e._func_is_derived = 2
        exists_e = src1.Entry('exists-e')
        exists_e._func_exists = 5

        # First check from the source directory.
        n = src1.srcdir_find_file('does_not_exist')
        assert n == (None, None), n

        n = src1.srcdir_find_file('derived-f')
        check(n, ['src1/derived-f', 'src1'])
        n = src1.srcdir_find_file('exists-f')
        check(n, ['src1/exists-f', 'src1'])
        n = src1.srcdir_find_file('on-disk-f1')
        check(n, ['src1/on-disk-f1', 'src1'])

        n = src1.srcdir_find_file('derived-e')
        check(n, ['src1/derived-e', 'src1'])
        n = src1.srcdir_find_file('exists-e')
        check(n, ['src1/exists-e', 'src1'])
        n = src1.srcdir_find_file('on-disk-e1')
        check(n, ['src1/on-disk-e1', 'src1'])

        # Now check from the variant directory.
        n = bld1.srcdir_find_file('does_not_exist')
        assert n == (None, None), n

        n = bld1.srcdir_find_file('derived-f')
        check(n, ['bld1/derived-f', 'src1'])
        n = bld1.srcdir_find_file('exists-f')
        check(n, ['bld1/exists-f', 'src1'])
        n = bld1.srcdir_find_file('on-disk-f2')
        check(n, ['bld1/on-disk-f2', 'bld1'])

        n = bld1.srcdir_find_file('derived-e')
        check(n, ['bld1/derived-e', 'src1'])
        n = bld1.srcdir_find_file('exists-e')
        check(n, ['bld1/exists-e', 'src1'])
        n = bld1.srcdir_find_file('on-disk-e2')
        check(n, ['bld1/on-disk-e2', 'bld1'])

    def test_dir_on_disk(self):
        """Test the Dir.dir_on_disk() method"""
        self.test.subdir('sub', ['sub', 'exists'])
        self.test.write(['sub', 'file'], "self/file\n")
        sub = self.fs.Dir('sub')

        r = sub.dir_on_disk('does_not_exist')
        assert not r, r

        r = sub.dir_on_disk('exists')
        assert r, r

        r = sub.dir_on_disk('file')
        assert not r, r

    def test_file_on_disk(self):
        """Test the Dir.file_on_disk() method"""
        self.test.subdir('sub', ['sub', 'dir'])
        self.test.write(['sub', 'exists'], "self/exists\n")
        sub = self.fs.Dir('sub')

        r = sub.file_on_disk('does_not_exist')
        assert not r, r

        r = sub.file_on_disk('exists')
        assert r, r

        r = sub.file_on_disk('dir')
        assert not r, r

class EntryTestCase(_tempdirTestCase):
    def test_runTest(self):
        """Test methods specific to the Entry sub-class.
        """
        test = TestCmd(workdir='')
        # FS doesn't like the cwd to be something other than its root.
        os.chdir(test.workpath(""))

        fs = SCons.Node.FS.FS()

        e1 = fs.Entry('e1')
        e1.rfile()
        assert e1.__class__ is SCons.Node.FS.File, e1.__class__

        test.subdir('e3d')
        test.write('e3f', "e3f\n")

        e3d = fs.Entry('e3d')
        e3d.get_contents()
        assert e3d.__class__ is SCons.Node.FS.Dir, e3d.__class__

        e3f = fs.Entry('e3f')
        e3f.get_contents()
        assert e3f.__class__ is SCons.Node.FS.File, e3f.__class__

        e3n = fs.Entry('e3n')
        e3n.get_contents()
        assert e3n.__class__ is SCons.Node.FS.Entry, e3n.__class__

        test.subdir('e4d')
        test.write('e4f', "e4f\n")

        e4d = fs.Entry('e4d')
        exists = e4d.exists()
        assert e4d.__class__ is SCons.Node.FS.Dir, e4d.__class__
        assert exists, "e4d does not exist?"

        e4f = fs.Entry('e4f')
        exists = e4f.exists()
        assert e4f.__class__ is SCons.Node.FS.File, e4f.__class__
        assert exists, "e4f does not exist?"

        e4n = fs.Entry('e4n')
        exists = e4n.exists()
        assert e4n.__class__ is SCons.Node.FS.File, e4n.__class__
        assert not exists, "e4n exists?"

        class MyCalc(object):
            def __init__(self, val):
                self.max_drift = 0
                class M(object):
                    def __init__(self, val):
                        self.val = val
                    def collect(self, args):
                        result = 0
                        for a in args:
                            result += a
                        return result
                    def signature(self, executor):
                        return self.val + 222
                self.module = M(val)

        test.subdir('e5d')
        test.write('e5f', "e5f\n")

    def test_Entry_Entry_lookup(self):
        """Test looking up an Entry within another Entry"""
        self.fs.Entry('#topdir')
        self.fs.Entry('#topdir/a/b/c')



class FileTestCase(_tempdirTestCase):

    def test_subclass(self):
        """Test looking up subclass of File nodes"""
        class FileSubclass(SCons.Node.FS.File):
            pass
        sd = self.fs._lookup('special_file', None, FileSubclass, create=1)
        sd.must_be_same(SCons.Node.FS.File)

    def test_Dirs(self):
        """Test the File.Dirs() method"""
        fff = self.fs.File('subdir/fff')
        # This simulates that the SConscript file that defined
        # fff is in subdir/.
        fff.cwd = self.fs.Dir('subdir')
        d1 = self.fs.Dir('subdir/d1')
        d2 = self.fs.Dir('subdir/d2')
        dirs = fff.Dirs(['d1', 'd2'])
        assert dirs == [d1, d2], list(map(str, dirs))

    def test_exists(self):
        """Test the File.exists() method"""
        fs = self.fs
        test = self.test

        src_f1 = fs.File('src/f1')
        assert not src_f1.exists(), "%s apparently exists?" % src_f1

        test.subdir('src')
        test.write(['src', 'f1'], "src/f1\n")

        assert not src_f1.exists(), "%s did not cache previous exists() value" % src_f1
        src_f1.clear()
        assert src_f1.exists(), "%s apparently does not exist?" % src_f1

        test.subdir('build')
        fs.VariantDir('build', 'src')
        build_f1 = fs.File('build/f1')

        assert build_f1.exists(), "%s did not realize that %s exists" % (build_f1, src_f1)
        assert os.path.exists(build_f1.get_abspath()), "%s did not get duplicated on disk" % build_f1.get_abspath()

        test.unlink(['src', 'f1'])
        src_f1.clear()  # so the next exists() call will look on disk again

        assert build_f1.exists(), "%s did not cache previous exists() value" % build_f1
        build_f1.clear()
        build_f1.linked = None
        assert not build_f1.exists(), "%s did not realize that %s disappeared" % (build_f1, src_f1)
        assert not os.path.exists(build_f1.get_abspath()), "%s did not get removed after %s was removed" % (build_f1, src_f1)

    def test_changed(self):
        """ 
        Verify that changes between BuildInfo's list of souces, depends, and implicit 
        dependencies do not corrupt content signiture values written to .SConsign
        when using CacheDir and Timestamp-MD5 decider.
        This is for issue #2980
        """
        # node should have
        # 1 source (for example main.cpp)
        # 0 depends
        # N implicits (for example ['alpha.h', 'beta.h', 'gamma.h', '/usr/bin/g++'])

        class ChangedNode(SCons.Node.FS.File):
            def __init__(self, name, directory=None, fs=None):
                SCons.Node.FS.File.__init__(self, name, directory, fs)
                self.name = name
                self.Tag('found_includes', [])
                self.stored_info = None
                self.build_env = None
                self.changed_since_last_build = 4
                self.timestamp = 1

            def get_stored_info(self):
                return self.stored_info

            def get_build_env(self):
                return self.build_env

            def get_timestamp(self):
                """ Fake timestamp so they always match"""
                return self.timestamp

            def get_contents(self):
                return self.name

            def get_ninfo(self):
                """ mocked to ensure csig will equal the filename"""
                try:
                    return self.ninfo
                except AttributeError:
                    self.ninfo = FakeNodeInfo(self.name, self.timestamp)
                    return self.ninfo

            def get_csig(self):
                ninfo = self.get_ninfo()
                try:
                    return ninfo.csig
                except AttributeError:
                    pass

                return "Should Never Happen"

        class ChangedEnvironment(SCons.Environment.Base):

            def __init__(self):
                SCons.Environment.Base.__init__(self)
                self.decide_source = self._changed_timestamp_then_content

        class FakeNodeInfo(object):
            def __init__(self, csig, timestamp):
                self.csig = csig
                self.timestamp = timestamp


        #Create nodes
        fs = SCons.Node.FS.FS()
        d = self.fs.Dir('.')

        node = ChangedNode('main.o',d,fs)  # main.o
        s1 = ChangedNode('main.cpp',d,fs) # main.cpp
        s1.timestamp = 2 # this changed
        i1 = ChangedNode('alpha.h',d,fs) # alpha.h - The bug is caused because the second build adds this file
        i1.timestamp = 2 # This is the new file.
        i2 = ChangedNode('beta.h',d,fs) # beta.h
        i3 = ChangedNode('gamma.h',d,fs) # gamma.h - In the bug beta.h's csig from binfo overwrites this ones
        i4 = ChangedNode('/usr/bin/g++',d,fs) # /usr/bin/g++



        node.add_source([s1])
        node.add_dependency([])
        node.implicit = [i1, i2, i3, i4]
        node.implicit_set = set()
        # node._add_child(node.implicit, node.implicit_set, [n7, n8, n9])
        # node._add_child(node.implicit, node.implicit_set, [n10, n11, n12])

        # Mock out node's scan method
        # node.scan = lambda *args: None

        # Mock out nodes' children() ?
        # Should return Node's.
        # All those nodes should have changed_since_last_build set to match Timestamp-MD5's
        # decider method...

        # Generate sconsign entry needed
        sconsign_entry = SCons.SConsign.SConsignEntry()
        sconsign_entry.binfo = node.new_binfo()
        sconsign_entry.ninfo = node.new_ninfo()

        # mock out loading info from sconsign
        # This will cause node.get_stored_info() to return our freshly created sconsign_entry
        node.stored_info = sconsign_entry

        # binfo = information from previous build (from sconsign)
        # We'll set the following attributes (which are lists): "bsources", "bsourcesigs",
        # "bdepends","bdependsigs", "bimplicit", "bimplicitsigs"
        bi = sconsign_entry.binfo
        bi.bsources = ['main.cpp']
        bi.bsourcesigs=[FakeNodeInfo('main.cpp',1),]

        bi.bdepends = []
        bi.bdependsigs = []

        bi.bimplicit = ['beta.h','gamma.h']
        bi.bimplicitsigs = [FakeNodeInfo('beta.h',1), FakeNodeInfo('gamma.h',1)]

        ni = sconsign_entry.ninfo
        # We'll set the following attributes (which are lists): sources, depends, implicit lists

        #Set timestamp-md5
        #Call changed
        #Check results
        node.build_env = ChangedEnvironment()

        changed = node.changed()

        # change to true to debug
        if False:
            print("Changed:%s"%changed)
            print("%15s -> csig:%s"%(s1.name, s1.ninfo.csig))
            print("%15s -> csig:%s"%(i1.name, i1.ninfo.csig))
            print("%15s -> csig:%s"%(i2.name, i2.ninfo.csig))
            print("%15s -> csig:%s"%(i3.name, i3.ninfo.csig))
            print("%15s -> csig:%s"%(i4.name, i4.ninfo.csig))

        self.assertEqual(i2.name,i2.ninfo.csig, "gamma.h's fake csig should equal gamma.h but equals:%s"%i2.ninfo.csig)


class GlobTestCase(_tempdirTestCase):
    def setUp(self):
        _tempdirTestCase.setUp(self)

        fs = SCons.Node.FS.FS()
        self.fs = fs

        # Make entries on disk that will not have Nodes, so we can verify
        # the behavior of looking for things on disk.
        self.test.write('disk-bbb', "disk-bbb\n")
        self.test.write('disk-aaa', "disk-aaa\n")
        self.test.write('disk-ccc', "disk-ccc\n")
        self.test.write('#disk-hash', "#disk-hash\n")
        self.test.subdir('disk-sub')
        self.test.write(['disk-sub', 'disk-ddd'], "disk-sub/disk-ddd\n")
        self.test.write(['disk-sub', 'disk-eee'], "disk-sub/disk-eee\n")
        self.test.write(['disk-sub', 'disk-fff'], "disk-sub/disk-fff\n")

        # Make some entries that have both Nodes and on-disk entries,
        # so we can verify what we do with
        self.test.write('both-aaa', "both-aaa\n")
        self.test.write('both-bbb', "both-bbb\n")
        self.test.write('both-ccc', "both-ccc\n")
        self.test.write('#both-hash', "#both-hash\n")
        self.test.subdir('both-sub1')
        self.test.write(['both-sub1', 'both-ddd'], "both-sub1/both-ddd\n")
        self.test.write(['both-sub1', 'both-eee'], "both-sub1/both-eee\n")
        self.test.write(['both-sub1', 'both-fff'], "both-sub1/both-fff\n")
        self.test.subdir('both-sub2')
        self.test.write(['both-sub2', 'both-ddd'], "both-sub2/both-ddd\n")
        self.test.write(['both-sub2', 'both-eee'], "both-sub2/both-eee\n")
        self.test.write(['both-sub2', 'both-fff'], "both-sub2/both-fff\n")

        self.both_aaa = fs.File('both-aaa')
        self.both_bbb = fs.File('both-bbb')
        self.both_ccc = fs.File('both-ccc')
        self._both_hash = fs.File('./#both-hash')
        self.both_sub1 = fs.Dir('both-sub1')
        self.both_sub1_both_ddd = self.both_sub1.File('both-ddd')
        self.both_sub1_both_eee = self.both_sub1.File('both-eee')
        self.both_sub1_both_fff = self.both_sub1.File('both-fff')
        self.both_sub2 = fs.Dir('both-sub2')
        self.both_sub2_both_ddd = self.both_sub2.File('both-ddd')
        self.both_sub2_both_eee = self.both_sub2.File('both-eee')
        self.both_sub2_both_fff = self.both_sub2.File('both-fff')

        # Make various Nodes (that don't have on-disk entries) so we
        # can verify how we match them.
        self.ggg = fs.File('ggg')
        self.hhh = fs.File('hhh')
        self.iii = fs.File('iii')
        self._hash = fs.File('./#hash')
        self.subdir1 = fs.Dir('subdir1')
        self.subdir1_lll = self.subdir1.File('lll')
        self.subdir1_jjj = self.subdir1.File('jjj')
        self.subdir1_kkk = self.subdir1.File('kkk')
        self.subdir2 = fs.Dir('subdir2')
        self.subdir2_lll = self.subdir2.File('lll')
        self.subdir2_kkk = self.subdir2.File('kkk')
        self.subdir2_jjj = self.subdir2.File('jjj')
        self.sub = fs.Dir('sub')
        self.sub_dir3 = self.sub.Dir('dir3')
        self.sub_dir3_kkk = self.sub_dir3.File('kkk')
        self.sub_dir3_jjj = self.sub_dir3.File('jjj')
        self.sub_dir3_lll = self.sub_dir3.File('lll')


    def do_cases(self, cases, **kwargs):

        # First, execute all of the cases with string=True and verify
        # that we get the expected strings returned.  We do this first
        # so the Glob() calls don't add Nodes to the self.fs file system
        # hierarchy.

        import copy
        strings_kwargs = copy.copy(kwargs)
        strings_kwargs['strings'] = True
        for input, string_expect, node_expect in cases:
            r = sorted(self.fs.Glob(input, **strings_kwargs))
            assert r == string_expect, "Glob(%s, strings=True) expected %s, got %s" % (input, string_expect, r)

        # Now execute all of the cases without string=True and look for
        # the expected Nodes to be returned.  If we don't have a list of
        # actual expected Nodes, that means we're expecting a search for
        # on-disk-only files to have returned some newly-created nodes.
        # Verify those by running the list through str() before comparing
        # them with the expected list of strings.
        for input, string_expect, node_expect in cases:
            r = self.fs.Glob(input, **kwargs)
            if node_expect:
                r = sorted(r, key=lambda a: a.get_internal_path())
                result = []
                for n in node_expect:
                    if isinstance(n, str):
                        n = self.fs.Entry(n)
                    result.append(n)
                fmt = lambda n: "%s %s" % (repr(n), repr(str(n)))
            else:
                r = sorted(map(str, r))
                result = string_expect
                fmt = lambda n: n
            if r != result:
                import pprint
                print("Glob(%s) expected:" % repr(input))
                pprint.pprint(list(map(fmt, result)))
                print("Glob(%s) got:" % repr(input))
                pprint.pprint(list(map(fmt, r)))
                self.fail()

    def test_exact_match(self):
        """Test globbing for exact Node matches"""
        join = os.path.join

        cases = (
            ('ggg',         ['ggg'],                    [self.ggg]),

            ('subdir1',     ['subdir1'],                [self.subdir1]),

            ('subdir1/jjj', [join('subdir1', 'jjj')],   [self.subdir1_jjj]),

            ('disk-aaa',    ['disk-aaa'],               None),

            ('disk-sub',    ['disk-sub'],               None),

            ('both-aaa',    ['both-aaa'],               []),
        )

        self.do_cases(cases)

    def test_subdir_matches(self):
        """Test globbing for exact Node matches in subdirectories"""
        join = os.path.join

        cases = (
            ('*/jjj',
             [join('subdir1', 'jjj'), join('subdir2', 'jjj')],
             [self.subdir1_jjj, self.subdir2_jjj]),

            ('*/disk-ddd',
             [join('disk-sub', 'disk-ddd')],
             None),
        )

        self.do_cases(cases)

    def test_asterisk1(self):
        """Test globbing for simple asterisk Node matches (1)"""
        cases = (
            ('h*',
             ['hhh'],
             [self.hhh]),

            ('*',
             ['#both-hash', '#hash',
              'both-aaa', 'both-bbb', 'both-ccc',
              'both-sub1', 'both-sub2',
              'ggg', 'hhh', 'iii',
              'sub', 'subdir1', 'subdir2'],
             [self._both_hash, self._hash,
              self.both_aaa, self.both_bbb, self.both_ccc, 'both-hash',
              self.both_sub1, self.both_sub2,
              self.ggg, 'hash', self.hhh, self.iii,
              self.sub, self.subdir1, self.subdir2]),
        )

        self.do_cases(cases, ondisk=False)

    def test_asterisk2(self):
        """Test globbing for simple asterisk Node matches (2)"""
        cases = (
            ('disk-b*',
             ['disk-bbb'],
             None),

            ('*',
             ['#both-hash', '#disk-hash', '#hash',
              'both-aaa', 'both-bbb', 'both-ccc',
              'both-sub1', 'both-sub2',
              'disk-aaa', 'disk-bbb', 'disk-ccc', 'disk-sub',
              'ggg', 'hhh', 'iii',
              'sub', 'subdir1', 'subdir2'],
             ['./#both-hash', './#disk-hash', './#hash',
              'both-aaa', 'both-bbb', 'both-ccc', 'both-hash',
              'both-sub1', 'both-sub2',
              'disk-aaa', 'disk-bbb', 'disk-ccc', 'disk-sub',
              'ggg', 'hash', 'hhh', 'iii',
              'sub', 'subdir1', 'subdir2']),
        )

        self.do_cases(cases)

    def test_question_mark(self):
        """Test globbing for simple question-mark Node matches"""
        join = os.path.join

        cases = (
            ('ii?',
             ['iii'],
             [self.iii]),

            ('both-sub?/both-eee',
             [join('both-sub1', 'both-eee'), join('both-sub2', 'both-eee')],
             [self.both_sub1_both_eee, self.both_sub2_both_eee]),

            ('subdir?/jjj',
             [join('subdir1', 'jjj'), join('subdir2', 'jjj')],
             [self.subdir1_jjj, self.subdir2_jjj]),

            ('disk-cc?',
             ['disk-ccc'],
             None),
        )

        self.do_cases(cases)

    def test_does_not_exist(self):
        """Test globbing for things that don't exist"""

        cases = (
            ('does_not_exist',  [], []),
            ('no_subdir/*',     [], []),
            ('subdir?/no_file', [], []),
        )

        self.do_cases(cases)

    def test_subdir_asterisk(self):
        """Test globbing for asterisk Node matches in subdirectories"""
        join = os.path.join

        cases = (
            ('*/k*',
             [join('subdir1', 'kkk'), join('subdir2', 'kkk')],
             [self.subdir1_kkk, self.subdir2_kkk]),

            ('both-sub?/*',
             [join('both-sub1', 'both-ddd'),
              join('both-sub1', 'both-eee'),
              join('both-sub1', 'both-fff'),
              join('both-sub2', 'both-ddd'),
              join('both-sub2', 'both-eee'),
              join('both-sub2', 'both-fff')],
             [self.both_sub1_both_ddd,
              self.both_sub1_both_eee,
              self.both_sub1_both_fff,
              self.both_sub2_both_ddd,
              self.both_sub2_both_eee,
              self.both_sub2_both_fff],
             ),

            ('subdir?/*',
             [join('subdir1', 'jjj'),
              join('subdir1', 'kkk'),
              join('subdir1', 'lll'),
              join('subdir2', 'jjj'),
              join('subdir2', 'kkk'),
              join('subdir2', 'lll')],
             [self.subdir1_jjj, self.subdir1_kkk, self.subdir1_lll,
              self.subdir2_jjj, self.subdir2_kkk, self.subdir2_lll]),

            ('sub/*/*',
             [join('sub', 'dir3', 'jjj'),
              join('sub', 'dir3', 'kkk'),
              join('sub', 'dir3', 'lll')],
             [self.sub_dir3_jjj, self.sub_dir3_kkk, self.sub_dir3_lll]),

            ('*/k*',
             [join('subdir1', 'kkk'), join('subdir2', 'kkk')],
             None),

            ('subdir?/*',
             [join('subdir1', 'jjj'),
              join('subdir1', 'kkk'),
              join('subdir1', 'lll'),
              join('subdir2', 'jjj'),
              join('subdir2', 'kkk'),
              join('subdir2', 'lll')],
             None),

            ('sub/*/*',
             [join('sub', 'dir3', 'jjj'),
              join('sub', 'dir3', 'kkk'),
              join('sub', 'dir3', 'lll')],
             None),
        )

        self.do_cases(cases)

    def test_subdir_question(self):
        """Test globbing for question-mark Node matches in subdirectories"""
        join = os.path.join

        cases = (
            ('*/?kk',
             [join('subdir1', 'kkk'), join('subdir2', 'kkk')],
             [self.subdir1_kkk, self.subdir2_kkk]),

            ('subdir?/l?l',
             [join('subdir1', 'lll'), join('subdir2', 'lll')],
             [self.subdir1_lll, self.subdir2_lll]),

            ('*/disk-?ff',
             [join('disk-sub', 'disk-fff')],
             None),

            ('subdir?/l?l',
             [join('subdir1', 'lll'), join('subdir2', 'lll')],
             None),
        )

        self.do_cases(cases)

    def test_sort(self):
        """Test whether globbing sorts"""
        join = os.path.join
        # At least sometimes this should return out-of-order items
        # if Glob doesn't sort.
        # It's not a very good test though since it depends on the
        # order returned by glob, which might already be sorted.
        g = self.fs.Glob('disk-sub/*', strings=True)
        expect = [
            os.path.join('disk-sub', 'disk-ddd'),
            os.path.join('disk-sub', 'disk-eee'),
            os.path.join('disk-sub', 'disk-fff'),
        ]
        assert g == expect, str(g) + " is not sorted, but should be!"

        g = self.fs.Glob('disk-*', strings=True)
        expect = [ 'disk-aaa', 'disk-bbb', 'disk-ccc', 'disk-sub' ]
        assert g == expect, str(g) + " is not sorted, but should be!"


class RepositoryTestCase(_tempdirTestCase):

    def setUp(self):
        _tempdirTestCase.setUp(self)

        self.test.subdir('rep1', 'rep2', 'rep3', 'work')

        self.rep1 = self.test.workpath('rep1')
        self.rep2 = self.test.workpath('rep2')
        self.rep3 = self.test.workpath('rep3')

        os.chdir(self.test.workpath('work'))

        self.fs = SCons.Node.FS.FS()
        self.fs.Repository(self.rep1, self.rep2, self.rep3)

    def test_getRepositories(self):
        """Test the Dir.getRepositories() method"""
        self.fs.Repository('foo')
        self.fs.Repository(os.path.join('foo', 'bar'))
        self.fs.Repository('bar/foo')
        self.fs.Repository('bar')

        expect = [
            self.rep1,
            self.rep2,
            self.rep3,
            'foo',
            os.path.join('foo', 'bar'),
            os.path.join('bar', 'foo'),
            'bar'
        ]

        rep = self.fs.Dir('#').getRepositories()
        r = [os.path.normpath(str(x)) for x in rep]
        assert r == expect, r

    def test_get_all_rdirs(self):
        """Test the Dir.get_all_rdirs() method"""
        self.fs.Repository('foo')
        self.fs.Repository(os.path.join('foo', 'bar'))
        self.fs.Repository('bar/foo')
        self.fs.Repository('bar')

        expect = [
            '.',
            self.rep1,
            self.rep2,
            self.rep3,
            'foo',
            os.path.join('foo', 'bar'),
            os.path.join('bar', 'foo'),
            'bar'
        ]

        rep = self.fs.Dir('#').get_all_rdirs()
        r = [os.path.normpath(str(x)) for x in rep]
        assert r == expect, r

    def test_rentry(self):
        """Test the Base.entry() method"""
        return_true = lambda: 1
        return_false = lambda: 0

        d1 = self.fs.Dir('d1')
        d2 = self.fs.Dir('d2')
        d3 = self.fs.Dir('d3')

        e1 = self.fs.Entry('e1')
        e2 = self.fs.Entry('e2')
        e3 = self.fs.Entry('e3')

        f1 = self.fs.File('f1')
        f2 = self.fs.File('f2')
        f3 = self.fs.File('f3')

        self.test.write([self.rep1, 'd2'], "")
        self.test.subdir([self.rep2, 'd3'])
        self.test.write([self.rep3, 'd3'], "")

        self.test.write([self.rep1, 'e2'], "")
        self.test.subdir([self.rep2, 'e3'])
        self.test.write([self.rep3, 'e3'], "")

        self.test.write([self.rep1, 'f2'], "")
        self.test.subdir([self.rep2, 'f3'])
        self.test.write([self.rep3, 'f3'], "")

        r = d1.rentry()
        assert r is d1, r

        r = d2.rentry()
        assert not r is d2, r
        r = str(r)
        assert r == os.path.join(self.rep1, 'd2'), r

        r = d3.rentry()
        assert not r is d3, r
        r = str(r)
        assert r == os.path.join(self.rep2, 'd3'), r

        r = e1.rentry()
        assert r is e1, r

        r = e2.rentry()
        assert not r is e2, r
        r = str(r)
        assert r == os.path.join(self.rep1, 'e2'), r

        r = e3.rentry()
        assert not r is e3, r
        r = str(r)
        assert r == os.path.join(self.rep2, 'e3'), r

        r = f1.rentry()
        assert r is f1, r

        r = f2.rentry()
        assert not r is f2, r
        r = str(r)
        assert r == os.path.join(self.rep1, 'f2'), r

        r = f3.rentry()
        assert not r is f3, r
        r = str(r)
        assert r == os.path.join(self.rep2, 'f3'), r

    def test_rdir(self):
        """Test the Dir.rdir() method"""
        def return_true(obj):
            return 1
        def return_false(obj):
            return 0
        SCons.Node._exists_map[5] = return_true
        SCons.Node._exists_map[6] = return_false
        SCons.Node._is_derived_map[2] = return_true
        SCons.Node._is_derived_map[3] = return_false

        d1 = self.fs.Dir('d1')
        d2 = self.fs.Dir('d2')
        d3 = self.fs.Dir('d3')

        self.test.subdir([self.rep1, 'd2'])
        self.test.write([self.rep2, 'd3'], "")
        self.test.subdir([self.rep3, 'd3'])

        r = d1.rdir()
        assert r is d1, r

        r = d2.rdir()
        assert not r is d2, r
        r = str(r)
        assert r == os.path.join(self.rep1, 'd2'), r

        r = d3.rdir()
        assert not r is d3, r
        r = str(r)
        assert r == os.path.join(self.rep3, 'd3'), r

        e1 = self.fs.Dir('e1')
        e1._func_exists = 6
        e2 = self.fs.Dir('e2')
        e2._func_exists = 6

        # Make sure we match entries in repositories,
        # regardless of whether they're derived or not.

        re1 = self.fs.Entry(os.path.join(self.rep1, 'e1'))
        re1._func_exists = 5
        re1._func_is_derived = 2
        re2 = self.fs.Entry(os.path.join(self.rep2, 'e2'))
        re2._func_exists = 5
        re2._func_is_derived = 3

        r = e1.rdir()
        assert r is re1, r

        r = e2.rdir()
        assert r is re2, r

    def test_rfile(self):
        """Test the File.rfile() method"""
        def return_true(obj):
            return 1
        def return_false(obj):
            return 0
        SCons.Node._exists_map[5] = return_true
        SCons.Node._exists_map[6] = return_false
        SCons.Node._is_derived_map[2] = return_true
        SCons.Node._is_derived_map[3] = return_false

        f1 = self.fs.File('f1')
        f2 = self.fs.File('f2')
        f3 = self.fs.File('f3')

        self.test.write([self.rep1, 'f2'], "")
        self.test.subdir([self.rep2, 'f3'])
        self.test.write([self.rep3, 'f3'], "")

        r = f1.rfile()
        assert r is f1, r

        r = f2.rfile()
        assert not r is f2, r
        r = str(r)
        assert r == os.path.join(self.rep1, 'f2'), r

        r = f3.rfile()
        assert not r is f3, r
        r = f3.rstr()
        assert r == os.path.join(self.rep3, 'f3'), r

        e1 = self.fs.File('e1')
        e1._func_exists = 6
        e2 = self.fs.File('e2')
        e2._func_exists = 6

        # Make sure we match entries in repositories,
        # regardless of whether they're derived or not.

        re1 = self.fs.Entry(os.path.join(self.rep1, 'e1'))
        re1._func_exists = 5
        re1._func_is_derived = 2
        re2 = self.fs.Entry(os.path.join(self.rep2, 'e2'))
        re2._func_exists = 5
        re2._func_is_derived = 3

        r = e1.rfile()
        assert r is re1, r

        r = e2.rfile()
        assert r is re2, r

    def test_Rfindalldirs(self):
        """Test the Rfindalldirs() methods"""
        fs = self.fs
        test = self.test

        d1 = fs.Dir('d1')
        d2 = fs.Dir('d2')
        rep1_d1 = fs.Dir(test.workpath('rep1', 'd1'))
        rep2_d1 = fs.Dir(test.workpath('rep2', 'd1'))
        rep3_d1 = fs.Dir(test.workpath('rep3', 'd1'))
        sub = fs.Dir('sub')
        sub_d1 = sub.Dir('d1')
        rep1_sub_d1 = fs.Dir(test.workpath('rep1', 'sub', 'd1'))
        rep2_sub_d1 = fs.Dir(test.workpath('rep2', 'sub', 'd1'))
        rep3_sub_d1 = fs.Dir(test.workpath('rep3', 'sub', 'd1'))

        r = fs.Top.Rfindalldirs((d1,))
        assert r == [d1], list(map(str, r))

        r = fs.Top.Rfindalldirs((d1, d2))
        assert r == [d1, d2], list(map(str, r))

        r = fs.Top.Rfindalldirs(('d1',))
        assert r == [d1, rep1_d1, rep2_d1, rep3_d1], list(map(str, r))

        r = fs.Top.Rfindalldirs(('#d1',))
        assert r == [d1, rep1_d1, rep2_d1, rep3_d1], list(map(str, r))

        r = sub.Rfindalldirs(('d1',))
        assert r == [sub_d1, rep1_sub_d1, rep2_sub_d1, rep3_sub_d1], list(map(str, r))

        r = sub.Rfindalldirs(('#d1',))
        assert r == [d1, rep1_d1, rep2_d1, rep3_d1], list(map(str, r))

        r = fs.Top.Rfindalldirs(('d1', d2))
        assert r == [d1, rep1_d1, rep2_d1, rep3_d1, d2], list(map(str, r))

    def test_rexists(self):
        """Test the Entry.rexists() method"""
        fs = self.fs
        test = self.test

        test.write([self.rep1, 'f2'], "")
        test.write([self.rep2, "i_exist"], "\n")
        test.write(["work", "i_exist_too"], "\n")

        fs.VariantDir('build', '.')

        f = fs.File(test.workpath("work", "i_do_not_exist"))
        assert not f.rexists()

        f = fs.File(test.workpath("work", "i_exist"))
        assert f.rexists()

        f = fs.File(test.workpath("work", "i_exist_too"))
        assert f.rexists()

        f1 = fs.File(os.path.join('build', 'f1'))
        assert not f1.rexists()

        f2 = fs.File(os.path.join('build', 'f2'))
        assert f2.rexists()

    def test_FAT_timestamps(self):
        """Test repository timestamps on FAT file systems"""
        fs = self.fs
        test = self.test

        test.write(["rep2", "tstamp"], "tstamp\n")
        try:
            # Okay, *this* manipulation accomodates Windows FAT file systems
            # that only have two-second granularity on their timestamps.
            # We round down the current time to the nearest even integer
            # value, subtract two to make sure the timestamp is not "now,"
            # and then convert it back to a float.
            tstamp = float(int(time.time() // 2) * 2) - 2.0
            os.utime(test.workpath("rep2", "tstamp"), (tstamp - 2.0, tstamp))
            f = fs.File("tstamp")
            t = f.get_timestamp()
            assert t == tstamp, "expected %f, got %f" % (tstamp, t)
        finally:
            test.unlink(["rep2", "tstamp"])

    def test_get_contents(self):
        """Ensure get_contents() returns binary contents from Repositories"""
        fs = self.fs
        test = self.test

        test.write(["rep3", "contents"], "Con\x1aTents\n")
        try:
            c = fs.File("contents").get_contents()
            assert c == bytearray("Con\x1aTents\n",'utf-8'), "got '%s'" % c
        finally:
            test.unlink(["rep3", "contents"])

    def test_get_text_contents(self):
        """Ensure get_text_contents() returns text contents from
        Repositories"""
        fs = self.fs
        test = self.test

        # Use a test string that has a file terminator in it to make
        # sure we read the entire file, regardless of its contents.
        try:
            eval('test_string = u"Con\x1aTents\n"')
        except SyntaxError:
            import collections
            class FakeUnicodeString(collections.UserString):
                def encode(self, encoding):
                    return str(self)
            test_string = FakeUnicodeString("Con\x1aTents\n")


        # Test with ASCII.
        test.write(["rep3", "contents"], test_string.encode('ascii'))
        try:
            c = fs.File("contents").get_text_contents()
            assert test_string == c, "got %s" % repr(c)
        finally:
            test.unlink(["rep3", "contents"])

        # Test with utf-8
        test.write(["rep3", "contents"], test_string.encode('utf-8'))
        try:
            c = fs.File("contents").get_text_contents()
            assert test_string == c, "got %s" % repr(c)
        finally:
            test.unlink(["rep3", "contents"])

        # Test with utf-16
        test.write(["rep3", "contents"], test_string.encode('utf-16'))
        try:
            c = fs.File("contents").get_text_contents()
            assert test_string == c, "got %s" % repr(c)
        finally:
            test.unlink(["rep3", "contents"])

    #def test_is_up_to_date(self):



class find_fileTestCase(unittest.TestCase):
    def runTest(self):
        """Testing find_file function"""
        test = TestCmd(workdir = '')
        test.write('./foo', 'Some file\n')
        test.write('./foo2', 'Another file\n')
        test.subdir('same')
        test.subdir('bar')
        test.write(['bar', 'on_disk'], 'Another file\n')
        test.write(['bar', 'same'], 'bar/same\n')

        fs = SCons.Node.FS.FS(test.workpath(""))
        # FS doesn't like the cwd to be something other than its root.
        os.chdir(test.workpath(""))

        node_derived = fs.File(test.workpath('bar/baz'))
        node_derived.builder_set(1) # Any non-zero value.
        node_pseudo = fs.File(test.workpath('pseudo'))
        node_pseudo.set_src_builder(1) # Any non-zero value.

        paths = tuple(map(fs.Dir, ['.', 'same', './bar']))
        nodes = [SCons.Node.FS.find_file('foo', paths)]
        nodes.append(SCons.Node.FS.find_file('baz', paths))
        nodes.append(SCons.Node.FS.find_file('pseudo', paths))
        nodes.append(SCons.Node.FS.find_file('same', paths))

        file_names = list(map(str, nodes))
        file_names = list(map(os.path.normpath, file_names))
        expect = ['./foo', './bar/baz', './pseudo', './bar/same']
        expect = list(map(os.path.normpath, expect))
        assert file_names == expect, file_names

        # Make sure we don't blow up if there's already a File in place
        # of a directory that we'd otherwise try to search.  If this
        # is broken, we'll see an exception like "Tried to lookup File
        # 'bar/baz' as a Dir.
        SCons.Node.FS.find_file('baz/no_file_here', paths)

        import io
        save_sys_stdout = sys.stdout

        try:
            sio = io.StringIO()
            sys.stdout = sio
            SCons.Node.FS.find_file('foo2', paths, verbose="xyz")
            expect = "  xyz: looking for 'foo2' in '.' ...\n" + \
                     "  xyz: ... FOUND 'foo2' in '.'\n"
            c = sio.getvalue()
            assert c == expect, c

            sio = io.StringIO()
            sys.stdout = sio
            SCons.Node.FS.find_file('baz2', paths, verbose=1)
            expect = "  find_file: looking for 'baz2' in '.' ...\n" + \
                     "  find_file: looking for 'baz2' in 'same' ...\n" + \
                     "  find_file: looking for 'baz2' in 'bar' ...\n"
            c = sio.getvalue()
            assert c == expect, c

            sio = io.StringIO()
            sys.stdout = sio
            SCons.Node.FS.find_file('on_disk', paths, verbose=1)
            expect = "  find_file: looking for 'on_disk' in '.' ...\n" + \
                     "  find_file: looking for 'on_disk' in 'same' ...\n" + \
                     "  find_file: looking for 'on_disk' in 'bar' ...\n" + \
                     "  find_file: ... FOUND 'on_disk' in 'bar'\n"
            c = sio.getvalue()
            assert c == expect, c
        finally:
            sys.stdout = save_sys_stdout

class StringDirTestCase(unittest.TestCase):
    def runTest(self):
        """Test using a string as the second argument of
        File() and Dir()"""

        test = TestCmd(workdir = '')
        test.subdir('sub')
        fs = SCons.Node.FS.FS(test.workpath(''))

        d = fs.Dir('sub', '.')
        assert str(d) == 'sub', str(d)
        assert d.exists()
        f = fs.File('file', 'sub')
        assert str(f) == os.path.join('sub', 'file')
        assert not f.exists()

class stored_infoTestCase(unittest.TestCase):
    def runTest(self):
        """Test how we store build information"""
        test = TestCmd(workdir = '')
        test.subdir('sub')
        fs = SCons.Node.FS.FS(test.workpath(''))

        d = fs.Dir('sub')
        f = fs.File('file1', d)
        bi = f.get_stored_info()
        assert hasattr(bi, 'ninfo')

        class MySConsign(object):
            class Null(object):
                def __init__(self):
                    self.xyzzy = 7
            def get_entry(self, name):
                return self.Null()
            
        def test_sconsign(node):
            return MySConsign()

        f = fs.File('file2', d)
        SCons.Node.FS._sconsign_map[2] = test_sconsign
        f.dir._func_sconsign = 2
        bi = f.get_stored_info()
        assert bi.xyzzy == 7, bi

class has_src_builderTestCase(unittest.TestCase):
    def runTest(self):
        """Test the has_src_builder() method"""
        test = TestCmd(workdir = '')
        fs = SCons.Node.FS.FS(test.workpath(''))
        os.chdir(test.workpath(''))
        test.subdir('sub1')

        sub1 = fs.Dir('sub1', '.')
        f1 = fs.File('f1', sub1)
        f2 = fs.File('f2', sub1)
        f3 = fs.File('f3', sub1)

        h = f1.has_src_builder()
        assert not h, h
        h = f1.has_builder()
        assert not h, h

        b1 = Builder(fs.File)
        sub1.set_src_builder(b1)

        test.write(['sub1', 'f2'], "sub1/f2\n")
        h = f1.has_src_builder()        # cached from previous call
        assert not h, h
        h = f1.has_builder()            # cached from previous call
        assert not h, h
        h = f2.has_src_builder()
        assert not h, h
        h = f2.has_builder()
        assert not h, h
        h = f3.has_src_builder()
        assert h, h
        h = f3.has_builder()
        assert h, h
        assert f3.builder is b1, f3.builder

class prepareTestCase(unittest.TestCase):
    def runTest(self):
        """Test the prepare() method"""

        class MyFile(SCons.Node.FS.File):
            def _createDir(self, update=None):
                raise SCons.Errors.StopError
            def exists(self):
                return None

        fs = SCons.Node.FS.FS()
        file = MyFile('foo', fs.Dir('.'), fs)

        exc_caught = 0
        try:
            file.prepare()
        except SCons.Errors.StopError:
            exc_caught = 1
        assert exc_caught, "Should have caught a StopError."

        class MkdirAction(Action):
            def __init__(self, dir_made):
                self.dir_made = dir_made
            def __call__(self, target, source, env, executor=None):
                if executor:
                    target = executor.get_all_targets()
                    source = executor.get_all_sources()
                self.dir_made.extend(target)

        dir_made = []
        new_dir = fs.Dir("new_dir")
        new_dir.builder = Builder(fs.Dir, action=MkdirAction(dir_made))
        new_dir.reset_executor()
        xyz = fs.File(os.path.join("new_dir", "xyz"))

        xyz.set_state(SCons.Node.up_to_date)
        xyz.prepare()
        assert dir_made == [], dir_made

        xyz.set_state(0)
        xyz.prepare()
        assert dir_made[0].get_internal_path() == "new_dir", dir_made[0]

        dir = fs.Dir("dir")
        dir.prepare()



class SConstruct_dirTestCase(unittest.TestCase):
    def runTest(self):
        """Test setting the SConstruct directory"""

        fs = SCons.Node.FS.FS()
        fs.set_SConstruct_dir(fs.Dir('xxx'))
        assert fs.SConstruct_dir.get_internal_path() == 'xxx'



class CacheDirTestCase(unittest.TestCase):

    def test_get_cachedir_csig(self):
        fs = SCons.Node.FS.FS()

        f9 = fs.File('f9')
        r = f9.get_cachedir_csig()
        assert r == 'd41d8cd98f00b204e9800998ecf8427e', r



class clearTestCase(unittest.TestCase):
    def runTest(self):
        """Test clearing FS nodes of cached data."""
        fs = SCons.Node.FS.FS()
        test = TestCmd(workdir='')

        e = fs.Entry('e')
        assert not e.exists()
        assert not e.rexists()
        assert str(e) == 'e', str(d)
        e.clear()
        assert not e.exists()
        assert not e.rexists()
        assert str(e) == 'e', str(d)

        d = fs.Dir(test.workpath('d'))
        test.subdir('d')
        assert d.exists()
        assert d.rexists()
        assert str(d) == test.workpath('d'), str(d)
        fs.rename(test.workpath('d'), test.workpath('gone'))
        # Verify caching is active
        assert d.exists(), 'caching not active'
        assert d.rexists()
        assert str(d) == test.workpath('d'), str(d)
        # Now verify clear() resets the cache
        d.clear()
        assert not d.exists()      
        assert not d.rexists()
        assert str(d) == test.workpath('d'), str(d)
        
        f = fs.File(test.workpath('f'))
        test.write(test.workpath('f'), 'file f')
        assert f.exists()
        assert f.rexists()
        assert str(f) == test.workpath('f'), str(f)
        # Verify caching is active
        test.unlink(test.workpath('f'))
        assert f.exists()
        assert f.rexists()
        assert str(f) == test.workpath('f'), str(f)
        # Now verify clear() resets the cache
        f.clear()
        assert not f.exists()
        assert not f.rexists()
        assert str(f) == test.workpath('f'), str(f)



class disambiguateTestCase(unittest.TestCase):
    def runTest(self):
        """Test calling the disambiguate() method."""
        test = TestCmd(workdir='')

        fs = SCons.Node.FS.FS()

        ddd = fs.Dir('ddd')
        d = ddd.disambiguate()
        assert d is ddd, d

        fff = fs.File('fff')
        f = fff.disambiguate()
        assert f is fff, f

        test.subdir('edir')
        test.write('efile', "efile\n")

        edir = fs.Entry(test.workpath('edir'))
        d = edir.disambiguate()
        assert d.__class__ is ddd.__class__, d.__class__

        efile = fs.Entry(test.workpath('efile'))
        f = efile.disambiguate()
        assert f.__class__ is fff.__class__, f.__class__

        test.subdir('build')
        test.subdir(['build', 'bdir'])
        test.write(['build', 'bfile'], "build/bfile\n")

        test.subdir('src')
        test.write(['src', 'bdir'], "src/bdir\n")
        test.subdir(['src', 'bfile'])

        test.subdir(['src', 'edir'])
        test.write(['src', 'efile'], "src/efile\n")

        fs.VariantDir(test.workpath('build'), test.workpath('src'))

        build_bdir = fs.Entry(test.workpath('build/bdir'))
        d = build_bdir.disambiguate()
        assert d is build_bdir, d
        assert d.__class__ is ddd.__class__, d.__class__

        build_bfile = fs.Entry(test.workpath('build/bfile'))
        f = build_bfile.disambiguate()
        assert f is build_bfile, f
        assert f.__class__ is fff.__class__, f.__class__

        build_edir = fs.Entry(test.workpath('build/edir'))
        d = build_edir.disambiguate()
        assert d.__class__ is ddd.__class__, d.__class__

        build_efile = fs.Entry(test.workpath('build/efile'))
        f = build_efile.disambiguate()
        assert f.__class__ is fff.__class__, f.__class__

        build_nonexistant = fs.Entry(test.workpath('build/nonexistant'))
        f = build_nonexistant.disambiguate()
        assert f.__class__ is fff.__class__, f.__class__

class postprocessTestCase(unittest.TestCase):
    def runTest(self):
        """Test calling the postprocess() method."""
        fs = SCons.Node.FS.FS()

        e = fs.Entry('e')
        e.postprocess()

        d = fs.Dir('d')
        d.postprocess()

        f = fs.File('f')
        f.postprocess()



class SpecialAttrTestCase(unittest.TestCase):
    def runTest(self):
        """Test special attributes of file nodes."""
        test=TestCmd(workdir='')
        fs = SCons.Node.FS.FS(test.workpath('work'))

        f = fs.Entry('foo/bar/baz.blat').get_subst_proxy()

        s = str(f.dir)
        assert s == os.path.normpath('foo/bar'), s
        assert f.dir.is_literal(), f.dir
        for_sig = f.dir.for_signature()
        assert for_sig == 'bar', for_sig

        s = str(f.file)
        assert s == 'baz.blat', s
        assert f.file.is_literal(), f.file
        for_sig = f.file.for_signature()
        assert for_sig == 'baz.blat_file', for_sig

        s = str(f.base)
        assert s == os.path.normpath('foo/bar/baz'), s
        assert f.base.is_literal(), f.base
        for_sig = f.base.for_signature()
        assert for_sig == 'baz.blat_base', for_sig

        s = str(f.filebase)
        assert s == 'baz', s
        assert f.filebase.is_literal(), f.filebase
        for_sig = f.filebase.for_signature()
        assert for_sig == 'baz.blat_filebase', for_sig

        s = str(f.suffix)
        assert s == '.blat', s
        assert f.suffix.is_literal(), f.suffix
        for_sig = f.suffix.for_signature()
        assert for_sig == 'baz.blat_suffix', for_sig

        s = str(f.get_abspath())
        assert s == test.workpath('work', 'foo', 'bar', 'baz.blat'), s
        assert f.abspath.is_literal(), f.abspath
        for_sig = f.abspath.for_signature()
        assert for_sig == 'baz.blat_abspath', for_sig

        s = str(f.posix)
        assert s == 'foo/bar/baz.blat', s
        assert f.posix.is_literal(), f.posix
        if f.posix != f:
            for_sig = f.posix.for_signature()
            assert for_sig == 'baz.blat_posix', for_sig

        s = str(f.windows)
        assert s == 'foo\\bar\\baz.blat', repr(s)
        assert f.windows.is_literal(), f.windows
        if f.windows != f:
            for_sig = f.windows.for_signature()
            assert for_sig == 'baz.blat_windows', for_sig

        # Deprecated synonym for the .windows suffix.
        s = str(f.win32)
        assert s == 'foo\\bar\\baz.blat', repr(s)
        assert f.win32.is_literal(), f.win32
        if f.win32 != f:
            for_sig = f.win32.for_signature()
            assert for_sig == 'baz.blat_windows', for_sig

        # And now, combinations!!!
        s = str(f.srcpath.base)
        assert s == os.path.normpath('foo/bar/baz'), s
        s = str(f.srcpath.dir)
        assert s == str(f.srcdir), s
        s = str(f.srcpath.posix)
        assert s == 'foo/bar/baz.blat', s
        s = str(f.srcpath.windows)
        assert s == 'foo\\bar\\baz.blat', s
        s = str(f.srcpath.win32)
        assert s == 'foo\\bar\\baz.blat', s

        # Test what happens with VariantDir()
        fs.VariantDir('foo', 'baz')

        s = str(f.srcpath)
        assert s == os.path.normpath('baz/bar/baz.blat'), s
        assert f.srcpath.is_literal(), f.srcpath
        g = f.srcpath.get()
        assert isinstance(g, SCons.Node.FS.File), g.__class__

        s = str(f.srcdir)
        assert s == os.path.normpath('baz/bar'), s
        assert f.srcdir.is_literal(), f.srcdir
        g = f.srcdir.get()
        assert isinstance(g, SCons.Node.FS.Dir), g.__class__

        # And now what happens with VariantDir() + Repository()
        fs.Repository(test.workpath('repository'))

        f = fs.Entry('foo/sub/file.suffix').get_subst_proxy()
        test.subdir('repository',
                    ['repository', 'baz'],
                    ['repository', 'baz', 'sub'])

        rd = test.workpath('repository', 'baz', 'sub')
        rf = test.workpath('repository', 'baz', 'sub', 'file.suffix')
        test.write(rf, "\n")

        s = str(f.srcpath)
        assert s == os.path.normpath('baz/sub/file.suffix'), s
        assert f.srcpath.is_literal(), f.srcpath
        g = f.srcpath.get()
        # Gets disambiguated to SCons.Node.FS.File by get_subst_proxy().
        assert isinstance(g, SCons.Node.FS.File), g.__class__

        s = str(f.srcdir)
        assert s == os.path.normpath('baz/sub'), s
        assert f.srcdir.is_literal(), f.srcdir
        g = f.srcdir.get()
        assert isinstance(g, SCons.Node.FS.Dir), g.__class__

        s = str(f.rsrcpath)
        assert s == rf, s
        assert f.rsrcpath.is_literal(), f.rsrcpath
        g = f.rsrcpath.get()
        assert isinstance(g, SCons.Node.FS.File), g.__class__

        s = str(f.rsrcdir)
        assert s == rd, s
        assert f.rsrcdir.is_literal(), f.rsrcdir
        g = f.rsrcdir.get()
        assert isinstance(g, SCons.Node.FS.Dir), g.__class__

        # Check that attempts to access non-existent attributes of the
        # subst proxy generate the right exceptions and messages.
        caught = None
        try:
            fs.Dir('ddd').get_subst_proxy().no_such_attr
        except AttributeError as e:
            assert str(e) == "Dir instance 'ddd' has no attribute 'no_such_attr'", e
            caught = 1
        assert caught, "did not catch expected AttributeError"

        caught = None
        try:
            fs.Entry('eee').get_subst_proxy().no_such_attr
        except AttributeError as e:
            # Gets disambiguated to File instance by get_subst_proxy().
            assert str(e) == "File instance 'eee' has no attribute 'no_such_attr'", e
            caught = 1
        assert caught, "did not catch expected AttributeError"

        caught = None
        try:
            fs.File('fff').get_subst_proxy().no_such_attr
        except AttributeError as e:
            assert str(e) == "File instance 'fff' has no attribute 'no_such_attr'", e
            caught = 1
        assert caught, "did not catch expected AttributeError"



class SaveStringsTestCase(unittest.TestCase):
    def runTest(self):
        """Test caching string values of nodes."""
        test=TestCmd(workdir='')

        def setup(fs):
            fs.Dir('src')
            fs.Dir('d0')
            fs.Dir('d1')

            d0_f = fs.File('d0/f')
            d1_f = fs.File('d1/f')
            d0_b = fs.File('d0/b')
            d1_b = fs.File('d1/b')
            d1_f.duplicate = 1
            d1_b.duplicate = 1
            d0_b.builder = 1
            d1_b.builder = 1

            return [d0_f, d1_f, d0_b, d1_b]

        def modify(nodes):
            d0_f, d1_f, d0_b, d1_b = nodes
            d1_f.duplicate = 0
            d1_b.duplicate = 0
            d0_b.builder = 0
            d1_b.builder = 0

        fs1 = SCons.Node.FS.FS(test.workpath('fs1'))
        nodes = setup(fs1)
        fs1.VariantDir('d0', 'src', duplicate=0)
        fs1.VariantDir('d1', 'src', duplicate=1)

        s = list(map(str, nodes))
        expect = list(map(os.path.normpath, ['src/f', 'd1/f', 'd0/b', 'd1/b']))
        assert s == expect, s

        modify(nodes)

        s = list(map(str, nodes))
        expect = list(map(os.path.normpath, ['src/f', 'src/f', 'd0/b', 'd1/b']))
        assert s == expect, s

        SCons.Node.FS.save_strings(1)
        fs2 = SCons.Node.FS.FS(test.workpath('fs2'))
        nodes = setup(fs2)
        fs2.VariantDir('d0', 'src', duplicate=0)
        fs2.VariantDir('d1', 'src', duplicate=1)

        s = list(map(str, nodes))
        expect = list(map(os.path.normpath, ['src/f', 'd1/f', 'd0/b', 'd1/b']))
        assert s == expect, s

        modify(nodes)

        s = list(map(str, nodes))
        expect = list(map(os.path.normpath, ['src/f', 'd1/f', 'd0/b', 'd1/b']))
        assert s == expect, 'node str() not cached: %s'%s


class AbsolutePathTestCase(unittest.TestCase):
    def test_root_lookup_equivalence(self):
        """Test looking up /fff vs. fff in the / directory"""
        test=TestCmd(workdir='')

        fs = SCons.Node.FS.FS('/')

        save_cwd = os.getcwd()
        try:
            os.chdir('/')
            fff1 = fs.File('fff')
            fff2 = fs.File('/fff')
            assert fff1 is fff2, "fff and /fff returned different Nodes!"
        finally:
            os.chdir(save_cwd)



if __name__ == "__main__":
    unittest.main()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
