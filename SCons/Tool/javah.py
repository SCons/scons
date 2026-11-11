#
# MIT License
#
# Copyright The SCons Foundation
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

"""SCons.Tool.javah

Tool-specific initialization for javah.

The ``javah`` command was removed in Java 10 (JEP 313), but ``javac``
has been able to generate JNI headers with its ``-h`` option since
Java 8.  If ``javah`` is available it is used; otherwise the ``JavaH``
builder drives ``javac -h`` instead, so existing build descriptions
keep working.

There normally shouldn't be any need to import this module directly.
It will usually be imported through the generic SCons.Tool.Tool()
selection method.

"""

import os.path

import SCons.Action
import SCons.Builder
import SCons.Errors
import SCons.Node.FS
import SCons.Tool.javac
import SCons.Util
from SCons.Tool.JavaCommon import (
    get_java_install_dirs,
    is_jni_header_class,
    parse_java_file_native_classes,
)


def _use_javac(env) -> bool:
    """Return whether the ``JavaH`` builder should use ``javac -h``.

    A ``JAVAH`` value which names a ``javah`` command selects the legacy
    protocol; anything else (normally ``javac``) selects ``javac -h``.
    """
    javah = env.subst('$JAVAH') if env.get('JAVAH') else 'javah'
    return 'javah' not in str(javah).lower()


def _java_source(node):
    """Return the ``.java`` source node for a Java class node, if known."""
    if str(node).endswith('.java'):
        return node
    for src in getattr(node, 'sources', []):
        if str(src).endswith('.java'):
            return src
    return None


def _is_native_class(node, classname):
    """Return whether *classname* declares native methods.

    ``None`` is returned when the Java source cannot be found or parsed,
    in which case the caller should assume a header may be produced.
    """
    source = _java_source(node)
    if source is None:
        return None
    try:
        natives = parse_java_file_native_classes(source.get_abspath())
    except OSError:
        return None
    if natives is None:
        return None
    name = classname.rsplit('.', 1)[-1]
    if name not in natives:
        return False
    # javac only writes a header for a top level class or a named
    # nested class, so a class declared in a method, an anonymous
    # class, or the synthetic class behind an enum constant with a
    # class body never gets one.
    return is_jni_header_class(name)


def _header_name(classname, use_javac):
    """Return the header file name for *classname*."""
    name = classname.replace('.', '_')
    if use_javac:
        # javac -h flattens nested classes as well as package separators.
        name = name.replace('$', '_')
    return name + '.h'


def emit_java_headers(target, source, env):
    """Create and return lists of Java stub header files that will
    be created from a set of class files.
    """
    use_javac = _use_javac(env)
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
        if use_javac:
            raise SCons.Errors.UserError(
                "The JavaH builder cannot write a single header file when "
                "using javac -h. Use a directory as the target, or a JDK "
                "which still provides the javah command."
            )
        tlist = target
    else:
        if not isinstance(target[0], SCons.Node.FS.Dir):
            target[0].__class__ = SCons.Node.FS.Dir
            target[0]._morph()
        tlist = []
        for s in slist:
            classname = s.attributes.java_classname
            if use_javac and _is_native_class(s, classname) is False:
                # javac -h only writes headers for classes with native
                # methods, so don't declare headers which won't exist.
                continue
            fname = _header_name(classname, use_javac)
            t = target[0].File(fname)
            t.attributes.java_lookupdir = target[0]
            tlist.append(t)

    return tlist, source


def _out_arg(target, use_javac):
    """Return the command-line arguments selecting the header output."""
    try:
        t = target[0]
    except (AttributeError, IndexError, TypeError):
        t = target
    if use_javac:
        try:
            return ['-h', str(t.attributes.java_lookupdir)]
        except AttributeError:
            raise SCons.Errors.UserError(
                "The JavaH builder cannot write a single header file when "
                "using javac -h. Use a directory as the target, or a JDK "
                "which still provides the javah command."
            )
    try:
        return ['-d', str(t.attributes.java_lookupdir)]
    except AttributeError:
        return ['-o', str(t)]


def _classdir_arg(source):
    """Return the javac output directory argument for class files."""
    try:
        return ['-d', str(source[0].attributes.java_classdir)]
    except AttributeError:
        return []


def _classpath_arg(source, env):
    """Return the classpath argument used to resolve referenced classes."""
    path = "${SOURCE.attributes.java_classdir}"
    if env.get('JAVACLASSPATH'):
        path = SCons.Util.AppendPath(path, env['JAVACLASSPATH'])
    return ['-classpath', path]


def _sources_arg(source, use_javac):
    """Return the names to pass to the header generator."""
    if not use_javac:
        return [str(s.attributes.java_classname) for s in source]

    result = []
    for s in source:
        java = _java_source(s)
        if java is None:
            raise SCons.Errors.UserError(
                "The JavaH builder needs .java source files when using "
                f"javac -h, but no Java source is known for {s}. Pass the "
                "result of the Java builder, or the .java files themselves."
            )
        path = str(java)
        if path not in result:
            result.append(path)
    return result


def JavaHArgsGenerator(target, source, env, for_signature):
    """Generate the argument list for the header generation command."""
    use_javac = _use_javac(env)
    args = _out_arg(target, use_javac)
    if use_javac:
        args += _classdir_arg(source)
    args += _classpath_arg(source, env)
    args += _sources_arg(source, use_javac)
    return args


def generate(env) -> None:
    """Add Builders and construction variables for javah to an Environment."""
    java_javah = SCons.Tool.CreateJavaHBuilder(env)
    java_javah.emitter = emit_java_headers

    if env['PLATFORM'] == 'win32':
        # Ensure that we have a proper path for javah, or for javac when
        # falling back to javac -h.
        paths = get_java_install_dirs('win32')
        javah = SCons.Tool.find_program_path(env, 'javah', default_paths=paths)
        if javah:
            javah_bin_dir = os.path.dirname(javah)
            env.AppendENVPath('PATH', javah_bin_dir)
        else:
            javac = SCons.Tool.find_program_path(env, 'javac', default_paths=paths)
            if javac:
                javac_bin_dir = os.path.dirname(javac)
                env.AppendENVPath('PATH', javac_bin_dir)

    # javah was removed in JDK 10; any JDK with javac provides -h.
    env.SetDefault(
        JAVAH='javah' if env.Detect('javah') else 'javac',
        JAVAHFLAGS=SCons.Util.CLVar(''),
        JAVACLASSSUFFIX='.class',
        JAVASUFFIX='.java',
    )
    env['_JAVAHARGS'] = JavaHArgsGenerator
    env['JAVAHCOM'] = '$JAVAH $JAVAHFLAGS $_JAVAHARGS'


def exists(env) -> bool:
    if env.Detect('javah') or env.Detect('javac'):
        return True
    # On Windows the JDK may not be on PATH; search the usual
    # install locations as well.
    paths = get_java_install_dirs(env['PLATFORM'])
    return bool(
        SCons.Tool.find_program_path(env, 'javah', default_paths=paths)
        or SCons.Tool.find_program_path(env, 'javac', default_paths=paths)
    )
