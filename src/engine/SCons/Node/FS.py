"""scons.Node.FS

File system nodes.

These Nodes represent the canonical external objects that people think
of when they think of building software: files and directories.

This initializes a "default_fs" Node with an FS at the current directory
for its own purposes, and for use by scripts or modules looking for the
canonical default.

"""

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
import shutil
import stat
import string
import sys
import cStringIO

import SCons.Action
import SCons.Errors
import SCons.Node
import SCons.Util
import SCons.Warnings

#
# SCons.Action objects for interacting with the outside world.
#
# The Node.FS methods in this module should use these actions to
# create and/or remove files and directories; they should *not* use
# os.{link,symlink,unlink,mkdir}(), etc., directly.
#
# Using these SCons.Action objects ensures that descriptions of these
# external activities are properly displayed, that the displays are
# suppressed when the -s (silent) option is used, and (most importantly)
# the actions are disabled when the the -n option is used, in which case
# there should be *no* changes to the external file system(s)...
#

if hasattr(os, 'symlink'):
    def _existsp(p):
        return os.path.exists(p) or os.path.islink(p)
else:
    _existsp = os.path.exists

def LinkFunc(target, source, env):
    src = source[0].path
    dest = target[0].path
    dir, file = os.path.split(dest)
    if dir and not os.path.isdir(dir):
        os.makedirs(dir)
    # Now actually link the files.  First try to make a hard link.  If that
    # fails, try a symlink.  If that fails then just copy it.
    try :
        os.link(src, dest)
    except (AttributeError, OSError):
        try :
            os.symlink(src, dest)
        except (AttributeError, OSError):
            shutil.copy2(src, dest)
            st=os.stat(src)
            os.chmod(dest, stat.S_IMODE(st[stat.ST_MODE]) | stat.S_IWRITE)
    return 0

Link = SCons.Action.Action(LinkFunc, None)

def LocalString(target, source, env):
    return 'Local copy of %s from %s' % (target[0], source[0])

LocalCopy = SCons.Action.Action(LinkFunc, LocalString)

def UnlinkFunc(target, source, env):
    os.unlink(target[0].path)
    return 0

Unlink = SCons.Action.Action(UnlinkFunc, None)

def MkdirFunc(target, source, env):
    os.mkdir(target[0].path)
    return 0

Mkdir = SCons.Action.Action(MkdirFunc, None)

def CacheRetrieveFunc(target, source, env):
    t = target[0]
    cachedir, cachefile = t.cachepath()
    if os.path.exists(cachefile):
        shutil.copy2(cachefile, t.path)
        st = os.stat(cachefile)
        os.chmod(t.path, stat.S_IMODE(st[stat.ST_MODE]) | stat.S_IWRITE)
        return 0
    return 1

def CacheRetrieveString(target, source, env):
    t = target[0]
    cachedir, cachefile = t.cachepath()
    if os.path.exists(cachefile):
        return "Retrieved `%s' from cache" % t.path
    return None

CacheRetrieve = SCons.Action.Action(CacheRetrieveFunc, CacheRetrieveString)

CacheRetrieveSilent = SCons.Action.Action(CacheRetrieveFunc, None)

def CachePushFunc(target, source, env):
    t = target[0]
    cachedir, cachefile = t.cachepath()
    if os.path.exists(cachefile):
        # Don't bother copying it if it's already there.
        return

    if not os.path.isdir(cachedir):
        os.mkdir(cachedir)

    tempfile = cachefile+'.tmp'
    try:
        shutil.copy2(t.path, tempfile)
        os.rename(tempfile, cachefile)
        st = os.stat(t.path)
        os.chmod(cachefile, stat.S_IMODE(st[stat.ST_MODE]) | stat.S_IWRITE)
    except OSError:
        # It's possible someone else tried writing the file at the same
        # time we did.  Print a warning but don't stop the build, since
        # it doesn't affect the correctness of the build.
        SCons.Warnings.warn(SCons.Warnings.CacheWriteErrorWarning,
                            "Unable to copy %s to cache. Cache file is %s"
                                % (str(target), cachefile))
        return

CachePush = SCons.Action.Action(CachePushFunc, None)

class _Null:
    pass

_null = _Null()

DefaultSCCSBuilder = None
DefaultRCSBuilder = None

def get_DefaultSCCSBuilder():
    global DefaultSCCSBuilder
    if DefaultSCCSBuilder is None:
        import SCons.Builder
        import SCons.Defaults
        DefaultSCCSBuilder = SCons.Builder.Builder(action = '$SCCSCOM',
                                                   env = SCons.Defaults.DefaultEnvironment())
    return DefaultSCCSBuilder

def get_DefaultRCSBuilder():
    global DefaultRCSBuilder
    if DefaultRCSBuilder is None:
        import SCons.Builder
        import SCons.Defaults
        DefaultRCSBuilder = SCons.Builder.Builder(action = '$RCS_COCOM',
                                                  env = SCons.Defaults.DefaultEnvironment())
    return DefaultRCSBuilder

#
class ParentOfRoot:
    """
    An instance of this class is used as the parent of the root of a
    filesystem (POSIX) or drive (Win32). This isn't actually a node,
    but it looks enough like one so that we don't have to have
    special purpose code everywhere to deal with dir being None. 
    This class is an instance of the Null object pattern.
    """
    def __init__(self):
        self.abspath = ''
        self.path = ''
        self.abspath_ = ''
        self.path_ = ''
        self.name=''
        self.duplicate=0
        self.srcdir=None
        self.build_dirs=[]
        
    def is_under(self, dir):
        return 0

    def up(self):
        return None

    def getRepositories(self):
        return []

    def get_dir(self):
        return None

    def recurse_get_path(self, dir, path_elems):
        return path_elems

    def src_builder(self):
        return _null

# Cygwin's os.path.normcase pretends it's on a case-sensitive filesystem.
_is_cygwin = sys.platform == "cygwin"
if os.path.normcase("TeSt") == os.path.normpath("TeSt") and not _is_cygwin:
    def _my_normcase(x):
        return x
else:
    def _my_normcase(x):
        return string.upper(x)

class EntryProxy(SCons.Util.Proxy):
    def __get_abspath(self):
        entry = self.get()
        return SCons.Util.SpecialAttrWrapper(entry.get_abspath(),
                                             entry.name + "_abspath")

    def __get_filebase(self):
        name = self.get().name
        return SCons.Util.SpecialAttrWrapper(SCons.Util.splitext(name)[0],
                                             name + "_filebase")

    def __get_suffix(self):
        name = self.get().name
        return SCons.Util.SpecialAttrWrapper(SCons.Util.splitext(name)[1],
                                             name + "_suffix")

    def __get_file(self):
        name = self.get().name
        return SCons.Util.SpecialAttrWrapper(name, name + "_file")

    def __get_base_path(self):
        """Return the file's directory and file name, with the
        suffix stripped."""
        entry = self.get()
        return SCons.Util.SpecialAttrWrapper(SCons.Util.splitext(entry.get_path())[0],
                                             entry.name + "_base")

    def __get_posix_path(self):
        """Return the path with / as the path separator, regardless
        of platform."""
        if os.sep == '/':
            return self
        else:
            entry = self.get()
            return SCons.Util.SpecialAttrWrapper(string.replace(entry.get_path(),
                                                                os.sep, '/'),
                                                 entry.name + "_posix")

    def __get_srcnode(self):
        return EntryProxy(self.get().srcnode())

    def __get_srcdir(self):
        """Returns the directory containing the source node linked to this
        node via BuildDir(), or the directory of this node if not linked."""
        return EntryProxy(self.get().srcnode().dir)

    def __get_dir(self):
        return EntryProxy(self.get().dir)
    
    dictSpecialAttrs = { "base" : __get_base_path,
                         "posix" : __get_posix_path,
                         "srcpath" : __get_srcnode,
                         "srcdir" : __get_srcdir,
                         "dir" : __get_dir,
                         "abspath" : __get_abspath,
                         "filebase" : __get_filebase,
                         "suffix" : __get_suffix,
                         "file" : __get_file }

    def __getattr__(self, name):
        # This is how we implement the "special" attributes
        # such as base, posix, srcdir, etc.
        try:
            return self.dictSpecialAttrs[name](self)
        except KeyError:
            try:
                attr = SCons.Util.Proxy.__getattr__(self, name)
            except AttributeError:
                entry = self.get()
                classname = string.split(str(entry.__class__), '.')[-1]
                raise AttributeError, "%s instance '%s' has no attribute '%s'" % (classname, entry.name, name)
            return attr

class Base(SCons.Node.Node):
    """A generic class for file system entries.  This class is for
    when we don't know yet whether the entry being looked up is a file
    or a directory.  Instances of this class can morph into either
    Dir or File objects by a later, more precise lookup.

    Note: this class does not define __cmp__ and __hash__ for
    efficiency reasons.  SCons does a lot of comparing of
    Node.FS.{Base,Entry,File,Dir} objects, so those operations must be
    as fast as possible, which means we want to use Python's built-in
    object identity comparisons.
    """

    def __init__(self, name, directory, fs):
        """Initialize a generic Node.FS.Base object.
        
        Call the superclass initialization, take care of setting up
        our relative and absolute paths, identify our parent
        directory, and indicate that this node should use
        signatures."""
        SCons.Node.Node.__init__(self)

        self.name = name
        self.fs = fs
        self.relpath = {}

        assert directory, "A directory must be provided"

        self.abspath = directory.abspath_ + name
        if directory.path == '.':
            self.path = name
        else:
            self.path = directory.path_ + name

        self.path_ = self.path
        self.abspath_ = self.abspath
        self.dir = directory
        self.cwd = None # will hold the SConscript directory for target nodes
        self.duplicate = directory.duplicate

    def clear(self):
        """Completely clear a Node.FS.Base object of all its cached
        state (so that it can be re-evaluated by interfaces that do
        continuous integration builds).
        """
        SCons.Node.Node.clear(self)
        try:
            delattr(self, '_exists')
        except AttributeError:
            pass
        try:
            delattr(self, '_rexists')
        except AttributeError:
            pass

    def get_dir(self):
        return self.dir

    def __str__(self):
        """A Node.FS.Base object's string representation is its path
        name."""
        if self.duplicate or self.is_derived():
            return self.get_path()
        return self.srcnode().get_path()

    def exists(self):
        try:
            return self._exists
        except AttributeError:
            self._exists = _existsp(self.abspath)
            return self._exists

    def rexists(self):
        try:
            return self._rexists
        except AttributeError:
            self._rexists = self.rfile().exists()
            return self._rexists

    def get_parents(self):
        parents = SCons.Node.Node.get_parents(self)
        if self.dir and not isinstance(self.dir, ParentOfRoot):
            parents.append(self.dir)
        return parents

    def current(self, calc):
        """If the underlying path doesn't exist, we know the node is
        not current without even checking the signature, so return 0.
        Otherwise, return None to indicate that signature calculation
        should proceed as normal to find out if the node is current."""
        bsig = calc.bsig(self)
        if not self.exists():
            return 0
        return calc.current(self, bsig)

    def is_under(self, dir):
        if self is dir:
            return 1
        else:
            return self.dir.is_under(dir)

    def set_local(self):
        self._local = 1

    def srcnode(self):
        """If this node is in a build path, return the node
        corresponding to its source file.  Otherwise, return
        ourself."""
        try:
            return self._srcnode
        except AttributeError:
            dir=self.dir
            name=self.name
            while dir:
                if dir.srcdir:
                    self._srcnode = self.fs.Entry(name, dir.srcdir,
                                                  klass=self.__class__)
                    return self._srcnode
                name = dir.name + os.sep + name
                dir=dir.get_dir()
            self._srcnode = self
            return self._srcnode

    def recurse_get_path(self, dir, path_elems):
        """Recursively build a path relative to a supplied directory
        node."""
        if self != dir:
            path_elems.append(self.name)
            path_elems = self.dir.recurse_get_path(dir, path_elems)
        return path_elems

    def get_path(self, dir=None):
        """Return path relative to the current working directory of the
        Node.FS.Base object that owns us."""
        if not dir:
            dir = self.fs.getcwd()
        try:
            return self.relpath[dir]
        except KeyError:
            if self == dir:
                # Special case, return "." as the path
                ret = '.'
            else:
                path_elems = self.recurse_get_path(dir, [])
                path_elems.reverse()
                ret = string.join(path_elems, os.sep)
            self.relpath[dir] = ret
            return ret
            
    def set_src_builder(self, builder):
        """Set the source code builder for this node."""
        self.sbuilder = builder

    def src_builder(self):
        """Fetch the source code builder for this node.

        If there isn't one, we cache the source code builder specified
        for the directory (which in turn will cache the value from its
        parent directory, and so on up to the file system root).
        """
        try:
            scb = self.sbuilder
        except AttributeError:
            scb = self.dir.src_builder()
            self.sbuilder = scb
        return scb

    def get_abspath(self):
        """Get the absolute path of the file."""
        return self.abspath

    def for_signature(self):
        # Return just our name.  Even an absolute path would not work,
        # because that can change thanks to symlinks or remapped network
        # paths.
        return self.name

    def get_subst_proxy(self):
        try:
            return self._proxy
        except AttributeError:
            ret = EntryProxy(self)
            self._proxy = ret
            return ret

class Entry(Base):
    """This is the class for generic Node.FS entries--that is, things
    that could be a File or a Dir, but we're just not sure yet.
    Consequently, the methods in this class really exist just to
    transform their associated object into the right class when the
    time comes, and then call the same-named method in the transformed
    class."""

    def rfile(self):
        """We're a generic Entry, but the caller is actually looking for
        a File at this point, so morph into one."""
        self.__class__ = File
        self._morph()
        self.clear()
        return File.rfile(self)

    def get_found_includes(self, env, scanner, target):
        """If we're looking for included files, it's because this Entry
        is really supposed to be a File itself."""
        node = self.rfile()
        return node.get_found_includes(env, scanner, target)

    def scanner_key(self):
        return SCons.Util.splitext(self.name)[1]

    def get_contents(self):
        """Fetch the contents of the entry.
        
        Since this should return the real contents from the file
        system, we check to see into what sort of subclass we should
        morph this Entry."""
        if os.path.isfile(self.abspath):
            self.__class__ = File
            self._morph()
            return File.get_contents(self)
        if os.path.isdir(self.abspath):
            self.__class__ = Dir
            self._morph()
            return Dir.get_contents(self)
        raise AttributeError

    def exists(self):
        """Return if the Entry exists.  Check the file system to see
        what we should turn into first.  Assume a file if there's no
        directory."""
        if os.path.isdir(self.abspath):
            self.__class__ = Dir
            self._morph()
            return Dir.exists(self)
        else:
            self.__class__ = File
            self._morph()
            self.clear()
            return File.exists(self)

    def calc_signature(self, calc):
        """Return the Entry's calculated signature.  Check the file
        system to see what we should turn into first.  Assume a file if
        there's no directory."""
        if os.path.isdir(self.abspath):
            self.__class__ = Dir
            self._morph()
            return Dir.calc_signature(self, calc)
        else:
            self.__class__ = File
            self._morph()
            self.clear()
            return File.calc_signature(self, calc)

# This is for later so we can differentiate between Entry the class and Entry
# the method of the FS class.
_classEntry = Entry


class FS:
    def __init__(self, path = None):
        """Initialize the Node.FS subsystem.

        The supplied path is the top of the source tree, where we
        expect to find the top-level build file.  If no path is
        supplied, the current directory is the default.

        The path argument must be a valid absolute path.
        """
        if path == None:
            self.pathTop = os.getcwd()
        else:
            self.pathTop = path
        self.Root = {}
        self.Top = None
        self.SConstruct_dir = None
        self.CachePath = None
        self.cache_force = None
        self.cache_show = None

    def set_toplevel_dir(self, path):
        assert not self.Top, "You can only set the top-level path on an FS object that has not had its File, Dir, or Entry methods called yet."
        self.pathTop = path

    def set_SConstruct_dir(self, dir):
        self.SConstruct_dir = dir
        
    def __setTopLevelDir(self):
        if not self.Top:
            self.Top = self.__doLookup(Dir, os.path.normpath(self.pathTop))
            self.Top.path = '.'
            self.Top.path_ = '.' + os.sep
            self._cwd = self.Top
        
    def getcwd(self):
        self.__setTopLevelDir()
        return self._cwd

    def __checkClass(self, node, klass):
        if klass == Entry:
            return node
        if node.__class__ == Entry:
            node.__class__ = klass
            node._morph()
            return node
        if not isinstance(node, klass):
            raise TypeError, "Tried to lookup %s '%s' as a %s." % \
                  (node.__class__.__name__, node.path, klass.__name__)
        return node
        
    def __doLookup(self, fsclass, name, directory = None, create = 1):
        """This method differs from the File and Dir factory methods in
        one important way: the meaning of the directory parameter.
        In this method, if directory is None or not supplied, the supplied
        name is expected to be an absolute path.  If you try to look up a
        relative path with directory=None, then an AssertionError will be
        raised."""

        if not name:
            # This is a stupid hack to compensate for the fact
            # that the POSIX and Win32 versions of os.path.normpath()
            # behave differently.  In particular, in POSIX:
            #   os.path.normpath('./') == '.'
            # in Win32
            #   os.path.normpath('./') == ''
            #   os.path.normpath('.\\') == ''
            #
            # This is a definite bug in the Python library, but we have
            # to live with it.
            name = '.'
        path_comp = string.split(name, os.sep)
        drive, path_first = os.path.splitdrive(path_comp[0])
        if not path_first:
            # Absolute path
            drive = _my_normcase(drive)
            try:
                directory = self.Root[drive]
            except KeyError:
                if not create:
                    raise SCons.Errors.UserError
                dir = Dir(drive, ParentOfRoot(), self)
                dir.path = dir.path + os.sep
                dir.abspath = dir.abspath + os.sep
                self.Root[drive] = dir
                directory = dir
            path_comp = path_comp[1:]
        else:
            path_comp = [ path_first, ] + path_comp[1:]

        if not path_comp:
            path_comp = ['']
            
        # Lookup the directory
        for path_name in path_comp[:-1]:
            path_norm = _my_normcase(path_name)
            try:
                directory = self.__checkClass(directory.entries[path_norm],
                                              Dir)
            except KeyError:
                if not create:
                    raise SCons.Errors.UserError

                # look at the actual filesystem and make sure there isn't
                # a file already there
                path = directory.path_ + path_name
                if os.path.isfile(path):
                    raise TypeError, \
                          "File %s found where directory expected." % path

                dir_temp = Dir(path_name, directory, self)
                directory.entries[path_norm] = dir_temp
                directory.add_wkid(dir_temp)
                directory = dir_temp
        file_name = _my_normcase(path_comp[-1])
        try:
            ret = self.__checkClass(directory.entries[file_name], fsclass)
        except KeyError:
            if not create:
                raise SCons.Errors.UserError

            # make sure we don't create File nodes when there is actually
            # a directory at that path on the disk, and vice versa
            path = directory.path_ + path_comp[-1]
            if fsclass == File:
                if os.path.isdir(path):
                    raise TypeError, \
                          "Directory %s found where file expected." % path
            elif fsclass == Dir:
                if os.path.isfile(path):
                    raise TypeError, \
                          "File %s found where directory expected." % path
            
            ret = fsclass(path_comp[-1], directory, self)
            directory.entries[file_name] = ret
            directory.add_wkid(ret)
        return ret

    def __transformPath(self, name, directory):
        """Take care of setting up the correct top-level directory,
        usually in preparation for a call to doLookup().

        If the path name is prepended with a '#', then it is unconditionally
        interpreted as relative to the top-level directory of this FS.

        If directory is None, and name is a relative path,
        then the same applies.
        """
        self.__setTopLevelDir()
        if name and name[0] == '#':
            directory = self.Top
            name = name[1:]
            if name and (name[0] == os.sep or name[0] == '/'):
                # Correct such that '#/foo' is equivalent
                # to '#foo'.
                name = name[1:]
            name = os.path.join('.', os.path.normpath(name))
        elif not directory:
            directory = self._cwd
        return (os.path.normpath(name), directory)

    def chdir(self, dir, change_os_dir=0):
        """Change the current working directory for lookups.
        If change_os_dir is true, we will also change the "real" cwd
        to match.
        """
        self.__setTopLevelDir()
        curr=self._cwd
        try:
            if not dir is None:
                self._cwd = dir
                if change_os_dir:
                    os.chdir(dir.abspath)
        except OSError:
            self._cwd = curr
            raise

    def Entry(self, name, directory = None, create = 1, klass=None):
        """Lookup or create a generic Entry node with the specified name.
        If the name is a relative path (begins with ./, ../, or a file
        name), then it is looked up relative to the supplied directory
        node, or to the top level directory of the FS (supplied at
        construction time) if no directory is supplied.
        """

        if not klass:
            klass = Entry

        if isinstance(name, Base):
            return self.__checkClass(name, klass)
        else:
            if directory and not isinstance(directory, Dir):
                directory = self.Dir(directory)
            name, directory = self.__transformPath(name, directory)
            return self.__doLookup(klass, name, directory, create)
    
    def File(self, name, directory = None, create = 1):
        """Lookup or create a File node with the specified name.  If
        the name is a relative path (begins with ./, ../, or a file name),
        then it is looked up relative to the supplied directory node,
        or to the top level directory of the FS (supplied at construction
        time) if no directory is supplied.

        This method will raise TypeError if a directory is found at the
        specified path.
        """

        return self.Entry(name, directory, create, File)
    
    def Dir(self, name, directory = None, create = 1):
        """Lookup or create a Dir node with the specified name.  If
        the name is a relative path (begins with ./, ../, or a file name),
        then it is looked up relative to the supplied directory node,
        or to the top level directory of the FS (supplied at construction
        time) if no directory is supplied.

        This method will raise TypeError if a normal file is found at the
        specified path.
        """

        return self.Entry(name, directory, create, Dir)
    
    def BuildDir(self, build_dir, src_dir, duplicate=1):
        """Link the supplied build directory to the source directory
        for purposes of building files."""
        
        self.__setTopLevelDir()
        if not isinstance(src_dir, SCons.Node.Node):
            src_dir = self.Dir(src_dir)
        if not isinstance(build_dir, SCons.Node.Node):
            build_dir = self.Dir(build_dir)
        if not src_dir.is_under(self.Top):
            raise SCons.Errors.UserError, "Source directory must be under top of build tree."
        if src_dir.is_under(build_dir):
            raise SCons.Errors.UserError, "Source directory cannot be under build directory."
        if build_dir.srcdir:
            if build_dir.srcdir == src_dir:
                return # We already did this.
            raise SCons.Errors.UserError, "'%s' already has a source directory: '%s'."%(build_dir, build_dir.srcdir)
        build_dir.link(src_dir, duplicate)

    def Repository(self, *dirs):
        """Specify Repository directories to search."""
        for d in dirs:
            if not isinstance(d, SCons.Node.Node):
                d = self.Dir(d)
            self.__setTopLevelDir()
            self.Top.addRepository(d)

    def Rsearch(self, path, clazz=_classEntry, cwd=None):
        """Search for something in a Repository.  Returns the first
        one found in the list, or None if there isn't one."""
        if isinstance(path, SCons.Node.Node):
            return path
        else:
            name, d = self.__transformPath(path, cwd)
            n = self.__doLookup(clazz, name, d)
            if n.exists():
                return n
            if isinstance(n, Dir):
                # If n is a Directory that has Repositories directly
                # attached to it, then any of those is a valid Repository
                # path.  Return the first one that exists.
                reps = filter(lambda x: x.exists(), n.getRepositories())
                if len(reps):
                    return reps[0]
            d = n.get_dir()
            name = n.name
            # Search repositories of all directories that this file is under.
            while d:
                for rep in d.getRepositories():
                    try:
                        rnode = self.__doLookup(clazz, name, rep)
                        # Only find the node if it exists and it is not
			# a derived file.  If for some reason, we are
			# explicitly building a file IN a Repository, we
			# don't want it to show up in the build tree.
			# This is usually the case with BuildDir().
			# We only want to find pre-existing files.
                        if rnode.exists() and \
                           (isinstance(rnode, Dir) or not rnode.is_derived()):
                            return rnode
                    except TypeError:
                        pass # Wrong type of node.
                # Prepend directory name
                name = d.name + os.sep + name
                # Go up one directory
                d = d.get_dir()
        return None

    def Rsearchall(self, pathlist, must_exist=1, clazz=_classEntry, cwd=None):
        """Search for a list of somethings in the Repository list."""
        ret = []
        if SCons.Util.is_String(pathlist):
            pathlist = string.split(pathlist, os.pathsep)
        if not SCons.Util.is_List(pathlist):
            pathlist = [pathlist]
        for path in pathlist:
            if isinstance(path, SCons.Node.Node):
                ret.append(path)
            else:
                name, d = self.__transformPath(path, cwd)
                n = self.__doLookup(clazz, name, d)
                if not must_exist or n.exists():
                    ret.append(n)
                if isinstance(n, Dir):
                    # If this node is a directory, then any repositories
                    # attached to this node can be repository paths.
                    ret.extend(filter(lambda x, me=must_exist, clazz=clazz: isinstance(x, clazz) and (not me or x.exists()),
                                      n.getRepositories()))
                    
                d = n.get_dir()
                name = n.name
                # Search repositories of all directories that this file
                # is under.
                while d:
                    for rep in d.getRepositories():
                        try:
                            rnode = self.__doLookup(clazz, name, rep)
                            # Only find the node if it exists (or
                            # must_exist is zero) and it is not a
                            # derived file.  If for some reason, we
                            # are explicitly building a file IN a
                            # Repository, we don't want it to show up in
                            # the build tree.  This is usually the case
                            # with BuildDir().  We only want to find
                            # pre-existing files.
                            if (not must_exist or rnode.exists()) and \
                               (not rnode.is_derived() or isinstance(rnode, Dir)):
                                ret.append(rnode)
                        except TypeError:
                            pass # Wrong type of node.
                    # Prepend directory name
                    name = d.name + os.sep + name
                    # Go up one directory
                    d = d.get_dir()
        return ret

    def CacheDir(self, path):
        self.CachePath = path

    def build_dir_target_climb(self, dir, tail):
        """Create targets in corresponding build directories

        Climb the directory tree, and look up path names
        relative to any linked build directories we find.
        """
        targets = []
        message = None
        while dir:
            for bd in dir.build_dirs:
                p = apply(os.path.join, [bd.path] + tail)
                targets.append(self.Entry(p))
            tail = [dir.name] + tail
            dir = dir.up()
        if targets:
            message = "building associated BuildDir targets: %s" % string.join(map(str, targets))
        return targets, message

class DummyExecutor:
    """Dummy executor class returned by Dir nodes to bamboozle SCons
    into thinking we are an actual derived node, where our sources are
    our directory entries."""
    def get_raw_contents(self):
        return ''
    def get_contents(self):
        return ''
    def get_timestamp(self):
        return 0

class Dir(Base):
    """A class for directories in a file system.
    """

    def __init__(self, name, directory, fs):
        Base.__init__(self, name, directory, fs)
        self._morph()

    def _morph(self):
        """Turn a file system node (either a freshly initialized
        directory object or a separate Entry object) into a
        proper directory object.
        
        Modify our paths to add the trailing slash that indicates
        a directory.  Set up this directory's entries and hook it
        into the file system tree.  Specify that directories (this
        node) don't use signatures for currency calculation."""

        self.path_ = self.path + os.sep
        self.abspath_ = self.abspath + os.sep
        self.repositories = []
        self.srcdir = None
        self.source_scanner = None
        
        self.entries = {}
        self.entries['.'] = self
        self.entries['..'] = self.dir
        self.cwd = self
        self.builder = 1
        self.searched = 0
        self._sconsign = None
        self.build_dirs = []

    def __clearRepositoryCache(self, duplicate=None):
        """Called when we change the repository(ies) for a directory.
        This clears any cached information that is invalidated by changing
        the repository."""

        for node in self.entries.values():
            if node != self.dir:
                if node != self and isinstance(node, Dir):
                    node.__clearRepositoryCache(duplicate)
                else:
                    try:
                        del node._srcreps
                    except AttributeError:
                        pass
                    try:
                        del node._rfile
                    except AttributeError:
                        pass
                    try:
                        del node._rexists
                    except AttributeError:
                        pass
                    try:
                        del node._exists
                    except AttributeError:
                        pass
                    try:
                        del node._srcnode
                    except AttributeError:
                        pass
                    if duplicate != None:
                        node.duplicate=duplicate
    
    def __resetDuplicate(self, node):
        if node != self:
            node.duplicate = node.get_dir().duplicate

    def Entry(self, name):
        """Create an entry node named 'name' relative to this directory."""
        return self.fs.Entry(name, self)

    def Dir(self, name):
        """Create a directory node named 'name' relative to this directory."""
        return self.fs.Dir(name, self)

    def File(self, name):
        """Create a file node named 'name' relative to this directory."""
        return self.fs.File(name, self)

    def link(self, srcdir, duplicate):
        """Set this directory as the build directory for the
        supplied source directory."""
        self.srcdir = srcdir
        self.duplicate = duplicate
        self.__clearRepositoryCache(duplicate)
        srcdir.build_dirs.append(self)

    def getRepositories(self):
        """Returns a list of repositories for this directory."""
        if self.srcdir and not self.duplicate:
            try:
                return self._srcreps
            except AttributeError:
                self._srcreps = self.fs.Rsearchall(self.srcdir.path,
                                                   clazz=Dir,
                                                   must_exist=0,
                                                   cwd=self.fs.Top) \
                                + self.repositories
                return self._srcreps
        return self.repositories

    def addRepository(self, dir):
        if not dir in self.repositories and dir != self:
            self.repositories.append(dir)
            self.__clearRepositoryCache()

    def up(self):
        return self.entries['..']

    def root(self):
        if not self.entries['..']:
            return self
        else:
            return self.entries['..'].root()

    def children(self, scan=1):
        return filter(lambda x, i=self.ignore: x not in i,
                             self.all_children(scan))

    def all_children(self, scan=1):
        # Before we traverse our children, make sure we have created Nodes
        # for any files that this directory contains.  We need to do this
        # so any change in a file in this directory will cause it to
        # be out of date.
        if not self.searched:
            try:
                for filename in os.listdir(self.abspath):
                    if filename != '.sconsign':
                        self.Entry(filename)
            except OSError:
                # Directory does not exist.  No big deal
                pass
            self.searched = 1
        keys = filter(lambda k: k != '.' and k != '..', self.entries.keys())
        kids = map(lambda x, s=self: s.entries[x], keys)
        def c(one, two):
            if one.abspath < two.abspath:
               return -1
            if one.abspath > two.abspath:
               return 1
            return 0
        kids.sort(c)
        return kids + SCons.Node.Node.all_children(self, 0)

    def get_actions(self):
        """A null "builder" for directories."""
        return []

    def build(self):
        """A null "builder" for directories."""
        pass

    def alter_targets(self):
        """Return any corresponding targets in a build directory.
        """
        return self.fs.build_dir_target_climb(self, [])

    def scanner_key(self):
        """A directory does not get scanned."""
        return None

    def set_bsig(self, bsig):
        """A directory has no signature."""
        bsig = None

    def set_csig(self, csig):
        """A directory has no signature."""
        csig = None

    def get_contents(self):
        """Return aggregate contents of all our children."""
        contents = cStringIO.StringIO()
        for kid in self.children(None):
            contents.write(kid.get_contents())
        return contents.getvalue()
    
    def prepare(self):
        pass

    def current(self, calc):
        """If all of our children were up-to-date, then this
        directory was up-to-date, too."""
        state = 0
        for kid in self.children(None):
            s = kid.get_state()
            if s and (not state or s > state):
                state = s
        import SCons.Node
        if state == 0 or state == SCons.Node.up_to_date:
            return 1
        else:
            return 0

    def rdir(self):
        try:
            return self._rdir
        except AttributeError:
            self._rdir = self
            if not self.exists():
                n = self.fs.Rsearch(self.path, clazz=Dir, cwd=self.fs.Top)
                if n:
                    self._rdir = n
            return self._rdir

    def sconsign(self):
        """Return the .sconsign file info for this directory,
        creating it first if necessary."""
        if not self._sconsign:
            import SCons.Sig
            self._sconsign = SCons.Sig.SConsignForDirectory(self)
        return self._sconsign

    def srcnode(self):
        """Dir has a special need for srcnode()...if we
        have a srcdir attribute set, then that *is* our srcnode."""
        if self.srcdir:
            return self.srcdir
        return Base.srcnode(self)

    def get_executor(self, create=1):
        """Fetch the action executor for this node.  Create one if
        there isn't already one, and requested to do so."""
        try:
            executor = self.executor
        except AttributeError:
            executor = DummyExecutor()
            self.executor = executor
        return executor

    def get_timestamp(self):
        """Return the latest timestamp from among our children"""
        stamp = 0
        for kid in self.children(None):
            if kid.get_timestamp() > stamp:
                stamp = kid.get_timestamp()
        return stamp

class File(Base):
    """A class for files in a file system.
    """
    def __init__(self, name, directory, fs):
        Base.__init__(self, name, directory, fs)
        self._morph()

    def Entry(self, name):
        """Create an entry node named 'name' relative to
        the SConscript directory of this file."""
        return self.fs.Entry(name, self.cwd)

    def Dir(self, name):
        """Create a directory node named 'name' relative to
        the SConscript directory of this file."""
        return self.fs.Dir(name, self.cwd)

    def File(self, name):
        """Create a file node named 'name' relative to
        the SConscript directory of this file."""
        return self.fs.File(name, self.cwd)

    def RDirs(self, pathlist):
        """Search for a list of directories in the Repository list."""
        return self.fs.Rsearchall(pathlist, clazz=Dir, must_exist=0,
                                  cwd=self.cwd)
    
    def generate_build_env(self, env):
        """Generate an appropriate Environment to build this File."""
        return env.Override({'Dir' : self.Dir,
                             'File' : self.File,
                             'RDirs' : self.RDirs})
        
    def _morph(self):
        """Turn a file system node into a File object."""
        self.scanner_paths = {}
        self.found_includes = {}
        if not hasattr(self, '_local'):
            self._local = 0

    def root(self):
        return self.dir.root()

    def scanner_key(self):
        return SCons.Util.splitext(self.name)[1]

    def get_contents(self):
        if not self.rexists():
            return ''
        return open(self.rfile().abspath, "rb").read()

    def get_timestamp(self):
        if self.rexists():
            return os.path.getmtime(self.rfile().abspath)
        else:
            return 0

    def store_csig(self):
        self.dir.sconsign().set_csig(self.name, self.get_csig())

    def store_bsig(self):
        self.dir.sconsign().set_bsig(self.name, self.get_bsig())

    def store_implicit(self):
        self.dir.sconsign().set_implicit(self.name, self.implicit)

    def store_timestamp(self):
        self.dir.sconsign().set_timestamp(self.name, self.get_timestamp())

    def get_prevsiginfo(self):
        """Fetch the previous signature information from the
        .sconsign entry."""
        return self.dir.sconsign().get(self.name)

    def get_stored_implicit(self):
        return self.dir.sconsign().get_implicit(self.name)

    def get_found_includes(self, env, scanner, target):
        """Return the included implicit dependencies in this file.
        Cache results so we only scan the file once regardless of
        how many times this information is requested."""
        if not scanner:
            return []

        try:
            path = target.scanner_paths[scanner]
        except AttributeError:
            # The target had no scanner_paths attribute, which means
            # it's an Alias or some other node that's not actually a
            # file.  In that case, back off and use the path for this
            # node itself.
            try:
                path = self.scanner_paths[scanner]
            except KeyError:
                path = scanner.path(env, self.cwd)
                self.scanner_paths[scanner] = path
        except KeyError:
            path = scanner.path(env, target.cwd)
            target.scanner_paths[scanner] = path

        try:
            includes = self.found_includes[path]
        except KeyError:
            includes = scanner(self, env, path)
            self.found_includes[path] = includes

        return includes

    def _createDir(self):
        # ensure that the directories for this node are
        # created.

        listDirs = []
        parent=self.dir
        while parent:
            if parent.exists():
                break
            listDirs.append(parent)
            p = parent.up()
            if isinstance(p, ParentOfRoot):
                raise SCons.Errors.StopError, parent.path
            parent = p
        listDirs.reverse()
        for dirnode in listDirs:
            try:
                Mkdir(dirnode, None, None)
                # The Mkdir() action may or may not have actually
                # created the directory, depending on whether the -n
                # option was used or not.  Delete the _exists and
                # _rexists attributes so they can be reevaluated.
                try:
                    delattr(dirnode, '_exists')
                except AttributeError:
                    pass
                try:
                    delattr(dirnode, '_rexists')
                except AttributeError:
                    pass
            except OSError:
                pass

    def build(self):
        """Actually build the file.

        This overrides the base class build() method to check for the
        existence of derived files in a CacheDir before going ahead and
        building them.

        This method is called from multiple threads in a parallel build,
        so only do thread safe stuff here. Do thread unsafe stuff in
        built().
        """
        b = self.is_derived()
        if not b and not self.has_src_builder():
            return
        if b and self.fs.CachePath:
            if self.fs.cache_show:
                if CacheRetrieveSilent(self, None, None) == 0:
                    def do_print(action, targets, sources, env, self=self):
                        if action.strfunction:
                            al = action.strfunction(targets, self.sources, env)
                            if not SCons.Util.is_List(al):
                                al = [al]
                            for a in al:
                                action.show(a)
                    self._for_each_action(do_print)
                    return
            elif CacheRetrieve(self, None, None) == 0:
                return
        SCons.Node.Node.build(self)

    def built(self):
        """Called just after this node is sucessfully built."""
        # Push this file out to cache before the superclass Node.built()
        # method has a chance to clear the build signature, which it
        # will do if this file has a source scanner.
        if self.fs.CachePath and os.path.exists(self.path):
            CachePush(self, None, None)
        SCons.Node.Node.built(self)
        self.found_includes = {}
        try:
            delattr(self, '_exists')
        except AttributeError:
            pass
        try:
            delattr(self, '_rexists')
        except AttributeError:
            pass

    def visited(self):
        if self.fs.CachePath and self.fs.cache_force and os.path.exists(self.path):
            CachePush(self, None, None)

    def has_src_builder(self):
        """Return whether this Node has a source builder or not.

        If this Node doesn't have an explicit source code builder, this
        is where we figure out, on the fly, if there's a transparent
        source code builder for it.

        Note that if we found a source builder, we also set the
        self.builder attribute, so that all of the methods that actually
        *build* this file don't have to do anything different.
        """
        try:
            scb = self.sbuilder
        except AttributeError:
            if self.rexists():
                scb = None
            else:
                scb = self.dir.src_builder()
                if scb is _null:
                    scb = None
                    dir = self.dir.path
                    sccspath = os.path.join('SCCS', 's.' + self.name)
                    if dir != '.':
                        sccspath = os.path.join(dir, sccspath)
                    if os.path.exists(sccspath):
                        scb = get_DefaultSCCSBuilder()
                    else:
                        rcspath = os.path.join('RCS', self.name + ',v')
                        if dir != '.':
                            rcspath = os.path.join(dir, rcspath)
                        if os.path.exists(rcspath):
                            scb = get_DefaultRCSBuilder()
                self.builder = scb
            self.sbuilder = scb
        return not scb is None

    def alter_targets(self):
        """Return any corresponding targets in a build directory.
        """
        if self.is_derived():
            return [], None
        return self.fs.build_dir_target_climb(self.dir, [self.name])

    def is_pseudo_derived(self):
        return self.has_src_builder()
    
    def prepare(self):
        """Prepare for this file to be created."""
        SCons.Node.Node.prepare(self)

        if self.get_state() != SCons.Node.up_to_date:
            if self.exists():
                if self.is_derived() and not self.precious:
                    try:
                        Unlink(self, None, None)
                    except OSError, e:
                        raise SCons.Errors.BuildError(node = self,
                                                      errstr = e.strerror)
                    try:
                        delattr(self, '_exists')
                    except AttributeError:
                        pass
            else:
                try:
                    self._createDir()
                except SCons.Errors.StopError, drive:
                    desc = "No drive `%s' for target `%s'." % (drive, self)
                    raise SCons.Errors.StopError, desc

    def remove(self):
        """Remove this file."""
        if _existsp(self.path):
            os.unlink(self.path)
            return 1
        return None

    def exists(self):
        # Duplicate from source path if we are set up to do this.
        if self.duplicate and not self.is_derived() and not self.linked:
            src=self.srcnode().rfile()
            if src.exists() and src.abspath != self.abspath:
                self._createDir()
                try:
                    Unlink(self, None, None)
                except OSError:
                    pass
                try:
                    Link(self, src, None)
                except IOError, e:
                    desc = "Cannot duplicate `%s' in `%s': %s." % (src, self.dir, e.strerror)
                    raise SCons.Errors.StopError, desc
                self.linked = 1
                # The Link() action may or may not have actually
                # created the file, depending on whether the -n
                # option was used or not.  Delete the _exists and
                # _rexists attributes so they can be reevaluated.
                try:
                    delattr(self, '_exists')
                except AttributeError:
                    pass
                try:
                    delattr(self, '_rexists')
                except AttributeError:
                    pass
        return Base.exists(self)

    def current(self, calc):
        bsig = calc.bsig(self)
        if not self.exists():
            # The file doesn't exist locally...
            r = self.rfile()
            if r != self:
                # ...but there is one in a Repository...
                if calc.current(r, bsig):
                    # ...and it's even up-to-date...
                    if self._local:
                        # ...and they'd like a local copy.
                        LocalCopy(self, r, None)
                        self.set_bsig(bsig)
                        self.store_bsig()
                    return 1
            self._rfile = self
            return None
        else:
            return calc.current(self, bsig)

    def rfile(self):
        try:
            return self._rfile
        except AttributeError:
            self._rfile = self
            if not self.exists():
                n = self.fs.Rsearch(self.path, clazz=File,
                                    cwd=self.fs.Top)
                if n:
                    self._rfile = n
            return self._rfile

    def rstr(self):
        return str(self.rfile())

    def cachepath(self):
        if self.fs.CachePath:
            bsig = self.get_bsig()
            if bsig is None:
                raise SCons.Errors.InternalError, "cachepath(%s) found a bsig of None" % self.path
            bsig = str(bsig)
            subdir = string.upper(bsig[0])
            dir = os.path.join(self.fs.CachePath, subdir)
            return dir, os.path.join(dir, bsig)
        return None, None

    def target_from_source(self, prefix, suffix, splitext=SCons.Util.splitext):
        return self.dir.File(prefix + splitext(self.name)[0] + suffix)


default_fs = FS()


def find_file(filename, paths, node_factory = default_fs.File):
    """
    find_file(str, [Dir()]) -> [nodes]

    filename - a filename to find
    paths - a list of directory path *nodes* to search in

    returns - the node created from the found file.

    Find a node corresponding to either a derived file or a file
    that exists already.

    Only the first file found is returned, and none is returned
    if no file is found.
    """
    retval = None
    for dir in paths:
        try:
            node = node_factory(filename, dir)
            # Return true of the node exists or is a derived node.
            if node.is_derived() or \
               (isinstance(node, SCons.Node.FS.Base) and node.exists()):
                retval = node
                break
        except TypeError:
            # If we find a directory instead of a file, we don't care
            pass

    return retval

def find_files(filenames, paths, node_factory = default_fs.File):
    """
    find_files([str], [Dir()]) -> [nodes]

    filenames - a list of filenames to find
    paths - a list of directory path *nodes* to search in

    returns - the nodes created from the found files.

    Finds nodes corresponding to either derived files or files
    that exist already.

    Only the first file found is returned for each filename,
    and any files that aren't found are ignored.
    """
    nodes = map(lambda x, paths=paths, node_factory=node_factory:
                       find_file(x, paths, node_factory),
                filenames)
    return filter(lambda x: x != None, nodes)
