"""SCons.Scanner.LaTeX

This module implements the dependency scanner for LaTeX code.

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

import os.path
import string
import re

import SCons.Scanner

def LaTeXScanner():
    """Return a prototype Scanner instance for scanning LaTeX source files
    when built with latex.
    """
    ds = LaTeX(name = "LaTeXScanner",
               suffixes =  '$LATEXSUFFIXES',
               # in the search order, see below in LaTeX class docstring
               graphics_extensions = ['.eps', '.ps'],
               recursive = 0)
    return ds

def PDFLaTeXScanner():
    """Return a prototype Scanner instance for scanning LaTeX source files
    when built with pdflatex.
    """
    ds = LaTeX(name = "PDFLaTeXScanner",
               suffixes =  '$LATEXSUFFIXES',
               # in the search order, see below in LaTeX class docstring
               graphics_extensions = ['.png', '.pdf', '.jpg', '.tif'],
               recursive = 0)
    return ds

class LaTeX(SCons.Scanner.Base):
    """Class for scanning LaTeX files for included files.

    Unlike most scanners, which use regular expressions that just
    return the included file name, this returns a tuple consisting
    of the keyword for the inclusion ("include", "includegraphics",
    "input", or "bibliography"), and then the file name itself.  
    Based on a quick look at LaTeX documentation, it seems that we 
    should append .tex suffix for the "include" keywords, append .tex if
    there is no extension for the "input" keyword, and need to add .bib
    for the "bibliography" keyword that does not accept extensions by itself.

    Finally, if there is no extension for an "includegraphics" keyword
    latex will append .ps or .eps to find the file, while pdftex may use .pdf,
    .jpg, .tif, .mps, or .png.
    
    The actual subset and search order may be altered by
    DeclareGraphicsExtensions command. This complication is ignored.
    The default order corresponds to experimentation with teTeX
        $ latex --version
        pdfeTeX 3.141592-1.21a-2.2 (Web2C 7.5.4)
        kpathsea version 3.5.4
    The order is:
        ['.eps', '.ps'] for latex
        ['.png', '.pdf', '.jpg', '.tif'].

    Another difference is that the search path is determined by the type
    of the file being searched:
    env['TEXINPUTS'] for "input" and "include" keywords
    env['TEXPICTS'] for "includegraphics" keyword
    env['BIBINPUTS'] for "bibliography" keyword
    env['BSTINPUTS'] for "bibliographystyle" keyword

    FIXME: also look for the class or style in document[class|style]{}
    FIXME: also look for the argument of bibliographystyle{}
    """
    keyword_paths = {'include': 'TEXINPUTS',
                     'input': 'TEXINPUTS',
                     'includegraphics': 'TEXPICTS',
                     'bibliography': 'BIBINPUTS',
                     'bibliographystyle': 'BSTINPUTS',
                     'usepackage': 'TEXINPUTS'}
    env_variables = SCons.Util.unique(keyword_paths.values())

    def __init__(self, name, suffixes, graphics_extensions, *args, **kw):

        regex = '\\\\(include|includegraphics(?:\[[^\]]+\])?|input|bibliography|usepackage){([^}]*)}'
        self.cre = re.compile(regex, re.M)
        self.graphics_extensions = graphics_extensions

        def _scan(node, env, path=(), self=self):
            node = node.rfile()
            if not node.exists():
                return []
            return self.scan(node, path)

        class FindMultiPathDirs:
            """The stock FindPathDirs function has the wrong granularity:
            it is called once per target, while we need the path that depends
            on what kind of included files is being searched. This wrapper
            hides multiple instances of FindPathDirs, one per the LaTeX path
            variable in the environment. When invoked, the function calculates
            and returns all the required paths as a dictionary (converted into
            a tuple to become hashable). Then the scan function converts it
            back and uses a dictionary of tuples rather than a single tuple
            of paths.
            """
            def __init__(self, dictionary):
                self.dictionary = {}
                for k,n in dictionary.items():
                    self.dictionary[k] = SCons.Scanner.FindPathDirs(n)

            def __call__(self, env, dir=None, target=None, source=None,
                                    argument=None):
                di = {}
                for k,c  in self.dictionary.items():
                    di[k] = c(env, dir=None, target=None, source=None,
                                   argument=None)
                # To prevent "dict is not hashable error"
                return tuple(di.items())

        class LaTeXScanCheck:
            """Skip all but LaTeX source files, i.e., do not scan *.eps,
            *.pdf, *.jpg, etc.
            """
            def __init__(self, suffixes):
                self.suffixes = suffixes
            def __call__(self, node, env):
                current = not node.has_builder() or node.is_up_to_date()
                scannable = node.get_suffix() in env.subst(self.suffixes)
                # Returning false means that the file is not scanned.
                return scannable and current

        kw['function'] = _scan
        kw['path_function'] = FindMultiPathDirs(LaTeX.keyword_paths)
        kw['recursive'] = 1
        kw['skeys'] = suffixes
        kw['scan_check'] = LaTeXScanCheck(suffixes)
        kw['name'] = name

        apply(SCons.Scanner.Base.__init__, (self,) + args, kw)

    def _latex_names(self, include):
        filename = include[1]
        if include[0] == 'input':
            base, ext = os.path.splitext( filename )
            if ext == "":
                return [filename + '.tex']
        if (include[0] == 'include'):
            return [filename + '.tex']
        if include[0] == 'bibliography':
            base, ext = os.path.splitext( filename )
            if ext == "":
                return [filename + '.bib']
        if include[0] == 'usepackage':
            base, ext = os.path.splitext( filename )
            if ext == "":
                return [filename + '.sty']
        if include[0] == 'includegraphics':
            base, ext = os.path.splitext( filename )
            if ext == "":
                #FUTURE return [filename + e for e in self.graphics_extensions]
                return map(lambda e, f=filename: f+e, self.graphics_extensions)
        return [filename]

    def sort_key(self, include):
        return SCons.Node.FS._my_normcase(str(include))

    def find_include(self, include, source_dir, path):
        try:
            sub_path = path[include[0]]
        except:
            sub_path = ()
        try_names = self._latex_names(include)
        for n in try_names:
            i = SCons.Node.FS.find_file(n, (source_dir,) + sub_path)
            if i:
                return i, include
        return i, include

    def scan(self, node, path=()):
        # Modify the default scan function to allow for the regular
        # expression to return a comma separated list of file names
        # as can be the case with the bibliography keyword.

        # Cache the includes list in node so we only scan it once:
        path_dict = dict(list(path))
        noopt_cre = re.compile('\[.*$')
        if node.includes != None:
            includes = node.includes
        else:
            includes = self.cre.findall(node.get_contents())
            # 1. Split comma-separated lines, e.g.
            #      ('bibliography', 'phys,comp')
            #    should become two entries
            #      ('bibliography', 'phys')
            #      ('bibliography', 'comp')
            # 2. Remove the options, e.g., such as
            #      ('includegraphics[clip,width=0.7\\linewidth]', 'picture.eps')
            #    should become
            #      ('includegraphics', 'picture.eps')
            split_includes = []
            for include in includes:
                inc_type = noopt_cre.sub('', include[0])
                inc_list = string.split(include[1],',')
                for j in range(len(inc_list)):
                    split_includes.append( (inc_type, inc_list[j]) )
            #
            includes = split_includes
            node.includes = includes

        # This is a hand-coded DSU (decorate-sort-undecorate, or
        # Schwartzian transform) pattern.  The sort key is the raw name
        # of the file as specifed on the \include, \input, etc. line.
        # TODO: what about the comment in the original Classic scanner:
        # """which lets
        # us keep the sort order constant regardless of whether the file
        # is actually found in a Repository or locally."""
        nodes = []
        source_dir = node.get_dir()
        for include in includes:
            #
            # Handle multiple filenames in include[1]
            #
            n, i = self.find_include(include, source_dir, path_dict)
            if n is None:
                # Do not bother with 'usepackage' warnings, as they most
                # likely refer to system-level files
                if include[0] != 'usepackage':
                    SCons.Warnings.warn(SCons.Warnings.DependencyWarning,
                                        "No dependency generated for file: %s (included from: %s) -- file not found" % (i, node))
            else:
                sortkey = self.sort_key(n)
                nodes.append((sortkey, n))
        #
        nodes.sort()
        nodes = map(lambda pair: pair[1], nodes)
        return nodes
