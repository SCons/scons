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
        bkids = map(str, children)

        # double check bsig, because the call to children() above may
        # have set it:
        bsig = cache.get_bsig()
        if bsig is not None:
            return bsig

        sigs = map(lambda n, c=self: n.calc_signature(c), children)

        if node.has_builder():
            executor = node.get_executor()
            bact = str(executor)
            bactsig = self.module.signature(executor)
            sigs.append(bactsig)
        else:
            bact = ""
            bactsig = ""

        bsig = self.module.collect(filter(None, sigs))

        cache.set_binfo(bsig, bkids, sigs, bact, bactsig)

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
            oldtime, oldbsig, oldcsig = node.get_prevsiginfo()
        else:
            import SCons.SConsign
            oldtime, oldbsig, oldcsig = SCons.SConsign.Base.null_siginfo

        mtime = node.get_timestamp()

        if (oldtime and oldcsig and oldtime == mtime):
            # use the signature stored in the .sconsign file
            csig = oldcsig
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

        if node.always_build:
            return 0
        
        oldtime, oldbsig, oldcsig = node.get_prevsiginfo()

        if type(newsig) != type(oldbsig):
            return 0

        if not node.has_builder() and node.get_timestamp() == oldtime:
            return 1

        return self.module.current(newsig, oldbsig)


default_calc = Calculator()
