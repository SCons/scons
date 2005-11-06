"""SCons.Scanner.LaTeX

This module implements the dependency scanner for LaTeX code. 

"""

#
# Copyright (c) 2005 The SCons Foundation
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

__revision__ = ""


import SCons.Scanner

def LaTeXScanner(fs = SCons.Node.FS.default_fs):
    """Return a prototype Scanner instance for scanning LaTeX source files"""
    ds = LaTeX(name = "LaTeXScanner",
           suffixes =  '$LATEXSUFFIXES',
           path_variable = 'TEXINPUTS',
           regex = '\\\\(include|input){([^}]*)}',
           recursive = 0)
    return ds

class LaTeX(SCons.Scanner.Classic):
    def find_include(self, include, source_dir, path):
        if callable(path): path=path()
        # find (2nd result reg expr) + extension
        # print 'looking for latex includes: ' + include[1]
        i = SCons.Node.FS.find_file(include[1] + '.tex',
                                    (source_dir,) + path)
        return i, include
