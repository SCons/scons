"""SCons.Tool.tex

Tool-specific initialization for TeX.

There normally shouldn't be any need to import this module directly.
It will usually be imported through the generic SCons.Tool.Tool()
selection method.

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
import re
import string

import SCons.Action
import SCons.Node
import SCons.Node.FS
import SCons.Util

# An Action sufficient to build any generic tex file.
TeXAction = None

# An action to build a latex file.  This action might be needed more
# than once if we are dealing with labels and bibtex.
LaTeXAction = None

# An action to run BibTeX on a file.
BibTeXAction = None

# An action to run MakeIndex on a file.
MakeIndexAction = None

def InternalLaTeXAuxAction(XXXLaTeXAction, target = None, source= None, env=None):
    """A builder for LaTeX files that checks the output in the aux file
    and decides how many times to use LaTeXAction, and BibTeXAction."""

    basename, ext = SCons.Util.splitext(str(target[0]))

    # Run LaTeX once to generate a new aux file.
    XXXLaTeXAction(target,source,env)

    # Decide if various things need to be run, or run again.  We check
    # for the existence of files before opening them--even ones like the
    # aux file that TeX always creates--to make it possible to write tests
    # with stubs that don't necessarily generate all of the same files.

    # Now decide if bibtex will need to be run.
    auxfilename = basename + '.aux'
    if os.path.exists(auxfilename):
        content = open(auxfilename, "rb").read()
        if string.find(content, "bibdata") != -1:
            bibfile = env.fs.File(basename)
            BibTeXAction(None,bibfile,env)

    # Now decide if makeindex will need to be run.
    idxfilename = basename + '.idx'
    if os.path.exists(idxfilename):
        idxfile = env.fs.File(basename)
        # TODO: if ( idxfile has changed) ...
        MakeIndexAction(None,idxfile,env)
        LaTeXAction(target,source,env)

    # Now decide if latex needs to be run yet again.
    logfilename = basename + '.log'
    for trial in range(int(env.subst('$LATEXRETRIES'))):
        if not os.path.exists(logfilename):
            break
        content = open(logfilename, "rb").read()
        if not re.search("^LaTeX Warning:.*Rerun",content,re.MULTILINE) and not re.search("^LaTeX Warning:.*undefined references",content,re.MULTILINE):
            break
        XXXLaTeXAction(target,source,env)
    return 0

def LaTeXAuxAction(target = None, source= None, env=None):
    InternalLaTeXAuxAction( LaTeXAction, target, source, env )

LaTeX_re = re.compile("\\\\document(style|class)")

def is_LaTeX(flist):
    # Scan a file list to decide if it's TeX- or LaTeX-flavored.
    for f in flist:
        content = f.get_contents()
        if LaTeX_re.search(content):
            return 1
    return 0

def TeXLaTeXFunction(target = None, source= None, env=None):
    """A builder for TeX and LaTeX that scans the source file to
    decide the "flavor" of the source and then executes the appropriate
    program."""
    if is_LaTeX(source):
        LaTeXAuxAction(target,source,env)
    else:
        TeXAction(target,source,env)
    return 0

def tex_emitter(target, source, env):
    base = SCons.Util.splitext(str(source[0]))[0]
    target.append(base + '.aux')
    target.append(base + '.log')
    return (target, source)

TeXLaTeXAction = None

def generate(env):
    """Add Builders and construction variables for TeX to an Environment."""

    # A generic tex file Action, sufficient for all tex files.
    global TeXAction
    if TeXAction is None:
        TeXAction = SCons.Action.Action("$TEXCOM", "$TEXCOMSTR")

    # An Action to build a latex file.  This might be needed more
    # than once if we are dealing with labels and bibtex.
    global LaTeXAction
    if LaTeXAction is None:
        LaTeXAction = SCons.Action.Action("$LATEXCOM", "$LATEXCOMSTR")

    # Define an action to run BibTeX on a file.
    global BibTeXAction
    if BibTeXAction is None:
        BibTeXAction = SCons.Action.Action("$BIBTEXCOM", "$BIBTEXCOMSTR")

    # Define an action to run MakeIndex on a file.
    global MakeIndexAction
    if MakeIndexAction is None:
        MakeIndexAction = SCons.Action.Action("$MAKEINDEXCOM", "$MAKEINDEXOMSTR")

    global TeXLaTeXAction
    if TeXLaTeXAction is None:
        TeXLaTeXAction = SCons.Action.Action(TeXLaTeXFunction, strfunction=None)

    import dvi
    dvi.generate(env)

    bld = env['BUILDERS']['DVI']
    bld.add_action('.tex', TeXLaTeXAction)
    bld.add_emitter('.tex', tex_emitter)

    env['TEX']      = 'tex'
    env['TEXFLAGS'] = SCons.Util.CLVar('')
    env['TEXCOM']   = '$TEX $TEXFLAGS $SOURCE'

    # Duplicate from latex.py.  If latex.py goes away, then this is still OK.
    env['LATEX']        = 'latex'
    env['LATEXFLAGS']   = SCons.Util.CLVar('')
    env['LATEXCOM']     = '$LATEX $LATEXFLAGS $SOURCE'
    env['LATEXRETRIES'] = 3

    env['BIBTEX']      = 'bibtex'
    env['BIBTEXFLAGS'] = SCons.Util.CLVar('')
    env['BIBTEXCOM']   = '$BIBTEX $BIBTEXFLAGS $SOURCE'

    env['MAKEINDEX']      = 'makeindex'
    env['MAKEINDEXFLAGS'] = SCons.Util.CLVar('')
    env['MAKEINDEXCOM']   = '$MAKEINDEX $MAKEINDEXFLAGS $SOURCES'

def exists(env):
    return env.Detect('tex')
