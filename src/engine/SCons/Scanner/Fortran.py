"""SCons.Scanner.Fortran

This module implements the dependency scanner for Fortran code. 

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
import SCons.Warnings

include_re = re.compile("INCLUDE[ \t]+'([\\w./\\\\]+)'", re.M)

def FortranScan(fs = SCons.Node.FS.default_fs):
    """Return a prototype Scanner instance for scanning source files
    for Fortran INCLUDE statements"""
    scanner = SCons.Scanner.Recursive(scan, "FortranScan", fs,
                                      [".f", ".F", ".for", ".FOR"],
                                      path_function = path)
    return scanner

def path(env, dir, fs = SCons.Node.FS.default_fs):
    try:
        f77path = env['F77PATH']
    except KeyError:
        return ()
    return tuple(fs.Rsearchall(SCons.Util.mapPaths(f77path, dir, env),
                               clazz = SCons.Node.FS.Dir,
                               must_exist = 0))

def scan(node, env, f77path = (), fs = SCons.Node.FS.default_fs):
    """
    scan(node, Environment) -> [node]

    the Fortran dependency scanner function
    """

    node = node.rfile()

    # This function caches the following information:
    # node.includes - the result of include_re.findall()

    if not node.exists():
        return []

    # cache the includes list in node so we only scan it once:
    if node.includes != None:
        includes = node.includes
    else:
        includes = include_re.findall(node.get_contents())
        node.includes = includes

    source_dir = node.get_dir()
    
    nodes = []
    for include in includes:
        n = SCons.Node.FS.find_file(include,
                                    (source_dir,) + f77path,
                                    fs.File)
        if not n is None:
            nodes.append(n)
        else:
            SCons.Warnings.warn(SCons.Warnings.DependencyWarning,
                                "No dependency generated for file: %s (included from: %s) -- file not found" % (include, node))

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
        # We don't want the order of includes to be 
        # modified by case changes on case insensitive OSes, so
        # normalize the case of the filename here:
        # (see test/win32pathmadness.py for a test of this)
        return SCons.Node.FS._my_normcase(str(node))

    return st(nodes, normalize)
