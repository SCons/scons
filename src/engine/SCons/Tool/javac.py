"""SCons.Tool.javac

Tool-specific initialization for javac.

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

import glob
import os.path

import SCons.Builder

def generate(env, platform):
    """Add Builders and construction variables for javac to an Environment."""
    try:
        bld = env['BUILDERS']['Java']
    except KeyError:
        def emit_java_files(target, source, env):
            """Create and return lists of source java files
            and their corresponding target class files.
            """
            env['_JAVACLASSDIR'] = target[0]
            env['_JAVASRCDIR'] = source[0]
            java_suffix = env.get('JAVASUFFIX', '.java')
            class_suffix = env.get('JAVACLASSSUFFIX', '.class')
            slist = []
            def visit(arg, dirname, names, js=java_suffix):
                java_files = filter(lambda n, js=js: n[-len(js):] == js, names)
                java_paths = map(lambda f, d=dirname:
                                        os.path.join(d, f),
                                 java_files)
                arg.extend(java_paths)
            os.path.walk(source[0], visit, slist)
            tlist = map(lambda x, t=target[0], cs=class_suffix:
                               os.path.join(t, x[:-5] + cs),
                        slist)

            return tlist, slist

        JavaBuilder = SCons.Builder.Builder(action = '$JAVACCOM',
                            emitter = emit_java_files,
                            target_factory = SCons.Node.FS.default_fs.File,
                            source_factory = SCons.Node.FS.default_fs.File)

        env['BUILDERS']['Java'] = JavaBuilder

    env['JAVAC']           = 'javac'
    env['JAVACFLAGS']      = ''
    env['JAVACCOM']        = '$JAVAC $JAVACFLAGS -d $_JAVACLASSDIR -sourcepath $_JAVASRCDIR $SOURCES'
    env['JAVACLASSSUFFIX'] = '.class'
    env['JAVASUFFIX']      = '.java'

def exists(env):
    return env.Detect('javac')
