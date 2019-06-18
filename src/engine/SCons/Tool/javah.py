"""SCons.Tool.javah

Tool-specific initialization for javah.

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

import SCons.Action
import SCons.Builder
import SCons.Node.FS
import SCons.Tool.javac
import SCons.Util
from SCons.Tool.JavaCommon import get_java_install_dirs


def emit_java_headers(target, source, env):
    """Create and return lists of Java stub header files that will
    be created from a set of class files.
    """
    class_suffix = env.get('JAVACLASSSUFFIX', '.class')
    classdir = env.get('JAVACLASSDIR')

    if not classdir:
        try:
            s = source[0]
        except IndexError:
            classdir = '.'
        else:
            try:
                classdir = s.attributes.java_classdir
            except AttributeError:
                classdir = '.'
    classdir = env.Dir(classdir).rdir()

    if str(classdir) == '.':
        c_ = None
    else:
        c_ = str(classdir) + os.sep

    slist = []
    for src in source:
        try:
            classname = src.attributes.java_classname
        except AttributeError:
            classname = str(src)
            if c_ and classname[:len(c_)] == c_:
                classname = classname[len(c_):]
            if class_suffix and classname[-len(class_suffix):] == class_suffix:
                classname = classname[:-len(class_suffix)]
            classname = SCons.Tool.javac.classname(classname)
        s = src.rfile()
        s.attributes.java_classname = classname
        slist.append(s)

    s = source[0].rfile()
    if not hasattr(s.attributes, 'java_classdir'):
        s.attributes.java_classdir = classdir

    if target[0].__class__ is SCons.Node.FS.File:
        tlist = target
    else:
        if not isinstance(target[0], SCons.Node.FS.Dir):
            target[0].__class__ = SCons.Node.FS.Dir
            target[0]._morph()
        tlist = []
        for s in source:
            fname = s.attributes.java_classname.replace('.', '_') + '.h'
            t = target[0].File(fname)
            t.attributes.java_lookupdir = target[0]
            tlist.append(t)

    return tlist, source

def JavaHOutFlagGenerator(target, source, env, for_signature):
    try:
        t = target[0]
    except (AttributeError, IndexError, TypeError):
        t = target
    try:
        return '-d ' + str(t.attributes.java_lookupdir)
    except AttributeError:
        return '-o ' + str(t)

def getJavaHClassPath(env,target, source, for_signature):
    path = "${SOURCE.attributes.java_classdir}"
    if 'JAVACLASSPATH' in env and env['JAVACLASSPATH']:
        path = SCons.Util.AppendPath(path, env['JAVACLASSPATH'])
    return "-classpath %s" % (path)

def generate(env):
    """Add Builders and construction variables for javah to an Environment."""
    java_javah = SCons.Tool.CreateJavaHBuilder(env)
    java_javah.emitter = emit_java_headers

    if env['PLATFORM'] == 'win32':
        # Ensure that we have a proper path for javah
        paths = get_java_install_dirs('win32')
        javah = SCons.Tool.find_program_path(env, 'javah', default_paths=paths)
        if javah:
            javah_bin_dir = os.path.dirname(javah)
            env.AppendENVPath('PATH', javah_bin_dir)

    env['_JAVAHOUTFLAG']    = JavaHOutFlagGenerator
    env['JAVAH']            = 'javah'
    env['JAVAHFLAGS']       = SCons.Util.CLVar('')
    env['_JAVAHCLASSPATH']  = getJavaHClassPath
    env['JAVAHCOM']         = '$JAVAH $JAVAHFLAGS $_JAVAHOUTFLAG $_JAVAHCLASSPATH ${SOURCES.attributes.java_classname}'
    env['JAVACLASSSUFFIX']  = '.class'

def exists(env):
    return env.Detect('javah')

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
