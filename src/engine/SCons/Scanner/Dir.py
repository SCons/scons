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

import string

import SCons.Node.FS
import SCons.Scanner

def DirScanner(**kw):
    """Return a prototype Scanner instance for scanning
    directories for on-disk files"""
    def only_dirs(nodes):
        return filter(lambda n: isinstance(n.disambiguate(),
                                SCons.Node.FS.Dir),
                      nodes)
    kw['node_factory'] = SCons.Node.FS.Entry
    kw['recursive'] = only_dirs
    ds = apply(SCons.Scanner.Base, (scan, "DirScanner"), kw)
    return ds

skip_entry = {
   '.' : 1,
   '..' : 1,
   '.sconsign' : 1,
   '.sconsign.dblite' : 1,
}

def scan(node, env, path=()):
    """
    This scanner scans a directory for on-disk files and directories therein.
    """
    try:
        flist = node.fs.listdir(node.abspath)
    except (IOError, OSError):
        return []
    dont_scan = lambda k: not skip_entry.has_key(k)
    flist = filter(dont_scan, flist)
    flist.sort()
    # Add ./ to the beginning of the file name so that if it begins with a
    # '#' we don't look it up relative to the top-level directory.
    return map(lambda f, node=node: node.Entry('./'+f), flist)
