"""scons.Node.FS

File system nodes.

This initializes a "default_fs" Node with an FS at the current directory
for its own purposes, and for use by scripts or modules looking for the
canonical default.

"""

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import os
import os.path
from SCons.Node import Node
from UserDict import UserDict
import sys

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

    if not hasattr(UserDict, 'setdefault'):
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
            path = os.getcwd()
        self.Root = PathDict()
        self.Top = self.__doLookup(Dir, path)
        self.Top.path = '.'

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
            if sys.platform is 'win32' and not drive:
                if not directory:
                    raise OSError, 'No drive letter supplied for absolute path.'
                return directory.root()
            return self.Root.setdefault(drive, Dir(tail))
        if head:
            # Recursively look up our parent directories.
            directory = self.__doLookup(Dir, head, directory)
        else:
            # This path looks like a relative path.  No leading slash or drive
	    # letter.  Therefore, we will look up this path relative to the
	    # supplied top-level directory.
	    assert directory, "Tried to lookup a node by relative path with no top-level directory supplied."
        ret = directory.entries.setdefault(tail, fsclass(tail, directory))
        if not isinstance(ret, fsclass):
            raise TypeError, ret
        return ret

    def __transformPath(self, name, directory):
        """Take care of setting up the correct top-level directory,
        usually in preparation for a call to doLookup().

        If the path name is prepended with a '#', then it is unconditionally
        interpreted as replative to the top-level directory of this FS.

        If directory is None, and name is a relative path,
        then the same applies.
        """
        if name[0] == '#':
            directory = self.Top
            name = os.path.join(os.path.normpath('./'), name[1:])
        elif not directory:
            directory = self.Top
        return (name, directory)
    
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

    

# XXX TODO?
# Annotate with the creator
# is_under
# rel_path
# srcpath / srcdir
# link / is_linked
# linked_targets
# is_accessible

class Dir(Node):
    """A class for directories in a file system.
    """

    def __init__(self, name, directory = None):
        Node.__init__(self)

        self.entries = PathDict()
        self.entries['.'] = self

        if directory:
            self.entries['..'] = directory
            self.abspath = os.path.join(directory.abspath, name, '')
            if str(directory.path) == '.':
                self.path = os.path.join(name, '')
            else:
                self.path = os.path.join(directory.path, name, '')
        else:
            self.abspath = self.path = name
            self.entries['..'] = None

    def __str__(self):
	return self.path

    def up(self):
        return self.entries['..']

    def root(self):
        if not self.entries['..']:
            return self
        else:
            return self.entries['..'].root()

    def children(self):
	return map(lambda x, s=self: s.entries[x],
		   filter(lambda k: k != '.' and k != '..',
			  self.entries.keys()))


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

class File(Node):
    """A class for files in a file system.
    """

    def __init__(self, name, directory):
        Node.__init__(self)

        self.abspath = os.path.join(directory.abspath, name)
        if str(directory.path) == '.':
            self.path = name
        else:
            self.path = os.path.join(directory.path, name)
        self.parent = directory

    def __str__(self):
	return self.path

    def root(self):
        return self.parent.root()

    def get_contents(self):
        return open(self.path, "r").read()

    def get_timestamp(self):
        return os.path.getmtime(self.path)

    def exists(self):
        return os.path.exists(self.path)


default_fs = FS()
