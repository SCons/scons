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

class PathName:
    """This is a string like object with limited capabilities (i.e.,
    cannot always be used interchangeably with strings).  This class
    is used by PathDict to manage case-insensitive path names.  It preserves
    the case of the string with which it was created, but on OS's with
    case insensitive paths, it will hash equal to any case of the same
    path when placed in a dictionary."""

    try:
        convert_path = unicode
    except NameError:
        convert_path = str

    def __init__(self, path_name=''):
        self.data = PathName.convert_path(path_name)
        self.norm_path = os.path.normcase(self.data)

    def __hash__(self):
        return hash(self.norm_path)
    def __cmp__(self, other):
        return cmp(self.norm_path,
                   os.path.normcase(PathName.convert_path(other)))
    def __rcmp__(self, other):
        return cmp(os.path.normcase(PathName.convert_path(other)),
                   self.norm_path)
    def __str__(self):
        return str(self.data)
    def __repr__(self):
        return repr(self.data)

class PathDict(UserDict):
    """This is a dictionary-like class meant to hold items keyed
    by path name.  The difference between this class and a normal
    dictionary is that string or unicode keys will act differently
    on OS's that have case-insensitive path names.  Specifically
    string or unicode keys of different case will be treated as
    equal on the OS's.

    All keys are implicitly converted to PathName objects before
    insertion into the dictionary."""

    def __init__(self, initdict = {}):
        UserDict.__init__(self, initdict)
        old_dict = self.data
        self.data = {}
        for key, val in old_dict.items():
            self.data[PathName(key)] = val

    def __setitem__(self, key, val):
        self.data[PathName(key)] = val

    def __getitem__(self, key):
        return self.data[PathName(key)]

    def __delitem__(self, key):
        del(self.data[PathName(key)])

    def setdefault(self, key, value):
        try:
            return self.data[PathName(key)]
        except KeyError:
            self.data[PathName(key)] = value
            return value

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
        self.Root = PathDict()
        self.Top = None

    def set_toplevel_dir(self, path):
        assert not self.Top, "You can only set the top-level path on an FS object that has not had its File, Dir, or Entry methods called yet."
        self.pathTop = path
        
    def __setTopLevelDir(self):
        if not self.Top:
            self.Top = self.__doLookup(Dir, self.pathTop)
            self.Top.path = '.'
            self.Top.srcpath = '.'
            self.Top.path_ = os.path.join('.', '')
            self._cwd = self.Top
        
    def __hash__(self):
        self.__setTopLevelDir()
        return hash(self.Top)

    def __cmp__(self, other):
        self.__setTopLevelDir()
        if isinstance(other, FS):
            other.__setTopLevelDir()
	return cmp(self.__dict__, other.__dict__)

    def getcwd(self):
        self.__setTopLevelDir()
	return self._cwd

    def __doLookup(self, fsclass, name, directory=None):
        """This method differs from the File and Dir factory methods in
        one important way: the meaning of the directory parameter.
        In this method, if directory is None or not supplied, the supplied
	name is expected to be an absolute path.  If you try to look up a
	relative path with directory=None, then an AssertionError will be
	raised."""

        head, tail = os.path.split(os.path.normpath(name))
        if not tail:
            # We have reached something that looks like a root
            # of an absolute path.  What we do here is a little
            # weird.  If we are on a UNIX system, everything is
            # well and good, just return the root node.
            #
            # On DOS/Win32 things are strange, since a path
            # starting with a slash is not technically an
            # absolute path, but a path relative to the
            # current drive.  Therefore if we get a path like
            # that, we will return the root Node of the
            # directory parameter.  If the directory parameter is
            # None, raise an exception.

            drive, tail = os.path.splitdrive(head)
            #if sys.platform is 'win32' and not drive:
            #    if not directory:
            #        raise OSError, 'No drive letter supplied for absolute path.'
            #    return directory.root()
            dir = Dir(tail)
            dir.path = drive + dir.path
            dir.path_ = drive + dir.path_
            dir.abspath = drive + dir.abspath
            dir.abspath_ = drive + dir.abspath_
            return self.Root.setdefault(drive, dir)
        if head:
            # Recursively look up our parent directories.
            directory = self.__doLookup(Dir, head, directory)
        else:
            # This path looks like a relative path.  No leading slash or drive
	    # letter.  Therefore, we will look up this path relative to the
	    # supplied top-level directory.
	    assert directory, "Tried to lookup a node by relative path with no top-level directory supplied."
        ret = directory.entries.setdefault(tail, fsclass(tail, directory))
	if fsclass.__name__ == 'Entry':
            # If they were looking up a generic entry, then
	    # whatever came back is all right.
	    return ret
	if ret.__class__.__name__ == 'Entry':
	    # They were looking up a File or Dir but found a
	    # generic entry.  Transform the node.
	    ret.__class__ = fsclass
	    ret._morph()
	    return ret
        if not isinstance(ret, fsclass):
            raise TypeError, "Tried to lookup %s '%s' as a %s." % \
    			(ret.__class__.__name__, str(ret), fsclass.__name__)
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
            name = os.path.join(os.path.normpath('./'), name[1:])
        elif not directory:
            directory = self._cwd
        return (name, directory)

    def chdir(self, dir):
        """Change the current working directory for lookups.
        """
        self.__setTopLevelDir()
        if not dir is None:
            self._cwd = dir

    def Entry(self, name, directory = None):
        """Lookup or create a generic Entry node with the specified name.
        If the name is a relative path (begins with ./, ../, or a file
        name), then it is looked up relative to the supplied directory
        node, or to the top level directory of the FS (supplied at
        construction time) if no directory is supplied.
        """
        name, directory = self.__transformPath(name, directory)
        return self.__doLookup(Entry, name, directory)
    
    def File(self, name, directory = None):
        """Lookup or create a File node with the specified name.  If
        the name is a relative path (begins with ./, ../, or a file name),
        then it is looked up relative to the supplied directory node,
        or to the top level directory of the FS (supplied at construction
        time) if no directory is supplied.

        This method will raise TypeError if a directory is found at the
        specified path.
        """
        name, directory = self.__transformPath(name, directory)
        return self.__doLookup(File, name, directory)

    def Dir(self, name, directory = None):
        """Lookup or create a Dir node with the specified name.  If
        the name is a relative path (begins with ./, ../, or a file name),
        then it is looked up relative to the supplied directory node,
        or to the top level directory of the FS (supplied at construction
        time) if no directory is supplied.

        This method will raise TypeError if a normal file is found at the
        specified path.
        """
        name, directory = self.__transformPath(name, directory)
        return self.__doLookup(Dir, name, directory)

    def BuildDir(self, build_dir, src_dir):
        """Link the supplied build directory to the source directory
        for purposes of building files."""
        self.__setTopLevelDir()
        dirSrc = self.Dir(src_dir)
        dirBuild = self.Dir(build_dir)
        if not dirSrc.is_under(self.Top) or not dirBuild.is_under(self.Top):
            raise UserError, "Both source and build directories must be under top of build tree."
        if dirSrc.is_under(dirBuild):
            raise UserError, "Source directory cannot be under build directory."
        dirBuild.link(dirSrc)
        

class Entry(SCons.Node.Node):
    """A generic class for file system entries.  This class if for
    when we don't know yet whether the entry being looked up is a file
    or a directory.  Instances of this class can morph into either
    Dir or File objects by a later, more precise lookup."""

    def __init__(self, name, directory):
	"""Initialize a generic file system Entry.
	
	Call the superclass initialization, take care of setting up
	our relative and absolute paths, identify our parent
	directory, and indicate that this node should use
	signatures."""
        SCons.Node.Node.__init__(self)

        self.name = name
        if directory:
            self.abspath = os.path.join(directory.abspath, name)
            if str(directory.path) == '.':
                self.path = name
            else:
                self.path = os.path.join(directory.path, name)
        else:
            self.abspath = self.path = name
        self.path_ = self.path
        self.abspath_ = self.abspath
        self.dir = directory
	self.use_signature = 1
        self.__doSrcpath()

    def adjust_srcpath(self):
        self.__doSrcpath()
        
    def __doSrcpath(self):
        if self.dir:
            if str(self.dir.srcpath) == '.':
                self.srcpath = self.name
            else:
                self.srcpath = os.path.join(self.dir.srcpath, self.name)
        else:
            self.srcpath = self.name

    def __str__(self):
	"""A FS node's string representation is its path name."""
	return self.path

    def __cmp__(self, other):
	if type(self) != types.StringType and type(other) != types.StringType:
            try:
                if self.__class__ != other.__class__:
                    return 1
            except:
                return 1
        return cmp(str(self), str(other))

    def __hash__(self):
	return hash(self.abspath_)

    def exists(self):
        return os.path.exists(self.abspath)

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
        if not self.dir:
            return 0
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

    def __init__(self, name, directory = None):
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

        self.path_ = os.path.join(self.path, '')
        self.abspath_ = os.path.join(self.abspath, '')

        self.entries = PathDict()
        self.entries['.'] = self
        if hasattr(self, 'dir'):
            self.entries['..'] = self.dir
	else:
	    self.entries['..'] = None
        self.use_signature = None
        self.builder = 1
        self._sconsign = None

    def __doReparent(self):
        for ent in self.entries.values():
            if not ent is self and not ent is self.dir:
                ent.adjust_srcpath()

    def adjust_srcpath(self):
        Entry.adjust_srcpath(self)
        self.__doReparent()
                
    def link(self, srcdir):
        """Set this directory as the build directory for the
        supplied source directory."""
        self.srcpath = srcdir.path
        self.__doReparent()

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
        if state == SCons.Node.up_to_date:
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
        return open(str(self), "r").read()

    def get_timestamp(self):
        if self.exists():
            return os.path.getmtime(self.path)
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
                    self.add_implicit(scn.scan(self.path, self.env),
                                      scn)
                    self.scanned[scn] = 1
                    
    def exists(self):
        if not self.created:
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

        listPaths = []
        strPath = self.abspath
        while 1:
            strPath, strFile = os.path.split(strPath)
            if os.path.exists(strPath):
                break
            listPaths.append(strPath)
            if not strFile:
                break
        listPaths.reverse()
        for strPath in listPaths:
            try:
                os.mkdir(strPath)
            except OSError:
                pass

    def build(self):
        self.__createDir()
        Entry.build(self)

default_fs = FS()
