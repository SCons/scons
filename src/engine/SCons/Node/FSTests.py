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

import os
import os.path
import string
import sys
import time
import unittest
from TestCmd import TestCmd
import shutil
import stat

import SCons.Errors
import SCons.Node.FS
import SCons.Warnings

built_it = None

# This will be built-in in 2.3.  For now fake it.
try :
    True , False
except NameError :
    True = 1 ; False = 0


scanner_count = 0

class Scanner:
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
    def _update(self, dict):
        pass

class Action:
    def __call__(self, targets, sources, env, errfunc, **kw):
        global built_it
        if kw.get('execute', 1):
            built_it = 1
        return 0
    def show(self, string):
        pass
    def strfunction(self, targets, sources, env):
        return ""
class Builder:
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

class BuildDirTestCase(unittest.TestCase):
    def runTest(self):
        """Test build dir functionality"""
        test=TestCmd(workdir='')

        fs = SCons.Node.FS.FS()
        f1 = fs.File('build/test1')
        fs.BuildDir('build', 'src')
        f2 = fs.File('build/test2')
        d1 = fs.Dir('build')
        assert f1.srcnode().path == os.path.normpath('src/test1'), f1.srcnode().path
        assert f2.srcnode().path == os.path.normpath('src/test2'), f2.srcnode().path
        assert d1.srcnode().path == 'src', d1.srcnode().path

        fs = SCons.Node.FS.FS()
        f1 = fs.File('build/test1')
        fs.BuildDir('build', '.')
        f2 = fs.File('build/test2')
        d1 = fs.Dir('build')
        assert f1.srcnode().path == 'test1', f1.srcnode().path
        assert f2.srcnode().path == 'test2', f2.srcnode().path
        assert d1.srcnode().path == '.', d1.srcnode().path

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

        # A source file in a subdir of the source directory
        test.subdir([ 'work', 'src', 'new_dir' ])
        test.write([ 'work', 'src', 'new_dir', 'test9.out' ], 'test9.out\n')

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

        os.chdir(test.workpath('work'))

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
        # ...but the actual file is not there...
        assert not os.path.exists(f1.get_abspath())
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
        # ...and exists() should copy the file from src to build path
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
        assert f3.rfile().path == os.path.normpath(test.workpath('rep1/src/test2.in')),\
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
        assert f7.rfile().path == os.path.normpath(test.workpath('rep1/build/var1/test2.out')),\
               f7.rfile().path

        assert not f8.exists()
        assert f8.rexists()
        assert f8.rfile().path == os.path.normpath(test.workpath('rep1/build/var2/test2.out')),\
               f8.rfile().path

        # Verify the Mkdir and Link actions are called
        d9 = fs.Dir('build/var2/new_dir')
        f9 = fs.File('build/var2/new_dir/test9.out')

        class MkdirAction(Action):
            def __init__(self, dir_made):
                self.dir_made = dir_made
            def __call__(self, target, source, env, errfunc):
                self.dir_made.extend(target)

        save_Link = SCons.Node.FS.Link
        link_made = []
        def link_func(target, source, env, link_made=link_made):
            link_made.append(target)
        SCons.Node.FS.Link = link_func

        try:
            dir_made = []
            d9.builder = Builder(fs.Dir, action=MkdirAction(dir_made))
            f9.exists()
            expect = os.path.join('build', 'var2', 'new_dir')
            assert dir_made[0].path == expect, dir_made[0].path
            expect = os.path.join('build', 'var2', 'new_dir', 'test9.out')
            assert link_made[0].path == expect, link_made[0].path
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
        assert f10.get_contents() == 'stuff', f10.get_contents()

        f11 = fs.File('src/file11')
        t, m = f11.alter_targets()
        bdt = map(lambda n: n.path, t)
        var1_file11 = os.path.normpath('build/var1/file11')
        var2_file11 = os.path.normpath('build/var2/file11')
        assert bdt == [var1_file11, var2_file11], bdt

        f12 = fs.File('src/file12')
        f12.builder = 1
        bdt, m = f12.alter_targets()
        assert bdt == [], map(lambda n: n.path, bdt)

        d13 = fs.Dir('src/new_dir')
        t, m = d13.alter_targets()
        bdt = map(lambda n: n.path, t)
        var1_new_dir = os.path.normpath('build/var1/new_dir')
        var2_new_dir = os.path.normpath('build/var2/new_dir')
        assert bdt == [var1_new_dir, var2_new_dir], bdt

        # Test that an IOError trying to Link a src file
        # into a BuildDir ends up throwing a StopError.
        fIO = fs.File("build/var2/IOError")

        save_Link = SCons.Node.FS.Link
        def Link_IOError(target, source, env):
            raise IOError, "Link_IOError"
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

        exc_caught = 0
        try:
            fs = SCons.Node.FS.FS()
            fs.BuildDir('build', '/test/foo')
        except SCons.Errors.UserError:
            exc_caught = 1
        assert exc_caught, "Should have caught a UserError."

        exc_caught = 0
        try:
            try:
                fs = SCons.Node.FS.FS()
                fs.BuildDir('build', 'build/src')
            except SCons.Errors.UserError:
                exc_caught = 1
            assert exc_caught, "Should have caught a UserError."
        finally:
            test.unlink( "src/foo" )
            test.unlink( "build/foo" )

        fs = SCons.Node.FS.FS()
        fs.BuildDir('build', 'src1')

        # Calling the same BuildDir twice should work fine.
        fs.BuildDir('build', 'src1')

        # Trying to move a build dir to a second source dir
        # should blow up
        try:
            fs.BuildDir('build', 'src2')
        except SCons.Errors.UserError:
            pass
        else:
            assert 0, "Should have caught a UserError."

        # Test against a former bug.  Make sure we can get a repository
        # path for the build directory itself!
        fs=SCons.Node.FS.FS(test.workpath('work'))
        test.subdir('work')
        fs.BuildDir('build/var3', 'src', duplicate=0)
        d1 = fs.Dir('build/var3')
        r = d1.rdir()
        assert r == d1, "%s != %s" % (r, d1)

        # verify the link creation attempts in file_link()
        class LinkSimulator :
            """A class to intercept os.[sym]link() calls and track them."""

            def __init__( self, duplicate ) :
                self.duplicate = duplicate
                self._reset()

            def _reset( self ) :
                """Reset the simulator if necessary"""
                if not self._need_reset() : return # skip if not needed now
                self.links_to_be_called = self.duplicate

            def _need_reset( self ) :
                """
                Determines whether or not the simulator needs to be reset.
                A reset is necessary if the object is first being initialized,
                or if all three methods have been tried already.
                """
                return (
                        ( not hasattr( self , "links_to_be_called" ) )
                        or
                        (self.links_to_be_called == "")
                       )

            def link_fail( self , src , dest ) :
                self._reset()
                l = string.split(self.links_to_be_called, "-")
                next_link = l[0]
                assert  next_link == "hard", \
                       "Wrong link order: expected %s to be called "\
                       "instead of hard" % next_link
                self.links_to_be_called = string.join(l[1:], '-')
                raise OSError( "Simulating hard link creation error." )

            def symlink_fail( self , src , dest ) :
                self._reset()
                l = string.split(self.links_to_be_called, "-")
                next_link = l[0]
                assert  next_link == "soft", \
                       "Wrong link order: expected %s to be called "\
                       "instead of soft" % next_link
                self.links_to_be_called = string.join(l[1:], '-')
                raise OSError( "Simulating symlink creation error." )

            def copy( self , src , dest ) :
                self._reset()
                l = string.split(self.links_to_be_called, "-")
                next_link = l[0]
                assert  next_link == "copy", \
                       "Wrong link order: expected %s to be called "\
                       "instead of copy" % next_link
                self.links_to_be_called = string.join(l[1:], '-')
                # copy succeeds, but use the real copy
                self._real_copy(src, dest)
        # end class LinkSimulator

        try:
            SCons.Node.FS.set_duplicate("no-link-order")
            assert 0, "Expected exception when passing an invalid duplicate to set_duplicate"
        except SCons.Errors.InternalError:
            pass

        for duplicate in SCons.Node.FS.Valid_Duplicates:
            simulator = LinkSimulator(duplicate)

            # save the real functions for later restoration
            real_link = None
            real_symlink = None
            try:
                real_link = os.link
            except AttributeError:
                pass
            try:
                real_symlink = os.symlink
            except AttributeError:
                pass
            real_copy = shutil.copy2
            simulator._real_copy = real_copy # the simulator needs the real one

            # override the real functions with our simulation
            os.link = simulator.link_fail
            os.symlink = simulator.symlink_fail
            shutil.copy2 = simulator.copy
            SCons.Node.FS.set_duplicate(duplicate)

            src_foo = test.workpath('src', 'foo')
            build_foo = test.workpath('build', 'foo')

            try:
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

        # Test BuildDir "reflection," where a same-named subdirectory
        # exists underneath a build_dir.
        fs = SCons.Node.FS.FS()
        fs.BuildDir('work/src/b1/b2', 'work/src')

        dir_list = [
                'work/src',
                'work/src/b1',
                'work/src/b1/b2',
                'work/src/b1/b2/b1',
                'work/src/b1/b2/b1/b2',
        ]

        srcnode_map = {
                'work/src/b1/b2' : 'work/src',
                'work/src/b1/b2/f' : 'work/src/f',
                'work/src/b1/b2/b1' : 'work/src/b1/',
                'work/src/b1/b2/b1/f' : 'work/src/b1/f',
                'work/src/b1/b2/b1/b2' : 'work/src/b1/b2',
                'work/src/b1/b2/b1/b2/f' : 'work/src/b1/b2/f',
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

            dp = dnode.srcnode().path
            expect = os.path.normpath(srcnode_map.get(dir, dir))
            if dp != expect:
                print "Dir `%s' srcnode() `%s' != expected `%s'" % (dir, dp, expect)
                errors = errors + 1

            fp = fnode.srcnode().path
            expect = os.path.normpath(srcnode_map.get(f, f))
            if fp != expect:
                print "File `%s' srcnode() `%s' != expected `%s'" % (f, fp, expect)
                errors = errors + 1

        for dir in dir_list:
            dnode = fs.Dir(dir)
            f = dir + '/f'
            fnode = fs.File(dir + '/f')

            t, m = dnode.alter_targets()
            tp = t[0].path
            expect = os.path.normpath(alter_map.get(dir, dir))
            if tp != expect:
                print "Dir `%s' alter_targets() `%s' != expected `%s'" % (dir, tp, expect)
                errors = errors + 1

            t, m = fnode.alter_targets()
            tp = t[0].path
            expect = os.path.normpath(alter_map.get(f, f))
            if tp != expect:
                print "File `%s' alter_targets() `%s' != expected `%s'" % (f, tp, expect)
                errors = errors + 1

        self.failIf(errors)

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

        e1 = fs.Entry('e1')
        assert isinstance(e1, SCons.Node.FS.Entry)

        d1 = fs.Dir('d1')
        assert isinstance(d1, SCons.Node.FS.Dir)
        assert d1.cwd is d1, d1

        f1 = fs.File('f1', directory = d1)
        assert isinstance(f1, SCons.Node.FS.File)

        d1_f1 = os.path.join('d1', 'f1')
        assert f1.path == d1_f1, "f1.path %s != %s" % (f1.path, d1_f1)
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
            assert 0

        assert x1.Entry(x4) == x4
        try:
            x1.Dir(x4)
        except TypeError:
            pass
        else:
            assert 0

        x6 = x1.File(x6)
        assert isinstance(x6, SCons.Node.FS.File)

        x7 = x1.Dir(x7)
        assert isinstance(x7, SCons.Node.FS.Dir)

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
                assert dir.get_abspath() == abspath, \
                       "dir.abspath %s != expected absolute path %s" % \
                       (dir.get_abspath(), abspath)
                assert dir.up().path == up_path, \
                       "dir.up().path %s != expected parent path %s" % \
                       (dir.up().path, up_path)

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

            # Test that just specifying the drive works to identify
            # its root directory.
            p = os.path.abspath(test.workpath('root_file'))
            drive, path = os.path.splitdrive(p)
            if drive:
                # The assert below probably isn't correct for the
                # general case, but it works for Win32, which covers a
                # lot of ground...
                dir = fs.Dir(drive)
                assert str(dir) == drive + os.sep, str(dir)

            # Test Dir.scan()
            dir = fs.Dir('ddd')
            fs.File(string.join(['ddd', 'f1'], sep))
            fs.File(string.join(['ddd', 'f2'], sep))
            fs.File(string.join(['ddd', 'f3'], sep))
            fs.Dir(string.join(['ddd', 'd1'], sep))
            fs.Dir(string.join(['ddd', 'd1', 'f4'], sep))
            fs.Dir(string.join(['ddd', 'd1', 'f5'], sep))
            dir.scan()
            kids = map(lambda x: x.path, dir.children(None))
            kids.sort()
            assert kids == [os.path.join('ddd', 'd1'),
                            os.path.join('ddd', 'f1'),
                            os.path.join('ddd', 'f2'),
                            os.path.join('ddd', 'f3')], kids

        # Test for a bug in 0.04 that did not like looking up
        # dirs with a trailing slash on Win32.
        d=fs.Dir('./')
        assert d.path == '.', d.abspath
        d=fs.Dir('foo/')
        assert d.path == 'foo', d.abspath

        # Test for sub-classing of node building.
        global built_it

        built_it = None
        assert not built_it
        d1.add_source([SCons.Node.Node()])    # XXX FAKE SUBCLASS ATTRIBUTE
        d1.builder_set(Builder(fs.File))
        d1.env_set(Environment())
        d1.build()
        assert built_it

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
        match(e1.dir.path, ".")

        e2 = fs.Entry("d1/f1")
        assert e2.__class__.__name__ == 'File'
        match(e2.path, "d1/f1")
        match(e2.dir.path, "d1")

        e3 = fs.Entry("e3")
        assert e3.__class__.__name__ == 'Entry'
        match(e3.path, "e3")
        match(e3.dir.path, ".")

        e4 = fs.Entry("d1/e4")
        assert e4.__class__.__name__ == 'Entry'
        match(e4.path, "d1/e4")
        match(e4.dir.path, "d1")

        e5 = fs.Entry("e3/e5")
        assert e3.__class__.__name__ == 'Dir'
        match(e3.path, "e3")
        match(e3.dir.path, ".")
        assert e5.__class__.__name__ == 'Entry'
        match(e5.path, "e3/e5")
        match(e5.dir.path, "e3")

        e6 = fs.Dir("d1/e4")
        assert e6 is e4
        assert e4.__class__.__name__ == 'Dir'
        match(e4.path, "d1/e4")
        match(e4.dir.path, "d1")

        e7 = fs.File("e3/e5")
        assert e7 is e5
        assert e5.__class__.__name__ == 'File'
        match(e5.path, "e3/e5")
        match(e5.dir.path, "e3")

        fs.chdir(fs.Dir('subdir'))
        f11 = fs.File("f11")
        match(f11.path, "subdir/f11")
        d12 = fs.Dir("d12")
        e13 = fs.Entry("subdir/e13")
        match(e13.path, "subdir/subdir/e13")
        fs.chdir(fs.Dir('..'))

        # Test scanning
        f1.builder_set(Builder(fs.File))
        f1.env_set(Environment())
        xyz = fs.File("xyz")
        f1.builder.target_scanner = Scanner(xyz)

        f1.scan()
        assert f1.implicit[0].path == "xyz"
        f1.implicit = []
        f1.scan()
        assert f1.implicit == []
        f1.implicit = None
        f1.scan()
        assert f1.implicit[0].path == "xyz"

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
        class DummyNode:
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
        assert fs.getcwd().path == 'subdir', fs.getcwd().path
        fs.chdir(fs.Dir('../..'))
        assert fs.getcwd().path == test.workdir, fs.getcwd().path

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

        # For some reason, in Win32, the \x1a character terminates
        # the reading of files in text mode.  This tests that
        # get_contents() returns the binary contents.
        test.write("binary_file", "Foo\x1aBar")
        f1 = SCons.Node.FS.default_fs.File(test.workpath("binary_file"))
        assert f1.get_contents() == "Foo\x1aBar", f1.get_contents()

        def nonexistent(method, s):
            try:
                x = method(s, create = 0)
            except SCons.Errors.UserError:
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
        try:
            e = fs.Entry('file')
            c = e.get_contents()
            assert c == "file\n", c
            assert e.__class__ == SCons.Node.FS.File
        finally:
            test.unlink("file")

        test.subdir("dir")
        e = fs.Entry('dir')
        c = e.get_contents()
        assert c == "", c
        assert e.__class__ == SCons.Node.FS.Dir

        if hasattr(os, 'symlink'):
            os.symlink('nonexistent', test.workpath('dangling_symlink'))
            e = fs.Entry('dangling_symlink')
            c = e.get_contents()
            assert e.__class__ == SCons.Node.FS.Entry
            assert c == "", c

        test.write("tstamp", "tstamp\n")
        try:
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
        finally:
            test.unlink("tstamp")

        test.subdir('tdir1')
        d = fs.Dir('tdir1')
        t = d.get_timestamp()
        assert t == 0, "expected 0, got %s" % str(t)

        test.subdir('tdir2')
        d = fs.Dir('tdir2')
        f1 = test.workpath('tdir2', 'file1')
        f2 = test.workpath('tdir2', 'file2')
        test.write(f1, 'file1\n')
        test.write(f2, 'file2\n')
        fs.File(f1)
        fs.File(f2)
        current_time = float(int(time.time() / 2) * 2)
        t1 = current_time - 4.0
        t2 = current_time - 2.0
        os.utime(f1, (t1 - 2.0, t1))
        os.utime(f2, (t2 - 2.0, t2))
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
        assert not os.path.exists(test.workpath('exists')), "exists was not removed"

        symlink = test.workpath('symlink')
        try:
            os.symlink(test.workpath('does_not_exist'), symlink)
            assert os.path.islink(symlink)
            f = fs.File('symlink')
            r = f.remove()
            assert r, r
            assert not os.path.islink(symlink), "symlink was not removed"
        except AttributeError:
            pass

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

        x = fs.File('x.c')
        t = x.target_from_source('pre-', '-suf')
        assert str(t) == 'pre-x-suf', str(t)

        y = fs.File('dir/y')
        t = y.target_from_source('pre-', '-suf')
        assert str(t) == os.path.join('dir', 'pre-y-suf'), str(t)

        z = fs.File('zz')
        t = z.target_from_source('pre-', '-suf', lambda x: x[:-1])
        assert str(t) == 'pre-z-suf', str(t)

class DirTestCase(_tempdirTestCase):

    def test_entry_exists_on_disk(self):
        """Test the Dir.entry_exists_on_disk() method
        """
        test = self.test

        does_not_exist = self.fs.Dir('does_not_exist')
        assert not does_not_exist.entry_exists_on_disk('foo')

        test.subdir('d')
        test.write(['d', 'exists'], "d/exists\n")

        d = self.fs.Dir('d')
        assert d.entry_exists_on_disk('exists')
        assert not d.entry_exists_on_disk('does_not_exist')

    def test_srcdir_list(self):
        """Test the Dir.srcdir_list() method
        """
        src = self.fs.Dir('src')
        bld = self.fs.Dir('bld')
        sub1 = bld.Dir('sub')
        sub2 = sub1.Dir('sub')
        sub3 = sub2.Dir('sub')
        self.fs.BuildDir(bld, src, duplicate=0)
        self.fs.BuildDir(sub2, src, duplicate=0)

        s = map(str, src.srcdir_list())
        assert s == [], s

        s = map(str, bld.srcdir_list())
        assert s == ['src'], s

        s = map(str, sub1.srcdir_list())
        assert s == ['src/sub'], s

        s = map(str, sub2.srcdir_list())
        assert s == ['src', 'src/sub/sub'], s

        s = map(str, sub3.srcdir_list())
        assert s == ['src/sub', 'src/sub/sub/sub'], s

        self.fs.BuildDir('src/b1/b2', 'src')
        b1 = src.Dir('b1')
        b1_b2 = b1.Dir('b2')
        b1_b2_b1 = b1_b2.Dir('b1')
        b1_b2_b1_b2 = b1_b2_b1.Dir('b2')
        b1_b2_b1_b2_sub = b1_b2_b1_b2.Dir('sub')

        s = map(str, b1.srcdir_list())
        assert s == [], s

        s = map(str, b1_b2.srcdir_list())
        assert s == ['src'], s

        s = map(str, b1_b2_b1.srcdir_list())
        assert s == ['src/b1'], s

        s = map(str, b1_b2_b1_b2.srcdir_list())
        assert s == [], s

        s = map(str, b1_b2_b1_b2_sub.srcdir_list())
        assert s == [], s

    def test_srcdir_duplicate(self):
        """Test the Dir.srcdir_duplicate() method
        """
        test = self.test

        test.subdir('src0')
        test.write(['src0', 'exists'], "src0/exists\n")

        bld0 = self.fs.Dir('bld0')
        src0 = self.fs.Dir('src0')
        self.fs.BuildDir(bld0, src0, duplicate=0)

        n = bld0.srcdir_duplicate('does_not_exist', SCons.Node.FS.File)
        assert n is None, n
        assert not os.path.exists(test.workpath('bld0', 'does_not_exist'))

        n = bld0.srcdir_duplicate('exists', SCons.Node.FS.File)
        assert str(n) == 'src0/exists', str(n)
        assert not os.path.exists(test.workpath('bld0', 'exists'))

        test.subdir('src1')
        test.write(['src1', 'exists'], "src0/exists\n")

        bld1 = self.fs.Dir('bld1')
        src1 = self.fs.Dir('src1')
        self.fs.BuildDir(bld1, src1, duplicate=1)

        n = bld1.srcdir_duplicate('does_not_exist', SCons.Node.FS.File)
        assert n is None, n
        assert not os.path.exists(test.workpath('bld1', 'does_not_exist'))

        n = bld1.srcdir_duplicate('exists', SCons.Node.FS.File)
        assert str(n) == 'bld1/exists', str(n)
        assert os.path.exists(test.workpath('bld1', 'exists'))

    def test_srcdir_find_file(self):
        """Test the Dir.srcdir_find_file() method
        """
        test = self.test

        return_true = lambda: 1

        test.subdir('src0')
        test.write(['src0', 'on-disk-f1'], "src0/on-disk-f1\n")
        test.write(['src0', 'on-disk-f2'], "src0/on-disk-f2\n")

        bld0 = self.fs.Dir('bld0')
        src0 = self.fs.Dir('src0')
        self.fs.BuildDir(bld0, src0, duplicate=0)

        derived = src0.File('derived-f')
        derived.is_derived = return_true
        pseudo = src0.File('pseudo-f')
        pseudo.is_pseudo_derived = return_true
        exists = src0.File('exists-f')
        exists.exists = return_true

        # First check from the source directory.
        n = src0.srcdir_find_file('does_not_exist')
        assert n == (None, None), n

        n = src0.srcdir_find_file('derived-f')
        n = map(str, n)
        assert n == ['src0/derived-f', 'src0'], n

        n = src0.srcdir_find_file('pseudo-f')
        n = map(str, n)
        assert n == ['src0/pseudo-f', 'src0'], n

        n = src0.srcdir_find_file('exists-f')
        n = map(str, n)
        assert n == ['src0/exists-f', 'src0'], n

        n = src0.srcdir_find_file('on-disk-f1')
        n = map(str, n)
        assert n == ['src0/on-disk-f1', 'src0'], n

        # Now check from the build directory.
        n = bld0.srcdir_find_file('does_not_exist')
        assert n == (None, None), n

        n = bld0.srcdir_find_file('derived-f')
        n = map(str, n)
        assert n == ['src0/derived-f', 'bld0'], n

        n = bld0.srcdir_find_file('pseudo-f')
        n = map(str, n)
        assert n == ['src0/pseudo-f', 'bld0'], n

        n = bld0.srcdir_find_file('exists-f')
        n = map(str, n)
        assert n == ['src0/exists-f', 'bld0'], n

        n = bld0.srcdir_find_file('on-disk-f2')
        n = map(str, n)
        assert n == ['src0/on-disk-f2', 'bld0'], n


        test.subdir('src1')
        test.write(['src1', 'on-disk-f1'], "src1/on-disk-f1\n")
        test.write(['src1', 'on-disk-f2'], "src1/on-disk-f2\n")

        bld1 = self.fs.Dir('bld1')
        src1 = self.fs.Dir('src1')
        self.fs.BuildDir(bld1, src1, duplicate=1)

        derived = src1.File('derived-f')
        derived.is_derived = return_true
        pseudo = src1.File('pseudo-f')
        pseudo.is_pseudo_derived = return_true
        exists = src1.File('exists-f')
        exists.exists = return_true

        # First check from the source directory.
        n = src1.srcdir_find_file('does_not_exist')
        assert n == (None, None), n

        n = src1.srcdir_find_file('derived-f')
        n = map(str, n)
        assert n == ['src1/derived-f', 'src1'], n

        n = src1.srcdir_find_file('pseudo-f')
        n = map(str, n)
        assert n == ['src1/pseudo-f', 'src1'], n

        n = src1.srcdir_find_file('exists-f')
        n = map(str, n)
        assert n == ['src1/exists-f', 'src1'], n

        n = src1.srcdir_find_file('on-disk-f1')
        n = map(str, n)
        assert n == ['src1/on-disk-f1', 'src1'], n

        # Now check from the build directory.
        n = bld1.srcdir_find_file('does_not_exist')
        assert n == (None, None), n

        n = bld1.srcdir_find_file('derived-f')
        n = map(str, n)
        assert n == ['bld1/derived-f', 'src1'], n

        n = bld1.srcdir_find_file('pseudo-f')
        n = map(str, n)
        assert n == ['bld1/pseudo-f', 'src1'], n

        n = bld1.srcdir_find_file('exists-f')
        n = map(str, n)
        assert n == ['bld1/exists-f', 'src1'], n

        n = bld1.srcdir_find_file('on-disk-f2')
        n = map(str, n)
        assert n == ['bld1/on-disk-f2', 'bld1'], n

class EntryTestCase(unittest.TestCase):
    def runTest(self):
        """Test methods specific to the Entry sub-class.
        """
        test = TestCmd(workdir='')
        # FS doesn't like the cwd to be something other than its root.
        os.chdir(test.workpath(""))

        fs = SCons.Node.FS.FS()

        e1 = fs.Entry('e1')
        e1.rfile()
        assert e1.__class__ is SCons.Node.FS.File, e1.__class__

        e2 = fs.Entry('e2')
        e2.get_found_includes(None, None, None)
        assert e2.__class__ is SCons.Node.FS.File, e2.__class__

        test.subdir('e3d')
        test.write('e3f', "e3f\n")

        e3d = fs.Entry('e3d')
        e3d.get_contents()
        assert e3d.__class__ is SCons.Node.FS.Dir, e3d.__class__

        e3f = fs.Entry('e3f')
        e3f.get_contents()
        assert e3f.__class__ is SCons.Node.FS.File, e3f.__class__

        e3n = fs.Entry('e3n')
        exc_caught = None
        try:
            e3n.get_contents()
        except AttributeError:
            exc_caught = 1
        assert exc_caught, "did not catch expected AttributeError"

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

        class MyCalc:
            def __init__(self, val):
                self.max_drift = 0
                class M:
                    def __init__(self, val):
                        self.val = val
                    def collect(self, args):
                        return reduce(lambda x, y: x+y, args)
                    def signature(self, executor):
                        return self.val + 222
                self.module = M(val)

        test.subdir('e5d')
        test.write('e5f', "e5f\n")

        e5d = fs.Entry('e5d')
        sig = e5d.calc_signature(MyCalc(555))
        assert e5d.__class__ is SCons.Node.FS.Dir, e5d.__class__
        # Node has builder (MkDirBuilder), so executor will calculate
        # the build signature.
        assert sig == 777, sig

        e5f = fs.Entry('e5f')
        sig = e5f.calc_signature(MyCalc(666))
        assert e5f.__class__ is SCons.Node.FS.File, e5f.__class__
        # This node has no builder, so it just calculates the
        # signature once: the source content signature.
        assert sig == 888, sig

        e5n = fs.Entry('e5n')
        sig = e5n.calc_signature(MyCalc(777))
        assert e5n.__class__ is SCons.Node.FS.File, e5n.__class__
        # Doesn't exist, no sources, and no builder: no sig
        assert sig is None, sig



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
        r = map(lambda x, np=os.path.normpath: np(str(x)), rep)
        assert r == expect, r

    def test_rfile(self):
        """Test the File.rfile() method"""
        f1 = self.fs.File('f1')
        f2 = self.fs.File('f2')
        f3 = self.fs.File('f3')

        self.test.write([self.rep1, 'f2'], "")
        self.test.subdir([self.rep2, 'f3'])
        self.test.write([self.rep3, 'f3'], "")

        assert f1.rfile() is f1

        r = f2.rfile()
        assert not r is f2, r
        assert str(r) == os.path.join(self.rep1, 'f2'), str(r)

        r = f3.rfile()
        assert not r is f3, r
        r = f3.rstr()
        assert r == os.path.join(self.rep3, 'f3'), r

    def test_Rsearches(self):
        """Test the Rsearch() methods"""
        fs = self.fs
        test = self.test

        test.write([self.rep1, 'f2'], "")
        test.subdir([self.rep2, 'f3'])
        test.write([self.rep3, 'f3'], "")

        r = fs.Rsearch('f1')
        assert r is None, r

        r = fs.Rsearch('f2')
        assert r, r

        f3 = fs.File('f3')
        r = fs.Rsearch(f3)
        assert r is f3, r

    def test_Rsearchall(self):
        """Test the Rsearchall() methods"""
        fs = self.fs
        test = self.test

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

        fs.File('d2').built() # Clear exists cache
        test.subdir(['work', 'd2'])

        list = fs.Rsearchall('d2')
        assert map(str, list) == ['d2'], list

        fs.File('../rep2/d2').built() # Clear exists cache
        test.subdir(['rep2', 'd2'])

        list = fs.Rsearchall('d2')
        assert map(str, list) == ['d2', test.workpath('rep2', 'd2')], list

        fs.File('../rep1/d2').built() # Clear exists cache
        test.subdir(['rep1', 'd2'])

        list = fs.Rsearchall('d2')
        assert map(str, list) == ['d2',
                                  test.workpath('rep1', 'd2'),
                                  test.workpath('rep2', 'd2')], list

        list = fs.Rsearchall(['d3', 'd4'])
        assert list == [], list

        fs.File('d3').built() # Clear exists cache
        test.subdir(['work', 'd3'])

        list = map(str, fs.Rsearchall(['d3', 'd4']))
        assert list == ['d3'], list

        fs.File('../rep3/d4').built() # Clear exists cache
        test.subdir(['rep3', 'd4'])

        list = map(str, fs.Rsearchall(['d3', 'd4']))
        assert list == ['d3', test.workpath('rep3', 'd4')], list

        list = map(str, fs.Rsearchall(string.join(['d3', 'd4'], os.pathsep)))
        assert list == ['d3', test.workpath('rep3', 'd4')], list

        work_d4 = fs.File(os.path.join('work', 'd4'))

        list = map(str, fs.Rsearchall(['d3', work_d4]))
        assert list == ['d3', str(work_d4)], list

        list = fs.Rsearchall('')
        assert list == [], list

        list = fs.Rsearchall([None])
        assert list == [], list

        list = fs.Rsearchall([''])
        assert list == [], list

    def test_rexists(self):
        """Test the Entry.rexists() method"""
        fs = self.fs
        test = self.test

        test.write([self.rep1, 'f2'], "")

        fs.BuildDir('build', '.')

        f = fs.File(test.workpath("work", "i_do_not_exist"))
        assert not f.rexists()

        test.write([self.rep2, "i_exist"], "\n")
        f = fs.File(test.workpath("work", "i_exist"))
        assert f.rexists()

        test.write(["work", "i_exist_too"], "\n")
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
            tstamp = float(int(time.time() / 2) * 2) - 2
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
            assert c == "Con\x1aTents\n", "got '%s'" % c
        finally:
            test.unlink(["rep3", "contents"])

    #def test calc_signature(self):

    #def test current(self):



class find_fileTestCase(unittest.TestCase):
    def runTest(self):
        """Testing find_file function"""
        test = TestCmd(workdir = '')
        test.write('./foo', 'Some file\n')
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

        paths = map(fs.Dir, ['.', 'same', './bar'])
        nodes = [SCons.Node.FS.find_file('foo', paths)]
        nodes.append(SCons.Node.FS.find_file('baz', paths))
        nodes.append(SCons.Node.FS.find_file('pseudo', paths))
        nodes.append(SCons.Node.FS.find_file('same', paths))

        file_names = map(str, nodes)
        file_names = map(os.path.normpath, file_names)
        expect = ['./foo', './bar/baz', './pseudo', './bar/same']
        expect = map(os.path.normpath, expect)
        assert file_names == expect, file_names

        # Make sure we don't blow up if there's already a File in place
        # of a directory that we'd otherwise try to search.  If this
        # is broken, we'll see an exception like "Tried to lookup File
        # 'bar/baz' as a Dir.
        SCons.Node.FS.find_file('baz/no_file_here', paths)

        import StringIO
        save_sys_stdout = sys.stdout

        try:
            sio = StringIO.StringIO()
            sys.stdout = sio
            SCons.Node.FS.find_file('foo', paths, verbose="xyz")
            expect = "  xyz: looking for 'foo' in '.' ...\n" + \
                     "  xyz: ... FOUND 'foo' in '.'\n"
            c = sio.getvalue()
            assert c == expect, c

            sio = StringIO.StringIO()
            sys.stdout = sio
            SCons.Node.FS.find_file('baz', paths, verbose=1)
            expect = "  find_file: looking for 'baz' in '.' ...\n" + \
                     "  find_file: looking for 'baz' in 'same' ...\n" + \
                     "  find_file: looking for 'baz' in 'bar' ...\n" + \
                     "  find_file: ... FOUND 'baz' in 'bar'\n"
            c = sio.getvalue()
            assert c == expect, c

            sio = StringIO.StringIO()
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
        assert str(d) == 'sub'
        assert d.exists()
        f = fs.File('file', 'sub')
        assert str(f) == os.path.join('sub', 'file')
        assert not f.exists()

class stored_infoTestCase(unittest.TestCase):
    def runTest(self):
        """Test how storing build information"""
        test = TestCmd(workdir = '')
        test.subdir('sub')
        fs = SCons.Node.FS.FS(test.workpath(''))

        d = fs.Dir('sub')
        f = fs.File('file1', d)
        bi = f.get_stored_info()
        assert bi.bsig == None, bi.bsig

        class MySConsign:
            class Null:
                def __init__(self):
                    self.xyzzy = 7
            def get_entry(self, name):
                return self.Null()

        f = fs.File('file2', d)
        f.dir.sconsign = MySConsign
        bi = f.get_stored_info()
        assert bi.xyzzy == 7, bi

class has_src_builderTestCase(unittest.TestCase):
    def runTest(self):
        """Test the has_src_builder() method"""
        test = TestCmd(workdir = '')
        fs = SCons.Node.FS.FS(test.workpath(''))
        os.chdir(test.workpath(''))
        test.subdir('sub1')
        test.subdir('sub2', ['sub2', 'SCCS'], ['sub2', 'RCS'])

        sub1 = fs.Dir('sub1', '.')
        f1 = fs.File('f1', sub1)
        f2 = fs.File('f2', sub1)
        f3 = fs.File('f3', sub1)
        sub2 = fs.Dir('sub2', '.')
        f4 = fs.File('f4', sub2)
        f5 = fs.File('f5', sub2)
        f6 = fs.File('f6', sub2)
        f7 = fs.File('f7', sub2)
        f8 = fs.File('f8', sub2)

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

        f7.set_src_builder(b1)
        f8.builder_set(b1)

        test.write(['sub2', 'SCCS', 's.f5'], "sub2/SCCS/s.f5\n")
        test.write(['sub2', 'RCS', 'f6,v'], "sub2/RCS/f6,v\n")
        h = f4.has_src_builder()
        assert not h, h
        h = f4.has_builder()
        assert not h, h
        h = f5.has_src_builder()
        assert h, h
        h = f5.has_builder()
        assert h, h
        h = f6.has_src_builder()
        assert h, h
        h = f6.has_builder()
        assert h, h
        h = f7.has_src_builder()
        assert h, h
        h = f7.has_builder()
        assert h, h
        h = f8.has_src_builder()
        assert not h, h
        h = f8.has_builder()
        assert h, h

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
            def __call__(self, target, source, env, errfunc):
                self.dir_made.extend(target)

        dir_made = []
        new_dir = fs.Dir("new_dir")
        new_dir.builder = Builder(fs.Dir, action=MkdirAction(dir_made))
        xyz = fs.File(os.path.join("new_dir", "xyz"))

        xyz.set_state(SCons.Node.up_to_date)
        xyz.prepare()
        assert dir_made == [], dir_made

        xyz.set_state(0)
        xyz.prepare()
        assert dir_made[0].path == "new_dir", dir_made[0]

        dir = fs.Dir("dir")
        dir.prepare()

class SConstruct_dirTestCase(unittest.TestCase):
    def runTest(self):
        """Test setting the SConstruct directory"""

        fs = SCons.Node.FS.FS()
        fs.set_SConstruct_dir(fs.Dir('xxx'))
        assert fs.SConstruct_dir.path == 'xxx'

class CacheDirTestCase(unittest.TestCase):
    def runTest(self):
        """Test CacheDir functionality"""
        test = TestCmd(workdir='')

        global built_it

        fs = SCons.Node.FS.FS()
        assert fs.CachePath is None, fs.CachePath
        assert fs.cache_force is None, fs.cache_force
        assert fs.cache_show is None, fs.cache_show

        fs.CacheDir('cache')
        assert fs.CachePath == 'cache', fs.CachePath

        save_CacheRetrieve = SCons.Node.FS.CacheRetrieve
        self.retrieved = []
        def retrieve_succeed(target, source, env, self=self, execute=1):
            self.retrieved.append(target)
            return 0
        def retrieve_fail(target, source, env, self=self, execute=1):
            self.retrieved.append(target)
            return 1

        f1 = fs.File("cd.f1")
        f1.builder_set(Builder(fs.File))
        f1.env_set(Environment())
        try:
            SCons.Node.FS.CacheRetrieve = retrieve_succeed
            self.retrieved = []
            built_it = None

            r = f1.retrieve_from_cache()
            assert r == 1, r
            assert self.retrieved == [f1], self.retrieved
            assert built_it is None, built_it

            SCons.Node.FS.CacheRetrieve = retrieve_fail
            self.retrieved = []
            built_it = None

            r = f1.retrieve_from_cache()
            assert r is None, r
            assert self.retrieved == [f1], self.retrieved
            assert built_it is None, built_it
        finally:
            SCons.Node.FS.CacheRetrieve = save_CacheRetrieve

        save_CacheRetrieveSilent = SCons.Node.FS.CacheRetrieveSilent

        fs.cache_show = 1

        f2 = fs.File("cd.f2")
        f2.builder_set(Builder(fs.File))
        f2.env_set(Environment())
        try:
            SCons.Node.FS.CacheRetrieveSilent = retrieve_succeed
            self.retrieved = []
            built_it = None

            r = f2.retrieve_from_cache()
            assert r == 1, r
            assert self.retrieved == [f2], self.retrieved
            assert built_it is None, built_it

            SCons.Node.FS.CacheRetrieveSilent = retrieve_fail
            self.retrieved = []
            built_it = None

            r = f2.retrieve_from_cache()
            assert r is None, r
            assert self.retrieved == [f2], self.retrieved
            assert built_it is None, built_it
        finally:
            SCons.Node.FS.CacheRetrieveSilent = save_CacheRetrieveSilent

        save_CachePush = SCons.Node.FS.CachePush
        def push(target, source, env, self=self):
            self.pushed.append(target)
            return 0
        SCons.Node.FS.CachePush = push

        try:
            self.pushed = []

            cd_f3 = test.workpath("cd.f3")
            f3 = fs.File(cd_f3)
            f3.built()
            assert self.pushed == [], self.pushed
            test.write(cd_f3, "cd.f3\n")
            f3.built()
            assert self.pushed == [f3], self.pushed

            self.pushed = []

            cd_f4 = test.workpath("cd.f4")
            f4 = fs.File(cd_f4)
            f4.visited()
            assert self.pushed == [], self.pushed
            test.write(cd_f4, "cd.f4\n")
            f4.visited()
            assert self.pushed == [], self.pushed
            fs.cache_force = 1
            f4.visited()
            assert self.pushed == [f4], self.pushed
        finally:
            SCons.Node.FS.CachePush = save_CachePush

        # Verify how the cachepath() method determines the name
        # of the file in cache.
        def my_collect(list):
            return list[0]
        save_collect = SCons.Sig.MD5.collect
        SCons.Sig.MD5.collect = my_collect
        try:
            f5 = fs.File("cd.f5")
            f5.binfo = f5.new_binfo()
            f5.binfo.bsig = 'a_fake_bsig'
            cp = f5.cachepath()
            dirname = os.path.join('cache', 'A')
            filename = os.path.join(dirname, 'a_fake_bsig')
            assert cp == (dirname, filename), cp
        finally:
            SCons.Sig.MD5.collect = save_collect

        # Verify that no bsig raises an InternalERror
        f6 = fs.File("cd.f6")
        f6.binfo = f6.new_binfo()
        exc_caught = 0
        try:
            cp = f6.cachepath()
        except SCons.Errors.InternalError:
            exc_caught = 1
        assert exc_caught

        # Verify that we raise a warning if we can't copy a file to cache.
        save_copy2 = shutil.copy2
        def copy2(src, dst):
            raise OSError
        shutil.copy2 = copy2
        save_mkdir = os.mkdir
        def mkdir(dir, mode=0):
            pass
        os.mkdir = mkdir
        old_warn_exceptions = SCons.Warnings.warningAsException(1)
        SCons.Warnings.enableWarningClass(SCons.Warnings.CacheWriteErrorWarning)

        try:
            cd_f7 = test.workpath("cd.f7")
            test.write(cd_f7, "cd.f7\n")
            f7 = fs.File(cd_f7)
            f7.binfo = f7.new_binfo()
            f7.binfo.bsig = 'f7_bsig'

            warn_caught = 0
            try:
                f7.built()
            except SCons.Warnings.CacheWriteErrorWarning:
                warn_caught = 1
            assert warn_caught
        finally:
            shutil.copy2 = save_copy2
            os.mkdir = save_mkdir
            SCons.Warnings.warningAsException(old_warn_exceptions)
            SCons.Warnings.suppressWarningClass(SCons.Warnings.CacheWriteErrorWarning)

        # Verify that we don't blow up if there's no strfunction()
        # for an action.
        act = Action()
        act.strfunction = None
        f8 = fs.File("cd.f8")
        f8.builder_set(Builder(fs.File, action=act))
        f8.env_set(Environment())
        try:
            SCons.Node.FS.CacheRetrieveSilent = retrieve_succeed
            self.retrieved = []
            built_it = None

            r = f8.retrieve_from_cache()
            assert r == 1, r
            assert self.retrieved == [f8], self.retrieved
            assert built_it is None, built_it

            SCons.Node.FS.CacheRetrieveSilent = retrieve_fail
            self.retrieved = []
            built_it = None

            r = f8.retrieve_from_cache()
            assert r is None, r
            assert self.retrieved == [f8], self.retrieved
            assert built_it is None, built_it
        finally:
            SCons.Node.FS.CacheRetrieveSilent = save_CacheRetrieveSilent

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

        s = str(f.abspath)
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

        s = str(f.win32)
        assert s == 'foo\\bar\\baz.blat', repr(s)
        assert f.win32.is_literal(), f.win32
        if f.win32 != f:
            for_sig = f.win32.for_signature()
            assert for_sig == 'baz.blat_win32', for_sig

        # And now, combinations!!!
        s = str(f.srcpath.base)
        assert s == os.path.normpath('foo/bar/baz'), s
        s = str(f.srcpath.dir)
        assert s == str(f.srcdir), s
        s = str(f.srcpath.posix)
        assert s == 'foo/bar/baz.blat', s
        s = str(f.srcpath.win32)
        assert s == 'foo\\bar\\baz.blat', s

        # Test what happens with BuildDir()
        fs.BuildDir('foo', 'baz')

        s = str(f.srcpath)
        assert s == os.path.normpath('baz/bar/baz.blat'), s
        assert f.srcpath.is_literal(), f.srcpath
        g = f.srcpath.get()
        assert isinstance(g, SCons.Node.FS.Entry), g.__class__

        s = str(f.srcdir)
        assert s == os.path.normpath('baz/bar'), s
        assert f.srcdir.is_literal(), f.srcdir
        g = f.srcdir.get()
        assert isinstance(g, SCons.Node.FS.Dir), g.__class__

        # And now what happens with BuildDir() + Repository()
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
        assert isinstance(g, SCons.Node.FS.Entry), g.__class__

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
        except AttributeError, e:
            assert str(e) == "Dir instance 'ddd' has no attribute 'no_such_attr'", e
            caught = 1
        assert caught, "did not catch expected AttributeError"

        caught = None
        try:
            fs.Entry('eee').get_subst_proxy().no_such_attr
        except AttributeError, e:
            assert str(e) == "Entry instance 'eee' has no attribute 'no_such_attr'", e
            caught = 1
        assert caught, "did not catch expected AttributeError"

        caught = None
        try:
            fs.File('fff').get_subst_proxy().no_such_attr
        except AttributeError, e:
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
        fs1.BuildDir('d0', 'src', duplicate=0)
        fs1.BuildDir('d1', 'src', duplicate=1)

        s = map(str, nodes)
        expect = map(os.path.normpath, ['src/f', 'd1/f', 'd0/b', 'd1/b'])
        assert s == expect, s

        modify(nodes)

        s = map(str, nodes)
        expect = map(os.path.normpath, ['src/f', 'src/f', 'd0/b', 'd1/b'])
        assert s == expect, s

        SCons.Node.FS.save_strings(1)
        fs2 = SCons.Node.FS.FS(test.workpath('fs2'))
        nodes = setup(fs2)
        fs2.BuildDir('d0', 'src', duplicate=0)
        fs2.BuildDir('d1', 'src', duplicate=1)

        s = map(str, nodes)
        expect = map(os.path.normpath, ['src/f', 'd1/f', 'd0/b', 'd1/b'])
        assert s == expect, s

        modify(nodes)

        s = map(str, nodes)
        expect = map(os.path.normpath, ['src/f', 'd1/f', 'd0/b', 'd1/b'])
        assert s == expect, 'node str() not cached: %s'%s

if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(FSTestCase())
    suite.addTest(BuildDirTestCase())
    suite.addTest(EntryTestCase())
    suite.addTest(find_fileTestCase())
    suite.addTest(StringDirTestCase())
    suite.addTest(stored_infoTestCase())
    suite.addTest(has_src_builderTestCase())
    suite.addTest(prepareTestCase())
    suite.addTest(SConstruct_dirTestCase())
    suite.addTest(CacheDirTestCase())
    suite.addTest(clearTestCase())
    suite.addTest(disambiguateTestCase())
    suite.addTest(postprocessTestCase())
    suite.addTest(SpecialAttrTestCase())
    suite.addTest(SaveStringsTestCase())
    tclasses = [
        DirTestCase,
        RepositoryTestCase,
    ]
    for tclass in tclasses:
        names = unittest.getTestCaseNames(tclass, 'test_')
        suite.addTests(map(tclass, names))
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
        sys.exit(1)
