"""SCons.Scanner.C

This module implements the depenency scanner for C/C++ code. 

"""

#
# Copyright (c) 2001, 2002 Steven Knight
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


import copy
import os.path
import re

import SCons.Node
import SCons.Node.FS
import SCons.Scanner
import SCons.Util

include_re = re.compile('^[ \t]*#[ \t]*include[ \t]+(<|")([\\w./\\\\]+)(>|")', re.M)

include_cache = {}

def CScan(fs = SCons.Node.FS.default_fs):
    "Return a prototype Scanner instance for scanning C/C++ source files"
    cs = CScanner(scan, "CScan", [fs, ()],
                  [".c", ".C", ".cxx", ".cpp", ".c++", ".cc",
                   ".h", ".H", ".hxx", ".hpp", ".hh"])
    cs.fs = fs
    return cs

class CScanner(SCons.Scanner.Recursive):
    def __init__(self, *args, **kw):
        apply(SCons.Scanner.Recursive.__init__, (self,) + args, kw)
        self.hash = None
        self.pathscanners = {}

    def instance(self, env):
        """
        Return a unique instance of a C scanner object for a
        given environment.
        """
        try:
            dirs = tuple(SCons.Node.arg2nodes(env.Dictionary('CPPPATH'),
                                              self.fs.Dir))
        except:
            dirs = ()
        if not self.pathscanners.has_key(dirs):
            clone = copy.copy(self)
            clone.hash = dirs
            clone.argument = [self.fs, dirs]	# XXX reaching into object
            self.pathscanners[dirs] = clone
        return self.pathscanners[dirs]

    def __hash__(self):
        return hash(self.hash)

def scan(node, env, args = [SCons.Node.FS.default_fs, ()]):
    """
    scan(node, Environment) -> [node]

    the C/C++ dependency scanner function

    This function is intentionally simple. There are two rules it
    follows:
    
    1) #include <foo.h> - search for foo.h in CPPPATH followed by the
        directory 'filename' is in
    2) #include \"foo.h\" - search for foo.h in the directory 'filename' is
       in followed by CPPPATH

    These rules approximate the behaviour of most C/C++ compilers.

    This scanner also ignores #ifdef and other preprocessor conditionals, so
    it may find more depencies than there really are, but it never misses
    dependencies.
    """

    fs, cpppath = args
    nodes = []

    try:
        nodes = node.found_includes[cpppath]
    except KeyError:
        if node.exists():

            # cache the includes list in node so we only scan it once:
            if hasattr(node, 'includes'):
                includes = node.includes
            else:
                includes = include_re.findall(node.get_contents())
                node.includes = includes

            source_dir = node.get_dir()
            
            for include in includes:
                if include[0] == '"':
                    n = SCons.Node.FS.find_file(include[1],
                                                (source_dir,) + cpppath,
                                                fs.File)
                else:
                    n = SCons.Node.FS.find_file(include[1],
                                                cpppath + (source_dir,),
                                                fs.File)

                if not n is None:
                    nodes.append(n)
        node.found_includes[cpppath] = nodes

    # Schwartzian transform from the Python FAQ Wizard
    def st(List, Metric):
        def pairing(element, M = Metric):
            return (M(element), element)
        def stripit(pair):
            return pair[1]
        paired = map(pairing, List)
        paired.sort()
        return map(stripit, paired)

    def normalize(node):
        return str(node)

    return st(nodes, normalize)


