"""SCons.SConsign

Writing and reading information to the .sconsign file or files.

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

import cPickle
import os
import os.path
import time

import SCons.Sig
import SCons.Node
import SCons.Warnings

#XXX Get rid of the global array so this becomes re-entrant.
sig_files = []

database = None

def write():
    global sig_files
    for sig_file in sig_files:
        sig_file.write()


class Entry:

    """Objects of this type are pickled to the .sconsign file, so it
    should only contain simple builtin Python datatypes and no methods.

    This class is used to store cache information about nodes between
    scons runs for efficiency, and to store the build signature for
    nodes so that scons can determine if they are out of date. """

    # setup the default value for various attributes:
    # (We make the class variables so the default values won't get pickled
    # with the instances, which would waste a lot of space)
    timestamp = None
    bsig = None
    csig = None
    implicit = None
    bkids = []
    bkidsigs = []
    bact = None
    bactsig = None

class Base:
    """
    This is the controlling class for the signatures for the collection of
    entries associated with a specific directory.  The actual directory
    association will be maintained by a subclass that is specific to
    the underlying storage method.  This class provides a common set of
    methods for fetching and storing the individual bits of information
    that make up signature entry.
    """
    def __init__(self, module=None):
        """
        module - the signature module being used
        """

        self.module = module or SCons.Sig.default_calc.module
        self.entries = {}
        self.dirty = 0

    # A null .sconsign entry.  We define this here so that it will
    # be easy to keep this in sync if/whenever we change the type of
    # information returned by the get() method, below.
    null_siginfo = (None, None, None)

    def get(self, filename):
        """
        Get the .sconsign entry for a file

        filename - the filename whose signature will be returned
        returns - (timestamp, bsig, csig)
        """
        entry = self.get_entry(filename)
        return (entry.timestamp, entry.bsig, entry.csig)

    def get_entry(self, filename):
        """
        Create an entry for the filename and return it, or if one already exists,
        then return it.
        """
        try:
            return self.entries[filename]
        except (KeyError, AttributeError):
            return Entry()

    def set_entry(self, filename, entry):
        """
        Set the entry.
        """
        self.entries[filename] = entry
        self.dirty = 1

    def set_csig(self, filename, csig):
        """
        Set the csig .sconsign entry for a file

        filename - the filename whose signature will be set
        csig - the file's content signature
        """

        entry = self.get_entry(filename)
        entry.csig = csig
        self.set_entry(filename, entry)

    def set_binfo(self, filename, bsig, bkids, bkidsigs, bact, bactsig):
        """
        Set the build info .sconsign entry for a file

        filename - the filename whose signature will be set
        bsig - the file's built signature
        """

        entry = self.get_entry(filename)
        entry.bsig = bsig
        entry.bkids = bkids
        entry.bkidsigs = bkidsigs
        entry.bact = bact
        entry.bactsig = bactsig
        self.set_entry(filename, entry)

    def set_timestamp(self, filename, timestamp):
        """
        Set the timestamp .sconsign entry for a file

        filename - the filename whose signature will be set
        timestamp - the file's timestamp
        """

        entry = self.get_entry(filename)
        entry.timestamp = timestamp
        self.set_entry(filename, entry)

    def get_implicit(self, filename):
        """Fetch the cached implicit dependencies for 'filename'"""
        entry = self.get_entry(filename)
        return entry.implicit

    def set_implicit(self, filename, implicit):
        """Cache the implicit dependencies for 'filename'."""
        entry = self.get_entry(filename)
        if not SCons.Util.is_List(implicit):
            implicit = [implicit]
        implicit = map(str, implicit)
        entry.implicit = implicit
        self.set_entry(filename, entry)

    def get_binfo(self, filename):
        """Fetch the cached implicit dependencies for 'filename'"""
        entry = self.get_entry(filename)
        return entry.bsig, entry.bkids, entry.bkidsigs, entry.bact, entry.bactsig

class DB(Base):
    """
    A Base subclass that reads and writes signature information
    from a global .sconsign.dbm file.
    """
    def __init__(self, dir, module=None):
        Base.__init__(self, module)

        self.dir = dir

        try:
            global database
            rawentries = database[self.dir.path]
        except KeyError:
            pass
        else:
            try:
                self.entries = cPickle.loads(rawentries)
                if type(self.entries) is not type({}):
                    self.entries = {}
                    raise TypeError
            except KeyboardInterrupt:
                raise
            except:
                SCons.Warnings.warn(SCons.Warnings.CorruptSConsignWarning,
                                    "Ignoring corrupt sconsign entry : %s"%self.dir.path)

        global sig_files
        sig_files.append(self)

    def write(self):
        if self.dirty:
            global database
            database[self.dir.path] = cPickle.dumps(self.entries, 1)
            try:
                database.sync()
            except AttributeError:
                # Not all anydbm modules have sync() methods.
                pass

class Dir(Base):
    def __init__(self, fp=None, module=None):
        """
        fp - file pointer to read entries from
        module - the signature module being used
        """
        Base.__init__(self, module)

        if fp:
            self.entries = cPickle.load(fp)
            if type(self.entries) is not type({}):
                self.entries = {}
                raise TypeError

class DirFile(Dir):
    """
    Encapsulates reading and writing a per-directory .sconsign file.
    """
    def __init__(self, dir, module=None):
        """
        dir - the directory for the file
        module - the signature module being used
        """

        self.dir = dir
        self.sconsign = os.path.join(dir.path, '.sconsign')

        try:
            fp = open(self.sconsign, 'rb')
        except IOError:
            fp = None

        try:
            Dir.__init__(self, fp, module)
        except KeyboardInterrupt:
            raise
        except:
            SCons.Warnings.warn(SCons.Warnings.CorruptSConsignWarning,
                                "Ignoring corrupt .sconsign file: %s"%self.sconsign)

        global sig_files
        sig_files.append(self)

    def write(self):
        """
        Write the .sconsign file to disk.

        Try to write to a temporary file first, and rename it if we
        succeed.  If we can't write to the temporary file, it's
        probably because the directory isn't writable (and if so,
        how did we build anything in this directory, anyway?), so
        try to write directly to the .sconsign file as a backup.
        If we can't rename, try to copy the temporary contents back
        to the .sconsign file.  Either way, always try to remove
        the temporary file at the end.
        """
        if self.dirty:
            temp = os.path.join(self.dir.path, '.scons%d' % os.getpid())
            try:
                file = open(temp, 'wb')
                fname = temp
            except IOError:
                try:
                    file = open(self.sconsign, 'wb')
                    fname = self.sconsign
                except IOError:
                    return
            cPickle.dump(self.entries, file, 1)
            file.close()
            if fname != self.sconsign:
                try:
                    mode = os.stat(self.sconsign)[0]
                    os.chmod(self.sconsign, 0666)
                    os.unlink(self.sconsign)
                except OSError:
                    pass
                try:
                    os.rename(fname, self.sconsign)
                except OSError:
                    open(self.sconsign, 'wb').write(open(fname, 'rb').read())
                    os.chmod(self.sconsign, mode)
            try:
                os.unlink(temp)
            except OSError:
                pass

ForDirectory = DirFile

def File(name, dbm_module=None):
    """
    Arrange for all signatures to be stored in a global .sconsign.dbm
    file.
    """
    global database
    if database is None:
        if dbm_module is None:
            import SCons.dblite
            dbm_module = SCons.dblite
        database = dbm_module.open(name, "c")

    global ForDirectory
    ForDirectory = DB
