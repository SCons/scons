"""SCons.Tool.qt

Tool-specific initialization for qt.

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

import SCons.Defaults
import SCons.Tool
import SCons.Util

header_extensions = (".h", ".H", ".hxx", ".hpp", ".hh")

class _Automoc:
    """
    Callable class, which works as an emitter for Programs, SharedLibraries and
    StaticLibraries.
    """

    def __init__(self, objBuilder,uicDeclBuild,mocFromHBld,mocFromCppBld):
        self.objBuilder = objBuilder
        self.uicDeclBld = uicDeclBuild
        self.mocFromHBld = mocFromHBld
        self.mocFromCppBld = mocFromCppBld
        
    def __call__(self, target, source, env):
        """
        Smart autoscan function. Gets the list of objects for the Program
        or Lib. Adds objects and builders for the special qt files.
        """
        # To make the following work, we assume that we stay in the
        # root directory
        old_os_cwd = os.getcwd()
        old_fs_cwd = SCons.Node.FS.default_fs.getcwd()
        SCons.Node.FS.default_fs.chdir(SCons.Node.FS.default_fs.Dir('#'),
                                       change_os_dir=1)

        # a regular expression for the Q_OBJECT macro
        # currently fails, when Q_OBJECT is in comment (e.g. /* Q_OBJECT */)
        q_object_search = re.compile(r'\sQ_OBJECT[\s;]')
        # out_sources contains at least all sources for the Library or Prog
        out_sources = source[:]
        for s in source:
            prefix, suffix = SCons.Util.splitext(str(s))
            # Nodes for header (h) / moc file (moc_cpp) / cpp file (cpp)
            # and ui.h file (ui_h)
            cpp = s.sources[0]
            ui = None
            if cpp.sources != None and len(cpp.sources) > 0:
                src_src_suffix = SCons.Util.splitext(str(cpp.sources[0]))[1]
                if src_src_suffix == env.subst('$QT_UISUFFIX'):
                    ui = cpp.sources[0]
            
            src_prefix, src_suffix = SCons.Util.splitext(str(cpp.srcnode()))
            h=None
            for h_ext in header_extensions:
                if os.path.exists(src_prefix + h_ext):
                    h = SCons.Node.FS.default_fs.File(prefix + h_ext)

            if ui:
                # file built from .ui file -> build also header from .ui
                h = self.uicDeclBld(env, prefix, ui)
                env.Depends(cpp, h)
                ui_h_suff = env.subst('$QT_UIHSUFFIX')
                if os.path.exists(src_prefix + ui_h_suff):
                    # if a .ui.h file exists, we need to specify the dependecy ...
                    ui_h = SCons.Node.FS.default_fs.File(prefix + ui_h_suff)
                    env.Depends(cpp, ui_h)
            if (h and q_object_search.search(h.get_contents())) or ui:
                # h file with the Q_OBJECT macro found -> add moc_cpp
                dir,base = os.path.split(prefix)
                src_ext = SCons.Util.splitext(str(h))[1]
                moc_cpp = SCons.Node.FS.default_fs.File(os.path.join(dir, 
                    env['QT_MOCNAMEGENERATOR'](base, src_ext, env)))
                moc_o = self.objBuilder(source=moc_cpp)
                out_sources.append(moc_o)
                self.objBuilder(moc_o, moc_cpp)
                self.mocFromHBld(env, moc_cpp, h)
                moc_cpp.target_scanner = SCons.Defaults.CScan
            if cpp and q_object_search.search(cpp.get_contents()):
                # cpp file with Q_OBJECT macro found -> add moc
                # (to be included in cpp)
                dir,base = os.path.split(prefix)
                src_ext = SCons.Util.splitext(str(cpp))[1]
                moc = SCons.Node.FS.default_fs.File(os.path.join(dir, 
                    env['QT_MOCNAMEGENERATOR'](base, src_ext, env)))
                self.mocFromCppBld(env, moc, cpp)
                env.Ignore(moc, moc)
                moc.source_scanner = SCons.Defaults.CScan

        os.chdir(old_os_cwd)
        SCons.Node.FS.default_fs.chdir(old_fs_cwd)
        return (target, out_sources)

def _detect(env):
    """Not really safe, but fast method to detect the QT library"""
    QTDIR = None
    if not QTDIR:
        QTDIR = env.get('QTDIR',None)
    if not QTDIR:
        QTDIR = os.environ.get('QTDIR',None)
    if not QTDIR:
        moc = env.Detect('moc')
        if moc:
            QTDIR = os.path.dirname(os.path.dirname(moc))
        else:
            QTDIR = None
    env['QTDIR'] = QTDIR
    return QTDIR

def generate(env):
    """Add Builders and construction variables for qt to an Environment."""
    _detect(env)
    env['QT_MOC']    = os.path.join('$QTDIR','bin','moc')
    env['QT_UIC']    = os.path.join('$QTDIR','bin','uic')
    env['QT_LIB']    = 'qt'

    # Some QT specific flags. I don't expect someone wants to
    # manipulate those ...
    env['QT_UICIMPLFLAGS'] = ''
    env['QT_UICDECLFLAGS'] = ''
    env['QT_MOCFROMHFLAGS'] = ''
    env['QT_MOCFROMCXXFLAGS'] = '-i'

    # Suffixes for the headers / sources to generate
    env['QT_HSUFFIX'] = '.h'
    env['QT_UISUFFIX'] = '.ui'
    env['QT_UIHSUFFIX'] = '.ui.h'
    env['QT_MOCNAMEGENERATOR'] = \
         lambda x, src_suffix, env: 'moc_' + x + env.get('CXXFILESUFFIX','.cc')

    # Commands for the qt support ...
    # command to generate implementation (cpp) file from a .ui file
    env['QT_UICIMPLCOM'] = ('$QT_UIC $QT_UICIMPLFLAGS -impl '
                            '${TARGETS[0].filebase}$QT_HSUFFIX '
                            '-o $TARGET $SOURCES')
    # command to generate declaration (h) file from a .ui file
    env['QT_UICDECLCOM'] = ('$QT_UIC $QT_UICDECLFLAGS '
                            '-o ${TARGETS[0].base}$QT_HSUFFIX $SOURCES')
    # command to generate meta object information for a class declarated
    # in a header
    env['QT_MOCFROMHCOM'] = '$QT_MOC $QT_MOCFROMHFLAGS -o $TARGET $SOURCE'
    # command to generate meta object information for a class declatazed
    # in a cpp file
    env['QT_MOCFROMCXXCOM'] = '$QT_MOC $QT_MOCFROMCXXFLAGS -o $TARGET $SOURCE'

    # ... and the corresponding builders
    uicDeclBld = SCons.Builder.Builder(action='$QT_UICDECLCOM',
                                       src_suffix='$QT_UISUFFIX',
                                       suffix='$QT_HSUFFIX')
    mocFromHBld = SCons.Builder.Builder(action='$QT_MOCFROMHCOM',
                                        src_suffix='$QT_HSUFFIX',
                                        suffix='$QT_MOCSUFFIX')
    mocFromCppBld = SCons.Builder.Builder(action='$QT_MOCFROMCXXCOM',
                                          src_suffix='$QT_CXXSUFFIX',
                                          suffix='$QT_MOCSUFFIX')

    # we use CXXFile to generate .cpp files from .ui files
    c_file, cxx_file = SCons.Tool.createCFileBuilders(env)
    cxx_file.add_action('$QT_UISUFFIX', '$QT_UICIMPLCOM')

    # We use the emitters of Program / StaticLibrary / SharedLibrary
    # to produce almost all builders except .cpp from .ui
    # First, make sure the Environment has Object builders.
    SCons.Tool.createObjBuilders(env)
    # We can't refer to the builders directly, we have to fetch them
    # as Environment attributes because that sets them up to be called
    # correctly later by our emitter.
    env['PROGEMITTER'] = _Automoc(env.StaticObject,
                                  uicDeclBld,mocFromHBld,mocFromCppBld)
    env['SHLIBEMITTER'] = _Automoc(env.SharedObject,
                                   uicDeclBld,mocFromHBld,mocFromCppBld)
    env['LIBEMITTER'] = _Automoc(env.StaticObject,
                                 uicDeclBld,mocFromHBld,mocFromCppBld)
    # Of course, we need to link against the qt libraries
    env.Append(CPPPATH=os.path.join('$QTDIR', 'include'))
    env.Append(LIBPATH=os.path.join('$QTDIR', 'lib')) 
    env.Append(LIBS='$QT_LIB')

def exists(env):
    return _detect(env)
