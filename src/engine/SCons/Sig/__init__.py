"""SCons.Sig

The Signature package for the scons software construction utility.

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

import SCons.Node
import SCons.Warnings

try:
    import MD5
    default_module = MD5
except ImportError:
    import TimeStamp
    default_module = TimeStamp

default_max_drift = 2*24*60*60

#XXX Get rid of the global array so this becomes re-entrant.
sig_files = []

# 1 means use build signature for derived source files
# 0 means use content signature for derived source files
build_signature = 1

def write():
    global sig_files
    for sig_file in sig_files:
        sig_file.write()


class SConsignEntry:

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

class SConsignFile:
    """
    Encapsulates reading and writing a .sconsign file.
    """

    def __init__(self, dir, module=None):
        """
        dir - the directory for the file
        module - the signature module being used
        """

        self.dir = dir

        if module is None:
            self.module = default_calc.module
        else:
            self.module = module
        self.sconsign = os.path.join(dir.path, '.sconsign')
        self.entries = {}
        self.dirty = 0

        try:
            file = open(self.sconsign, 'rb')
        except:
            pass
        else:
            try:
                self.entries = cPickle.load(file)
                if type(self.entries) is not type({}):
                    self.entries = {}
                    raise TypeError
            except:
                SCons.Warnings.warn(SCons.Warnings.CorruptSConsignWarning,
                                    "Ignoring corrupt .sconsign file: %s"%self.sconsign)
        global sig_files
        sig_files.append(self)

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
        except:
            return SConsignEntry()

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

    def set_bsig(self, filename, bsig):
        """
        Set the csig .sconsign entry for a file

        filename - the filename whose signature will be set
        bsig - the file's built signature
        """

        entry = self.get_entry(filename)
        entry.bsig = bsig
        self.set_entry(filename, entry)

    def set_timestamp(self, filename, timestamp):
        """
        Set the csig .sconsign entry for a file

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
        if SCons.Util.is_String(implicit):
            implicit = [implicit]
        implicit = map(str, implicit)
        entry.implicit = implicit
        self.set_entry(filename, entry)

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
            except:
                try:
                    file = open(self.sconsign, 'wb')
                    fname = self.sconsign
                except:
                    return
            cPickle.dump(self.entries, file, 1)
            file.close()
            if fname != self.sconsign:
                try:
                    mode = os.stat(self.sconsign)[0]
                    os.chmod(self.sconsign, 0666)
                    os.unlink(self.sconsign)
                except:
                    pass
                try:
                    os.rename(fname, self.sconsign)
                except:
                    open(self.sconsign, 'wb').write(open(fname, 'rb').read())
                    os.chmod(self.sconsign, mode)
            try:
                os.unlink(temp)
            except:
                pass

class Calculator:
    """
    Encapsulates signature calculations and .sconsign file generating
    for the build engine.
    """

    def __init__(self, module=default_module, max_drift=default_max_drift):
        """
        Initialize the calculator.

        module - the signature module to use for signature calculations
        max_drift - the maximum system clock drift used to determine when to
          cache content signatures. A negative value means to never cache
          content signatures. (defaults to 2 days)
        """
        self.module = module
        self.max_drift = max_drift

    def bsig(self, node, cache=None):
        """
        Generate a node's build signature, the digested signatures
        of its dependency files and build information.

        node - the node whose sources will be collected
        cache - alternate node to use for the signature cache
        returns - the build signature

        This no longer handles the recursive descent of the
        node's children's signatures.  We expect that they're
        already built and updated by someone else, if that's
        what's wanted.
        """

        if cache is None: cache = node

        bsig = cache.get_bsig()
        if bsig is not None:
            return bsig

        children = node.children()

        # double check bsig, because the call to childre() above may
        # have set it:
        bsig = cache.get_bsig()
        if bsig is not None:
            return bsig

        sigs = map(lambda n, c=self: n.calc_signature(c), children)
        if node.has_builder():
            sigs.append(self.module.signature(node.get_executor()))

        bsig = self.module.collect(filter(lambda x: not x is None, sigs))

        cache.set_bsig(bsig)

        # don't store the bsig here, because it isn't accurate until
        # the node is actually built.

        return bsig

    def csig(self, node, cache=None):
        """
        Generate a node's content signature, the digested signature
        of its content.

        node - the node
        cache - alternate node to use for the signature cache
        returns - the content signature
        """

        if cache is None: cache = node

        csig = cache.get_csig()
        if csig is not None:
            return csig
        
        if self.max_drift >= 0:
            info = node.get_prevsiginfo()
        else:
            info = None

        mtime = node.get_timestamp()

        if (info and info[0] and info[2] and info[0] == mtime):
            # use the signature stored in the .sconsign file
            csig = info[2]
            # Set the csig here so it doesn't get recalculated unnecessarily
            # and so it's set when the .sconsign file gets written
            cache.set_csig(csig)
        else:
            csig = self.module.signature(node)
            # Set the csig here so it doesn't get recalculated unnecessarily
            # and so it's set when the .sconsign file gets written
            cache.set_csig(csig)

            if self.max_drift >= 0 and (time.time() - mtime) > self.max_drift:
                node.store_csig()
                node.store_timestamp()

        return csig

    def current(self, node, newsig):
        """
        Check if a signature is up to date with respect to a node.

        node - the node whose signature will be checked
        newsig - the (presumably current) signature of the file

        returns - 1 if the file is current with the specified signature,
        0 if it isn't
        """
        oldtime, oldbsig, oldcsig = node.get_prevsiginfo()

        if not node.has_builder() and node.get_timestamp() == oldtime:
            return 1

        return self.module.current(newsig, oldbsig)


default_calc = Calculator()
