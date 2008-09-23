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
import shutil

import SCons.Action
import SCons.Node
import SCons.Node.FS
import SCons.Util

Verbose = False

must_rerun_latex = True

# these are files that just need to be checked for changes and then rerun latex
check_suffixes = ['.toc', '.lof', '.lot', '.out', '.nav', '.snm']

# these are files that require bibtex or makeindex to be run when they change
all_suffixes = check_suffixes + ['.bbl', '.idx', '.nlo', '.glo']

#
# regular expressions used to search for Latex features
# or outputs that require rerunning latex
#
# search for all .aux files opened by latex (recorded in the .log file)
openout_aux_re = re.compile(r"\\openout.*`(.*\.aux)'")

#printindex_re = re.compile(r"^[^%]*\\printindex", re.MULTILINE)
#printnomenclature_re = re.compile(r"^[^%]*\\printnomenclature", re.MULTILINE)
#printglossary_re = re.compile(r"^[^%]*\\printglossary", re.MULTILINE)

# search to find rerun warnings
warning_rerun_str = '(^LaTeX Warning:.*Rerun)|(^Package \w+ Warning:.*Rerun)'
warning_rerun_re = re.compile(warning_rerun_str, re.MULTILINE)

# search to find citation rerun warnings
rerun_citations_str = "^LaTeX Warning:.*\n.*Rerun to get citations correct"
rerun_citations_re = re.compile(rerun_citations_str, re.MULTILINE)

# search to find undefined references or citations warnings
undefined_references_str = '(^LaTeX Warning:.*undefined references)|(^Package \w+ Warning:.*undefined citations)'
undefined_references_re = re.compile(undefined_references_str, re.MULTILINE)

# used by the emitter
auxfile_re = re.compile(r".", re.MULTILINE)
tableofcontents_re = re.compile(r"^[^%]*\\tableofcontents", re.MULTILINE)
makeindex_re = re.compile(r"^[^%]*\\makeindex", re.MULTILINE)
bibliography_re = re.compile(r"^[^%]*\\bibliography", re.MULTILINE)
listoffigures_re = re.compile(r"^[^%]*\\listoffigures", re.MULTILINE)
listoftables_re = re.compile(r"^[^%]*\\listoftables", re.MULTILINE)
hyperref_re = re.compile(r"^[^%]*\\usepackage.*\{hyperref\}", re.MULTILINE)
makenomenclature_re = re.compile(r"^[^%]*\\makenomenclature", re.MULTILINE)
makeglossary_re = re.compile(r"^[^%]*\\makeglossary", re.MULTILINE)
beamer_re = re.compile(r"^[^%]*\\documentclass\{beamer\}", re.MULTILINE)

# search to find all files opened by Latex (recorded in .log file)
openout_re = re.compile(r"\\openout.*`(.*)'")

# An Action sufficient to build any generic tex file.
TeXAction = None

# An action to build a latex file.  This action might be needed more
# than once if we are dealing with labels and bibtex.
LaTeXAction = None

# An action to run BibTeX on a file.
BibTeXAction = None

# An action to run MakeIndex on a file.
MakeIndexAction = None

# An action to run MakeIndex (for nomencl) on a file.
MakeNclAction = None

# An action to run MakeIndex (for glossary) on a file.
MakeGlossaryAction = None

# Used as a return value of modify_env_var if the variable is not set.
class _Null:
    pass
_null = _Null

# The user specifies the paths in env[variable], similar to other builders.
# They may be relative and must be converted to absolute, as expected
# by LaTeX and Co. The environment may already have some paths in
# env['ENV'][var]. These paths are honored, but the env[var] paths have
# higher precedence. All changes are un-done on exit.
def modify_env_var(env, var, abspath):
    try:
        save = env['ENV'][var]
    except KeyError:
        save = _null
    env.PrependENVPath(var, abspath)
    try:
        if SCons.Util.is_List(env[var]):
            #FUTURE env.PrependENVPath(var, [os.path.abspath(str(p)) for p in env[var]])
            env.PrependENVPath(var, map(lambda p: os.path.abspath(str(p)), env[var]))
        else:
            # Split at os.pathsep to convert into absolute path
            #FUTURE env.PrependENVPath(var, [os.path.abspath(p) for p in str(env[var]).split(os.pathsep)])
            env.PrependENVPath(var, map(lambda p: os.path.abspath(p), str(env[var]).split(os.pathsep)))
    except KeyError:
        pass
    # Convert into a string explicitly to append ":" (without which it won't search system
    # paths as well). The problem is that env.AppendENVPath(var, ":")
    # does not work, refuses to append ":" (os.pathsep).
    if SCons.Util.is_List(env['ENV'][var]):
        env['ENV'][var] = os.pathsep.join(env['ENV'][var])
    # Append the trailing os.pathsep character here to catch the case with no env[var]
    env['ENV'][var] = env['ENV'][var] + os.pathsep
    return save

def InternalLaTeXAuxAction(XXXLaTeXAction, target = None, source= None, env=None):
    """A builder for LaTeX files that checks the output in the aux file
    and decides how many times to use LaTeXAction, and BibTeXAction."""

    global must_rerun_latex

    # This routine is called with two actions. In this file for DVI builds
    # with LaTeXAction and from the pdflatex.py with PDFLaTeXAction
    # set this up now for the case where the user requests a different extension
    # for the target filename
    if (XXXLaTeXAction == LaTeXAction):
       callerSuffix = ".dvi"
    else:
       callerSuffix = env['PDFSUFFIX']

    basename = SCons.Util.splitext(str(source[0]))[0]
    basedir = os.path.split(str(source[0]))[0]
    basefile = os.path.split(str(basename))[1]
    abspath = os.path.abspath(basedir)
    targetext = os.path.splitext(str(target[0]))[1]
    targetdir = os.path.split(str(target[0]))[0]

    saved_env = {}
    for var in SCons.Scanner.LaTeX.LaTeX.env_variables:
        saved_env[var] = modify_env_var(env, var, abspath)

    # Create base file names with the target directory since the auxiliary files
    # will be made there.   That's because the *COM variables have the cd
    # command in the prolog. We check
    # for the existence of files before opening them--even ones like the
    # aux file that TeX always creates--to make it possible to write tests
    # with stubs that don't necessarily generate all of the same files.

    targetbase = os.path.join(targetdir, basefile)

    # if there is a \makeindex there will be a .idx and thus
    # we have to run makeindex at least once to keep the build
    # happy even if there is no index.
    # Same for glossaries and nomenclature
    src_content = source[0].get_contents()
    run_makeindex = makeindex_re.search(src_content) and not os.path.exists(targetbase + '.idx')
    run_nomenclature = makenomenclature_re.search(src_content) and not os.path.exists(targetbase + '.nlo')
    run_glossary = makeglossary_re.search(src_content) and not os.path.exists(targetbase + '.glo')

    saved_hashes = {}
    suffix_nodes = {}

    for suffix in all_suffixes:
        theNode = env.fs.File(targetbase + suffix)
        suffix_nodes[suffix] = theNode
        saved_hashes[suffix] = theNode.get_csig()

    if Verbose:
        print "hashes: ",saved_hashes

    must_rerun_latex = True

    #
    # routine to update MD5 hash and compare
    #
    def check_MD5(filenode, suffix, saved_hashes=saved_hashes):
        global must_rerun_latex
        # two calls to clear old csig
        filenode.clear_memoized_values()
        filenode.ninfo = filenode.new_ninfo()
        new_md5 = filenode.get_csig()

        if saved_hashes[suffix] == new_md5:
            if Verbose:
                print "file %s not changed" % (targetbase+suffix)
            return False        # unchanged
        saved_hashes[suffix] = new_md5
        must_rerun_latex = True
        if Verbose:
            print "file %s changed, rerunning Latex, new hash = " % (targetbase+suffix), new_md5
        return True     # changed

    # generate the file name that latex will generate
    resultfilename = targetbase + callerSuffix

    count = 0

    while (must_rerun_latex and count < int(env.subst('$LATEXRETRIES'))) :
        result = XXXLaTeXAction(target, source, env)
        if result != 0:
            return result

        count = count + 1

        must_rerun_latex = False
        # Decide if various things need to be run, or run again.

        # Read the log file to find all .aux files
        logfilename = targetbase + '.log'
        logContent = ''
        auxfiles = []
        if os.path.exists(logfilename):
            logContent = open(logfilename, "rb").read()
            auxfiles = openout_aux_re.findall(logContent)

        # Now decide if bibtex will need to be run.
        # The information that bibtex reads from the .aux file is
        # pass-independent. If we find (below) that the .bbl file is unchanged,
        # then the last latex saw a correct bibliography.
        # Therefore only do this on the first pass
        if count == 1:
            for auxfilename in auxfiles:
                target_aux = os.path.join(targetdir, auxfilename)
                if os.path.exists(target_aux):
                    content = open(target_aux, "rb").read()
                    if string.find(content, "bibdata") != -1:
                        if Verbose:
                            print "Need to run bibtex"
                        bibfile = env.fs.File(targetbase)
                        result = BibTeXAction(bibfile, bibfile, env)
                        if result != 0:
                            return result
                        must_rerun_latex = check_MD5(suffix_nodes['.bbl'],'.bbl')
                        break

        # Now decide if latex will need to be run again due to index.
        if check_MD5(suffix_nodes['.idx'],'.idx') or (count == 1 and run_makeindex):
            # We must run makeindex
            if Verbose:
                print "Need to run makeindex"
            idxfile = suffix_nodes['.idx']
            result = MakeIndexAction(idxfile, idxfile, env)
            if result != 0:
                return result

        # TO-DO: need to add a way for the user to extend this list for whatever
        # auxiliary files they create in other (or their own) packages
        # Harder is case is where an action needs to be called -- that should be rare (I hope?)

        for index in check_suffixes:
            check_MD5(suffix_nodes[index],index)

        # Now decide if latex will need to be run again due to nomenclature.
        if check_MD5(suffix_nodes['.nlo'],'.nlo') or (count == 1 and run_nomenclature):
            # We must run makeindex
            if Verbose:
                print "Need to run makeindex for nomenclature"
            nclfile = suffix_nodes['.nlo']
            result = MakeNclAction(nclfile, nclfile, env)
            if result != 0:
                return result

        # Now decide if latex will need to be run again due to glossary.
        if check_MD5(suffix_nodes['.glo'],'.glo') or (count == 1 and run_glossary):
            # We must run makeindex
            if Verbose:
                print "Need to run makeindex for glossary"
            glofile = suffix_nodes['.glo']
            result = MakeGlossaryAction(glofile, glofile, env)
            if result != 0:
                return result

        # Now decide if latex needs to be run yet again to resolve warnings.
        if warning_rerun_re.search(logContent):
            must_rerun_latex = True
            if Verbose:
                print "rerun Latex due to latex or package rerun warning"

        if rerun_citations_re.search(logContent):
            must_rerun_latex = True
            if Verbose:
                print "rerun Latex due to 'Rerun to get citations correct' warning"

        if undefined_references_re.search(logContent):
            must_rerun_latex = True
            if Verbose:
                print "rerun Latex due to undefined references or citations"

        if (count >= int(env.subst('$LATEXRETRIES')) and must_rerun_latex):
            print "reached max number of retries on Latex ,",int(env.subst('$LATEXRETRIES'))
# end of while loop

    # rename Latex's output to what the target name is
    if not (str(target[0]) == resultfilename  and  os.path.exists(resultfilename)):
        if os.path.exists(resultfilename):
            print "move %s to %s" % (resultfilename, str(target[0]), )
            shutil.move(resultfilename,str(target[0]))

    # Original comment (when TEXPICTS was not restored):
    # The TEXPICTS enviroment variable is needed by a dvi -> pdf step
    # later on Mac OSX so leave it
    #
    # It is also used when searching for pictures (implicit dependencies).
    # Why not set the variable again in the respective builder instead
    # of leaving local modifications in the environment? What if multiple
    # latex builds in different directories need different TEXPICTS?
    for var in SCons.Scanner.LaTeX.LaTeX.env_variables:
        if var == 'TEXPICTS':
            continue
        if saved_env[var] is _null:
            try:
                del env['ENV'][var]
            except KeyError:
                pass # was never set
        else:
            env['ENV'][var] = saved_env[var]

    return result

def LaTeXAuxAction(target = None, source= None, env=None):
    result = InternalLaTeXAuxAction( LaTeXAction, target, source, env )
    return result

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
        result = LaTeXAuxAction(target,source,env)
    else:
        result = TeXAction(target,source,env)
    return result

def TeXLaTeXStrFunction(target = None, source= None, env=None):
    """A strfunction for TeX and LaTeX that scans the source file to
    decide the "flavor" of the source and then returns the appropriate
    command string."""
    if env.GetOption("no_exec"):
        if is_LaTeX(source):
            result = env.subst('$LATEXCOM',0,target,source)+" ..."
        else:
            result = env.subst("$TEXCOM",0,target,source)+" ..."
    else:
        result = ''
    return result

def tex_emitter(target, source, env):
    """An emitter for TeX and LaTeX sources.
    For LaTeX sources we try and find the common created files that
    are needed on subsequent runs of latex to finish tables of contents,
    bibliographies, indices, lists of figures, and hyperlink references.
    """
    targetbase = SCons.Util.splitext(str(target[0]))[0]
    basename = SCons.Util.splitext(str(source[0]))[0]
    basefile = os.path.split(str(basename))[1]

    #
    # file names we will make use of in searching the sources and log file
    #
    emit_suffixes = ['.aux', '.log', '.ilg', '.blg', '.nls', '.nlg', '.gls', '.glg'] + all_suffixes
    auxfilename = targetbase + '.aux'
    logfilename = targetbase + '.log'

    env.SideEffect(auxfilename,target[0])
    env.SideEffect(logfilename,target[0])
    env.Clean(target[0],auxfilename)
    env.Clean(target[0],logfilename)

    content = source[0].get_contents()
    idx_exists = os.path.exists(targetbase + '.idx')
    nlo_exists = os.path.exists(targetbase + '.nlo')
    glo_exists = os.path.exists(targetbase + '.glo')

    file_tests = [(auxfile_re.search(content),['.aux']),
                  (makeindex_re.search(content) or idx_exists,['.idx', '.ind', '.ilg']),
                  (bibliography_re.search(content),['.bbl', '.blg']),
                  (tableofcontents_re.search(content),['.toc']),
                  (listoffigures_re.search(content),['.lof']),
                  (listoftables_re.search(content),['.lot']),
                  (hyperref_re.search(content),['.out']),
                  (makenomenclature_re.search(content) or nlo_exists,['.nlo', '.nls', '.nlg']),
                  (makeglossary_re.search(content) or glo_exists,['.glo', '.gls', '.glg']),
                  (beamer_re.search(content),['.nav', '.snm', '.out', '.toc']) ]
    # Note we add the various makeindex files if the file produced by latex exists (.idx, .glo, .nlo)
    # This covers the case where the \makeindex, \makenomenclature, or \makeglossary
    # is not in the main file but we want to clean the files and those made by makeindex

    # TO-DO: need to add a way for the user to extend this list for whatever
    # auxiliary files they create in other (or their own) packages

    for (theSearch,suffix_list) in file_tests:
        if theSearch:
            for suffix in suffix_list:
                env.SideEffect(targetbase + suffix,target[0])
                env.Clean(target[0],targetbase + suffix)

    # read log file to get all other files that latex creates and will read on the next pass
    if os.path.exists(logfilename):
        content = open(logfilename, "rb").read()
        out_files = openout_re.findall(content)
        env.SideEffect(out_files,target[0])
        env.Clean(target[0],out_files)

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
        MakeIndexAction = SCons.Action.Action("$MAKEINDEXCOM", "$MAKEINDEXCOMSTR")

    # Define an action to run MakeIndex on a file for nomenclatures.
    global MakeNclAction
    if MakeNclAction is None:
        MakeNclAction = SCons.Action.Action("$MAKENCLCOM", "$MAKENCLCOMSTR")

    # Define an action to run MakeIndex on a file for glossaries.
    global MakeGlossaryAction
    if MakeGlossaryAction is None:
        MakeGlossaryAction = SCons.Action.Action("$MAKEGLOSSARYCOM", "$MAKEGLOSSARYCOMSTR")

    global TeXLaTeXAction
    if TeXLaTeXAction is None:
        TeXLaTeXAction = SCons.Action.Action(TeXLaTeXFunction,
                              strfunction=TeXLaTeXStrFunction)

    import dvi
    dvi.generate(env)

    bld = env['BUILDERS']['DVI']
    bld.add_action('.tex', TeXLaTeXAction)
    bld.add_emitter('.tex', tex_emitter)

    env['TEX']      = 'tex'
    env['TEXFLAGS'] = SCons.Util.CLVar('-interaction=nonstopmode')
    env['TEXCOM']   = 'cd ${TARGET.dir} && $TEX $TEXFLAGS ${SOURCE.file}'

    # Duplicate from latex.py.  If latex.py goes away, then this is still OK.
    env['LATEX']        = 'latex'
    env['LATEXFLAGS']   = SCons.Util.CLVar('-interaction=nonstopmode')
    env['LATEXCOM']     = 'cd ${TARGET.dir} && $LATEX $LATEXFLAGS ${SOURCE.file}'
    env['LATEXRETRIES'] = 3

    env['BIBTEX']      = 'bibtex'
    env['BIBTEXFLAGS'] = SCons.Util.CLVar('')
    env['BIBTEXCOM']   = 'cd ${TARGET.dir} && $BIBTEX $BIBTEXFLAGS ${SOURCE.filebase}'

    env['MAKEINDEX']      = 'makeindex'
    env['MAKEINDEXFLAGS'] = SCons.Util.CLVar('')
    env['MAKEINDEXCOM']   = 'cd ${TARGET.dir} && $MAKEINDEX $MAKEINDEXFLAGS ${SOURCE.file}'

    env['MAKEGLOSSARY']      = 'makeindex'
    env['MAKEGLOSSARYSTYLE'] = '${SOURCE.filebase}.ist'
    env['MAKEGLOSSARYFLAGS'] = SCons.Util.CLVar('-s ${MAKEGLOSSARYSTYLE} -t ${SOURCE.filebase}.glg')
    env['MAKEGLOSSARYCOM']   = 'cd ${TARGET.dir} && $MAKEGLOSSARY ${SOURCE.filebase}.glo $MAKEGLOSSARYFLAGS -o ${SOURCE.filebase}.gls'

    env['MAKENCL']      = 'makeindex'
    env['MAKENCLSTYLE'] = '$nomencl.ist'
    env['MAKENCLFLAGS'] = '-s ${MAKENCLSTYLE} -t ${SOURCE.filebase}.nlg'
    env['MAKENCLCOM']   = 'cd ${TARGET.dir} && $MAKENCL ${SOURCE.filebase}.nlo $MAKENCLFLAGS -o ${SOURCE.filebase}.nls'

    # Duplicate from pdflatex.py.  If latex.py goes away, then this is still OK.
    env['PDFLATEX']      = 'pdflatex'
    env['PDFLATEXFLAGS'] = SCons.Util.CLVar('-interaction=nonstopmode')
    env['PDFLATEXCOM']   = 'cd ${TARGET.dir} && $PDFLATEX $PDFLATEXFLAGS ${SOURCE.file}'

def exists(env):
    return env.Detect('tex')
