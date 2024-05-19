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

"""Tool-specific initialization for jar.

There normally shouldn't be any need to import this module directly.
It will usually be imported through the generic SCons.Tool.Tool()
selection method.
"""

import os
from typing import List

import SCons.Node
import SCons.Node.FS
import SCons.Subst
import SCons.Tool
import SCons.Util
import SCons.Warnings
from SCons.Node.FS import _my_normcase
from SCons.Tool.JavaCommon import get_java_install_dirs


def jarSources(target, source, env, for_signature) -> List[str]:
    """Only include sources that are not a manifest file."""
    try:
        env['JARCHDIR']
    except KeyError:
        jarchdir_set = False
    else:
        jarchdir_set = True
        jarchdir = env.subst('$JARCHDIR', target=target, source=source)
        if jarchdir:
            jarchdir = env.fs.Dir(jarchdir)
    result = []
    for src in source:
        contents = src.get_text_contents()
        if contents.startswith("Manifest-Version"):
            continue
        if jarchdir_set:
            _chdir = jarchdir
        else:
            try:
                _chdir = src.attributes.java_classdir
            except AttributeError:
                _chdir = None
        if _chdir:
            # If we are changing the dir with -C, then sources should
            # be relative to that directory.
            src = SCons.Subst.Literal(src.get_path(_chdir))
            result.append('-C')
            result.append(_chdir)
        result.append(src)
    return result

def jarManifest(target, source, env, for_signature):
    """Look in sources for a manifest file, if any."""
    for src in source:
        contents = src.get_text_contents()
        if contents.startswith("Manifest-Version"):
            return src
    return ''

def jarFlags(target, source, env, for_signature) -> str:
    """If we have a manifest, make sure that the 'm'
    flag is specified."""
    jarflags = env.subst('$JARFLAGS', target=target, source=source)
    for src in source:
        contents = src.get_text_contents()
        if contents.startswith("Manifest-Version"):
            if 'm' not in jarflags:
                return jarflags + 'm'
            break
    return jarflags

def Jar(env, target=None, source=[], *args, **kw):
    """The Jar Builder.

    This is a pseudo-Builder wrapper around the separate jar builders
    depending on whether the sources are a file list or a directory.
    """
    # TODO: W1113: Keyword argument before variable positional arguments list in the definition of Jar function
    # TODO: W0102: Dangerous default value [] as argument

    # jar target should not be a list so assume they passed
    # no target and want implicit target to be made and the arg
    # was actaully the list of sources
    if SCons.Util.is_List(target) and source == []:
        SCons.Warnings.warn(
            SCons.Warnings.SConsWarning,
            "Making implicit target jar file, and treating the list as sources"
        )
        source = target
        target = None

    # mutiple targets passed so build each target the same from the
    # same source
    #TODO Maybe this should only be done once, and the result copied
    #     for each target since it should result in the same?
    if SCons.Util.is_List(target) and SCons.Util.is_List(source):
        jars = []
        for single_target in target:
            jars += env.Jar(target=single_target, source=source, *args, **kw)
        return jars

    # they passed no target so make a target implicitly
    if target is None:
        try:
            # make target from the first source file
            target = os.path.splitext(str(source[0]))[0] + env.subst('$JARSUFFIX')
        except:
            # TODO: W0702: No exception type(s) specified
            # something strange is happening but attempt anyways
            SCons.Warnings.warn(
                SCons.Warnings.SConsWarning,
                "Could not make implicit target from sources, using directory"
            )
            target = os.path.basename(str(env.Dir('.'))) + env.subst('$JARSUFFIX')

    # make lists out of our target and sources
    if not SCons.Util.is_List(target):
        target = [target]
    if not SCons.Util.is_List(source):
        source = [source]

    # setup for checking through all the sources and handle accordingly
    java_class_suffix = env.subst('$JAVACLASSSUFFIX')
    java_suffix = env.subst('$JAVASUFFIX')
    target_nodes = []

    # function for determining what to do with a file and not a directory
    # if its already a class file then it can be used as a
    # source for jar, otherwise turn it into a class file then
    # return the source
    def file_to_class(src):
        if _my_normcase(str(src)).endswith(java_suffix):
            return env.JavaClassFile(source=src, *args, **kw)
        return [env.fs.File(src)]

    # function for calling the JavaClassDir builder if a directory is
    # passed as a source to Jar builder. The JavaClassDir builder will
    # return an empty list if there were no target classes built from
    # the directory, in this case assume the user wanted the directory
    # copied into the jar as is (it contains other files such as
    # resources or class files compiled from prior commands)
    # TODO: investigate the expexcted behavior for directories that
    #       have mixed content, such as Java files along side other files
    #       files.
    def dir_to_class(src):
        dir_targets = env.JavaClassDir(source=src, *args, **kw)
        if dir_targets == []:
            # no classes files could be built from the source dir
            # so pass the dir as is.
            return [env.fs.Dir(src)]
        return dir_targets

    # loop through the sources and handle each accordingly
    # the goal here is to get all the source files into a class
    # file or a directory that contains class files
    for src in SCons.Util.flatten(source):
        src = env.subst(src)
        if isinstance(src, SCons.Node.FS.Base):
            if isinstance(src, SCons.Node.FS.File):
                # found a file so make sure its a class file
                target_nodes.extend(file_to_class(src))
            else:
                # found a dir so get the class files out of it
                target_nodes.extend(dir_to_class(src))
        else:
            try:
                # source is string try to convert it to file
                target_nodes.extend(file_to_class(env.fs.File(src)))
                continue
            except:
                # TODO: W0702: No exception type(s) specified
                pass

            try:
                # source is string try to covnert it to dir
                target_nodes.extend(dir_to_class(env.fs.Dir(src)))
                continue
            except:
                # TODO: W0702: No exception type(s) specified
                pass

            SCons.Warnings.warn(
                SCons.Warnings.SConsWarning,
                ("File: " + str(src)
                + " could not be identified as File or Directory, skipping.")
            )

    # at this point all our sources have been converted to classes or
    # directories of class so pass it to the Jar builder
    return env.JarFile(target=target, source=target_nodes, *args, **kw)

def generate(env) -> None:
    """Add Builders and construction variables for jar to an Environment."""
    SCons.Tool.CreateJarBuilder(env)

    SCons.Tool.CreateJavaFileBuilder(env)
    SCons.Tool.CreateJavaClassFileBuilder(env)
    SCons.Tool.CreateJavaClassDirBuilder(env)

    env.AddMethod(Jar)

    if env['PLATFORM'] == 'win32':
        # Ensure that we have a proper path for jar
        paths = get_java_install_dirs('win32')
        jar = SCons.Tool.find_program_path(env, 'jar', default_paths=paths)
        if jar:
            jar_bin_dir = os.path.dirname(jar)
            env.AppendENVPath('PATH', jar_bin_dir)

    env['JAR'] = 'jar'
    env['JARFLAGS'] = SCons.Util.CLVar('cf')
    env['_JARFLAGS'] = jarFlags
    env['_JARMANIFEST'] = jarManifest
    env['_JARSOURCES'] = jarSources
    env['_JARCOM'] = '$JAR $_JARFLAGS $TARGET $_JARMANIFEST $_JARSOURCES'
    env['JARCOM'] = "${TEMPFILE('$_JARCOM','$JARCOMSTR')}"
    env['JARSUFFIX'] = '.jar'

def exists(env) -> bool:
    # As reported by Jan Nijtmans in issue #2730, the simple
    #    return env.Detect('jar')
    # doesn't always work during initialization. For now, we
    # stop trying to detect an executable (analogous to the
    # javac Builder).
    # TODO: Come up with a proper detect() routine...and enable it.
    return True

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
