"""SCons.Node.FS

File system nodes.

"""

__revision__ = "Node/FS.py __REVISION__ __DATE__ __DEVELOPER__"



import os
import os.path
import SCons.Node



Top = None
Root = {}



def init(path = None):
    """Initialize the Node.FS subsystem.

    The supplied path is the top of the source tree, where we
    expect to find the top-level build file.  If no path is
    supplied, the current directory is the default.
    """
    global Top
    if path == None:
	path = os.getcwd()
    Top = lookup(Dir, path, directory = None)
    Top.path = '.'

def lookup(fsclass, name, directory = Top):
    """Look up a file system node for a path name.  If the path
    name is relative, it will be looked up relative to the
    specified directory node, or to the top-level directory
    if no node was specified.  An initial '#' specifies that
    the name will be looked up relative to the top-level directory,
    regardless of the specified directory argument.  Returns the
    existing or newly-created node for the specified path name.
    The node returned will be of the specified fsclass (Dir or
    File).
    """
    global Top
    head, tail = os.path.split(name)
    if not tail:
	drive, path = os.path.splitdrive(head)
	if not Root.has_key(drive):
	    Root[drive] = Dir(head, None)
	    Root[drive].abspath = head
	    Root[drive].path = head
	return Root[drive]
    if tail[0] == '#':
	directory = Top
	tail = tail[1:]
    elif directory is None:
	directory = Top
    if head:
	directory = lookup(Dir, head, directory)
    try:
	self = directory.entries[tail]
    except AttributeError:
	# There was no "entries" attribute on the directory,
	# which essentially implies that it was a file.
	# Return it as a more descriptive exception.
	raise TypeError, directory
    except KeyError:
	# There was to entry for "tail," so create the new
	# node and link it in to the existing structure.
	self = fsclass(tail, directory)
	self.name = tail
	if self.path[0:2] == "./":
	    self.path = self.path[2:]
	directory.entries[tail] = self
    except:
	raise
    if self.__class__.__name__ != fsclass.__name__:
	# Here, we found an existing node for this path,
	# but it was the wrong type (a File when we were
	# looking for a Dir, or vice versa).
	raise TypeError, self
    return self



# XXX TODO?
# Annotate with the creator
# is_under
# rel_path
# srcpath / srcdir
# link / is_linked
# linked_targets
# is_accessible

class Dir(SCons.Node.Node):
    """A class for directories in a file system.
    """

    def __init__(self, name, directory):
	self.entries = {}
	self.entries['.'] = self
	self.entries['..'] = directory
	if not directory is None:
	    self.abspath = os.path.join(directory.abspath, name, '')
	    self.path = os.path.join(directory.path, name, '')

    def up(self):
	return self.entries['..']


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

class File(SCons.Node.Node):
    """A class for files in a file system.
    """

    def __init__(self, name, directory):
	self.abspath = os.path.join(directory.abspath, name)
	self.path = os.path.join(directory.path, name)
