"""scons.Node.FS

File system nodes.

This initializes a "default_fs" Node with an FS at the current directory
for its own purposes, and for use by scripts or modules looking for the
canonical default.

"""

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

import string
import os
import os.path
import types
import SCons.Node
from UserDict import UserDict
import sys
from SCons.Errors import UserError

try:
    import os
    file_link = os.link
except AttributeError:
    import shutil
    import stat
    def file_link(src, dest):
        shutil.copyfile(src, dest)
        st=os.stat(src)
        os.chmod(dest, stat.S_IMODE(st[stat.ST_MODE]) | stat.S_IWRITE)

class ParentOfRoot:
    """
    An instance of this class is used as the parent of the root of a
    filesystem (POSIX) or drive (Win32). This isn't actually a node,
    but it looks enough like one so that we don't have to have
    special purpose code everywhere to deal with dir being None. 
    This class is an instance of the Null object pattern.
    """
    def __init__(self):
        self.abspath = ""
        self.duplicate = 1
        self.path = ""
        self.srcpath = ""
        self.abspath_=''
        self.path_=''
        self.srcpath_=''

    def is_under(self, dir):
        return 0

    def up(self):
        return None

if os.path.normcase("TeSt") == os.path.normpath("TeSt"):
    def _my_normcase(x):
        return x
else:
    def _my_normcase(x):
        return string.upper(x)

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

    def set_toplevel_dir(self, path):
        assert not self.Top, "You can only set the top-level path on an FS object that has not had its File, Dir, or Entry methods called yet."
        self.pathTop = path
        
    def __setTopLevelDir(self):
        if not self.Top:
            self.Top = self.__doLookup(Dir, os.path.normpath(self.pathTop))
            self.Top.path = '.'
            self.Top.srcpath = '.'
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
                  (node.__class__.__name__, str(node), klass.__name__)
        return node
        
    def __doLookup(self, fsclass, name, directory = None, create = 1):
        """This method differs from the File and Dir factory methods in
        one important way: the meaning of the directory parameter.
        In this method, if directory is None or not supplied, the supplied
	name is expected to be an absolute path.  If you try to look up a
	relative path with directory=None, then an AssertionError will be
	raised."""

        path_comp = string.split(name, os.sep)
        drive, path_first = os.path.splitdrive(path_comp[0])
        if not path_first:
            # Absolute path
            drive_path = _my_normcase(drive)
            try:
                directory = self.Root[drive_path]
            except KeyError:
                if not create:
                    raise UserError
                dir = Dir(drive, ParentOfRoot())
                dir.path = dir.path + os.sep
                dir.abspath = dir.abspath + os.sep
                dir.srcpath = dir.srcpath + os.sep
                self.Root[drive_path] = dir
                directory = dir
            path_comp = path_comp[1:]
        else:
            path_comp = [ path_first, ] + path_comp[1:]
        # Lookup the directory
        for path_name in path_comp[:-1]:
            path_norm = _my_normcase(path_name)
            try:
                directory = self.__checkClass(directory.entries[path_norm],
                                              Dir)
            except KeyError:
                if not create:
                    raise UserError
                dir_temp = Dir(path_name, directory)
                directory.entries[path_norm] = dir_temp
                directory.add_wkid(dir_temp)
                directory = dir_temp
        file_name = _my_normcase(path_comp[-1])
        try:
            ret = self.__checkClass(directory.entries[file_name], fsclass)
        except KeyError:
            if not create:
                raise UserError
            ret = fsclass(path_comp[-1], directory)
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
        if name[0] == '#':
            directory = self.Top
            name = os.path.join('./', name[1:])
        elif not directory:
            directory = self._cwd
        return (os.path.normpath(name), directory)

    def chdir(self, dir):
        """Change the current working directory for lookups.
        """
        self.__setTopLevelDir()
        if not dir is None:
            self._cwd = dir

    def Entry(self, name, directory = None, create = 1):
        """Lookup or create a generic Entry node with the specified name.
        If the name is a relative path (begins with ./, ../, or a file
        name), then it is looked up relative to the supplied directory
        node, or to the top level directory of the FS (supplied at
        construction time) if no directory is supplied.
        """
        name, directory = self.__transformPath(name, directory)
        return self.__doLookup(Entry, name, directory, create)
    
    def File(self, name, directory = None, create = 1):
        """Lookup or create a File node with the specified name.  If
        the name is a relative path (begins with ./, ../, or a file name),
        then it is looked up relative to the supplied directory node,
        or to the top level directory of the FS (supplied at construction
        time) if no directory is supplied.

        This method will raise TypeError if a directory is found at the
        specified path.
        """
        name, directory = self.__transformPath(name, directory)
        return self.__doLookup(File, name, directory, create)

    def Dir(self, name, directory = None, create = 1):
        """Lookup or create a Dir node with the specified name.  If
        the name is a relative path (begins with ./, ../, or a file name),
        then it is looked up relative to the supplied directory node,
        or to the top level directory of the FS (supplied at construction
        time) if no directory is supplied.

        This method will raise TypeError if a normal file is found at the
        specified path.
        """
        name, directory = self.__transformPath(name, directory)
        return self.__doLookup(Dir, name, directory, create)

    def BuildDir(self, build_dir, src_dir, duplicate=1):
        """Link the supplied build directory to the source directory
        for purposes of building files."""
        self.__setTopLevelDir()
        if not isinstance(src_dir, SCons.Node.Node):
            src_dir = self.Dir(src_dir)
        if not isinstance(build_dir, SCons.Node.Node):
            build_dir = self.Dir(build_dir)
        build_dir.duplicate = duplicate
        if not src_dir.is_under(self.Top) or not build_dir.is_under(self.Top):
            raise UserError, "Both source and build directories must be under top of build tree."
        if src_dir.is_under(build_dir):
            raise UserError, "Source directory cannot be under build directory."
        build_dir.link(src_dir, duplicate)

class Entry(SCons.Node.Node):
    """A generic class for file system entries.  This class if for
    when we don't know yet whether the entry being looked up is a file
    or a directory.  Instances of this class can morph into either
    Dir or File objects by a later, more precise lookup.

    Note: this class does not define __cmp__ and __hash__ for efficiency
    reasons.  SCons does a lot of comparing of Entry objects, and so that
    operation must be as fast as possible, which means we want to use
    Python's built-in object identity comparison.
    """

    def __init__(self, name, directory):
	"""Initialize a generic file system Entry.
	
	Call the superclass initialization, take care of setting up
	our relative and absolute paths, identify our parent
	directory, and indicate that this node should use
	signatures."""
        SCons.Node.Node.__init__(self)

        self.name = name

        assert directory, "A directory must be provided"

        self.duplicate = directory.duplicate
        self.abspath = directory.abspath_ + name
        if str(directory.path) == '.':
            self.path = name
        else:
            self.path = directory.path_ + name

        self.path_ = self.path
        self.abspath_ = self.abspath
        self.dir = directory
	self.use_signature = 1
        self.__doSrcpath(self.duplicate)
        self.srcpath_ = self.srcpath

    def get_dir(self):
        return self.dir

    def adjust_srcpath(self, duplicate):
        self.__doSrcpath(duplicate)
        
    def __doSrcpath(self, duplicate):
        self.duplicate = duplicate
        if str(self.dir.srcpath) == '.':
            self.srcpath = self.name
        else:
            self.srcpath = self.dir.srcpath_ + self.name

    def __str__(self):
	"""A FS node's string representation is its path name."""
        if self.duplicate or self.builder:
            return self.path
        else:
            return self.srcpath

    def exists(self):
        return os.path.exists(str(self))

    def cached_exists(self):
        try:
            return self.exists_flag
        except AttributeError:
            self.exists_flag = self.exists()
            return self.exists_flag

    def current(self):
        """If the underlying path doesn't exist, we know the node is
        not current without even checking the signature, so return 0.
        Otherwise, return None to indicate that signature calculation
        should proceed as normal to find out if the node is current."""
        if not self.exists():
            return 0
        return None

    def is_under(self, dir):
        if self is dir:
            return 1
        else:
            return self.dir.is_under(dir)



# XXX TODO?
# Annotate with the creator
# is_under
# rel_path
# srcpath / srcdir
# link / is_linked
# linked_targets
# is_accessible

class Dir(Entry):
    """A class for directories in a file system.
    """

    def __init__(self, name, directory):
        Entry.__init__(self, name, directory)
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
        self.srcpath_ = self.srcpath + os.sep

        self.entries = {}
        self.entries['.'] = self
        self.entries['..'] = self.dir
        self.use_signature = None
        self.builder = 1
        self._sconsign = None

    def __doReparent(self, duplicate):
        for ent in self.entries.values():
            if not ent is self and not ent is self.dir:
                ent.adjust_srcpath(duplicate)

    def adjust_srcpath(self, duplicate):
        Entry.adjust_srcpath(self, duplicate)
        self.srcpath_ = self.srcpath + os.sep
        self.__doReparent(duplicate)
                
    def link(self, srcdir, duplicate):
        """Set this directory as the build directory for the
        supplied source directory."""
        self.srcpath = srcdir.path
        self.srcpath_ = srcdir.path_
        self.__doReparent(duplicate)

    def up(self):
        return self.entries['..']

    def root(self):
        if not self.entries['..']:
            return self
        else:
            return self.entries['..'].root()

    def children(self):
	#XXX --random:  randomize "dependencies?"
	keys = filter(lambda k: k != '.' and k != '..', self.entries.keys())
	kids = map(lambda x, s=self: s.entries[x], keys)
	def c(one, two):
            if one.abspath < two.abspath:
               return -1
            if one.abspath > two.abspath:
               return 1
            return 0
	kids.sort(c)
	return kids

    def build(self):
        """A null "builder" for directories."""
        pass

    def set_bsig(self, bsig):
        """A directory has no signature."""
        pass

    def set_csig(self, csig):
        """A directory has no signature."""
        pass

    def current(self):
        """If all of our children were up-to-date, then this
        directory was up-to-date, too."""
        state = 0
        for kid in self.children():
            s = kid.get_state()
            if s and (not state or s > state):
                state = s
        import SCons.Node
        if state == 0 or state == SCons.Node.up_to_date:
            return 1
        else:
            return 0

    def sconsign(self):
        """Return the .sconsign file info for this directory,
        creating it first if necessary."""
        if not self._sconsign:
            #XXX Rework this to get rid of the hard-coding
            import SCons.Sig
            import SCons.Sig.MD5
            self._sconsign = SCons.Sig.SConsignFile(self, SCons.Sig.MD5)
        return self._sconsign



# XXX TODO?
# rfile
# precious
# no_rfile
# rpath
# rsrcpath
# source_exists
# derived_exists
# is_on_rpath
# local
# base_suf
# suffix
# addsuffix
# accessible
# ignore
# build
# bind
# is_under
# relpath

class File(Entry):
    """A class for files in a file system.
    """
    def __init__(self, name, directory = None):
        Entry.__init__(self, name, directory)
        self._morph()
        
    def _morph(self):
        """Turn a file system node into a File object."""
        self.created = 0

    def root(self):
        return self.dir.root()

    def get_contents(self):
        if not self.exists():
            return ''
        return open(str(self), "rb").read()

    def get_timestamp(self):
        if self.exists():
            return os.path.getmtime(str(self))
        else:
            return 0

    def set_bsig(self, bsig):
        """Set the build signature for this file, updating the
        .sconsign entry."""
        Entry.set_bsig(self, bsig)
        self.set_sconsign()

    def set_csig(self, csig):
        """Set the content signature for this file, updating the
        .sconsign entry."""
        Entry.set_csig(self, csig)
        self.set_sconsign()

    def set_sconsign(self):
        """Update a file's .sconsign entry with its current info."""
        self.dir.sconsign().set(self.name, self.get_timestamp(),
                                self.get_bsig(), self.get_csig())

    def get_prevsiginfo(self):
        """Fetch the previous signature information from the
        .sconsign entry."""
        return self.dir.sconsign().get(self.name)

    def scan(self):
        if self.env:
            for scn in self.scanners:
                if not self.scanned.has_key(scn):
                    deps = scn.scan(self, self.env)
                    self.add_implicit(deps,scn)
                    self.scanned[scn] = 1
                    
    def exists(self):
        if self.duplicate and not self.created:
            self.created = 1
            if self.srcpath != self.path and \
               os.path.exists(self.srcpath):
                if os.path.exists(self.path):
                    os.unlink(self.path)
                self.__createDir()
                file_link(self.srcpath, self.path)
        return Entry.exists(self)

    def __createDir(self):
        # ensure that the directories for this node are
        # created.

        listDirs = []
        parent=self.dir
        while parent:
            if parent.cached_exists():
                break
            listDirs.append(parent)
            parent = parent.up()
        listDirs.reverse()
        for dirnode in listDirs:
            try:
                os.mkdir(dirnode.abspath)
                dirnode.exists_flag = 1
            except OSError:
                pass

    def build(self):
        self.__createDir()
        Entry.build(self)
        self.exists_flag = self.exists()

default_fs = FS()

