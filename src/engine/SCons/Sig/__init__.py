"""SCons.Sig

The Signature package for the scons software construction utility.

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

import os.path
import string


#XXX Get rid of the global array so this becomes re-entrant.
sig_files = []

def write():
    global sig_files
    for sig_file in sig_files:
        sig_file.write()

class SConsignFile:
    """
    Encapsulates reading and writing a .sconsign file.
    """

    def __init__(self, dir, module):
        """
        dir - the directory for the file
        module - the signature module being used
        """
        
        self.path = os.path.join(dir, '.sconsign')
        self.entries = {}
                    
        try:
            file = open(self.path, 'rt')
        except:
            pass
        else:
            for line in file.readlines():
                filename, rest = map(string.strip, string.split(line, ":"))
                time, signature = map(string.strip, string.split(rest, " "))
                self.entries[filename] = (int(time), module.from_string(signature))

        global sig_files
        sig_files.append(self)

    def get(self, filename):
        """
        Get the signature for a file

        filename - the filename whose signature will be returned
        returns - (timestamp, signature)
        """
        
        try:
            return self.entries[filename]
        except KeyError:
            return (0, None)

    def set(self, filename, timestamp, signature, module):
        """
        Set the signature for a file

        filename - the filename whose signature will be set
        timestamp - the timestamp
        signature - the signature
        module - the signature module being used
        """
        self.entries[filename] = (timestamp, module.to_string(signature))

    def write(self):
        """
        Write the .sconsign file to disk.
        """
        
        file = open(self.path, 'wt')
        for item in self.entries.items():
            file.write("%s: %d %s\n" % (item[0], item[1][0], item[1][1]))


class Calculator:
    """
    Encapsulates signature calculations and .sconsign file generating
    for the build engine.
    """

    def __init__(self, module):
        """
        Initialize the calculator.

        module - the signature module to use for signature calculations
        """
        self.module = module

    
    def collect(self, node, signatures):
        """
        Collect the signatures of the node's sources.

        node - the node whose sources will be collected
        signatures - the dictionary that the signatures will be
        gathered into.
        """
        for source_node in node.children():
            if not signatures.has_key(source_node):
                signature = self.get_signature(source_node)
                signatures[source_node] = signature
                self.collect(source_node, signatures)

    def get_signature(self, node):
        """
        Get the signature for a node.

        node - the node
        returns - the signature or None if the signature could not
        be computed.

        This method does not store the signature in the node and
        in the .sconsign file.
        """

        if not node.use_signature:
            # This node type doesn't use a signature (e.g. a
            # directory) so bail right away.
            return None
        elif node.has_signature():
            sig = node.get_signature()
        elif node.builder:
            signatures = {}
            self.collect(node, signatures)
            signatures = filter(lambda x: not x is None, signatures.values())
            sig = self.module.collect(signatures)
        else:
            if not node.exists():
                return None
            
            # XXX handle nodes that are not under the source root
            sig = self.module.signature(node)

        return sig

    def current(self, node, newsig):
        """
        Check if a node is up to date.

        node - the node whose signature will be checked

        returns - 0 if the signature has changed since the last invocation,
        and 1 if it hasn't
        """

        c = node.current()
        if not c is None:
            # The node itself has told us whether or not it's
            # current without checking the signature.  The
            # canonical uses here are a "0" return for a file
            # that doesn't exist, or a directory.
            return c

        oldtime, oldsig = node.get_oldentry()

        newtime = node.get_timestamp()

        if not node.builder and newtime == oldtime:
            newsig = oldsig
        
        return self.module.current(newsig, oldsig)
