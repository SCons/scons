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

import os.path
import string

import SCons.Builder

# Okay, I don't really know what configurability would be good for
# parsing Java files for package and/or class names, but it was easy, so
# here it is.
#
# Set java_parsing to the following values to enable three different
# flavors of parsing:
#
#    0  The file isn't actually parsed, so this will be quickest.  The
#       package + class name is assumed to be the file path name, and we
#       just split the path name.  This breaks if a package name will
#       ever be different from the path to the .java file.
#
#    1  The file is read to find the package name, after which we stop.
#       This should be pretty darn quick, and allows flexibility in
#       package names, but assumes that the public class name in the
#       file matches the file name.  This seems to be a good assumption
#       because, for example, if you try to declare a public class
#       with a different name from the file, javac tells you:
#
#           class Foo is public, should be declared in a file named Foo.java
#
#    2  Full flexibility of class names.  We parse for the package name
#       (like level #1) but the output .class file name is assumed to
#       match the declared public class name--and, as a bonus, this will
#       actually support multiple public classes in a single file.  My
#       guess is that's illegal Java, though...  Or is it an option
#       supported by some compilers?
#
java_parsing = 1

if java_parsing == 0:
    def parse_java(file, suffix):
        """ "Parse" a .java file.

        This actually just splits the file name, so the assumption here
        is that the file name matches the public class name, and that
        the path to the file is the same as the package name.
        """
        return os.path.split(file)
elif java_parsing == 1:
    def parse_java(file, suffix):
        """Parse a .java file for a package name.

        This, of course, is not full parsing of Java files, but
        simple-minded searching for the usual begins-in-column-1
        "package" string most Java programs use to define their package.
        """
        pkg_dir = None
        classes = []
        f = open(file, "rb")
        while 1:
            line = f.readline()
            if not line:
                break
            if line[:7] == 'package':
                pkg = string.split(line)[1]
                if pkg[-1] == ';':
                    pkg = pkg[:-1]
                pkg_dir = apply(os.path.join, string.split(pkg, '.'))
                classes = [ os.path.split(file[:-len(suffix)])[1] ]
                break
        f.close()
        return pkg_dir, classes

elif java_parsing == 2:
    import re
    pub_re = re.compile('^\s*public(\s+abstract)?\s+class\s+(\S+)')
    def parse_java(file, suffix):
        """Parse a .java file for package name and classes.
    
        This, of course, is not full parsing of Java files, but
        simple-minded searching for the usual strings most Java programs
        seem to use for packages and public class names.
        """
        pkg_dir = None
        classes = []
        f = open(file, "rb")
        while 1:
            line = f.readline()
            if not line:
                break
            if line[:7] == 'package':
                pkg = string.split(line)[1]
                if pkg[-1] == ';':
                    pkg = pkg[:-1]
                pkg_dir = apply(os.path.join, string.split(pkg, '.'))
            elif line[:6] == 'public':
                c = pub_re.findall(line)
                try:
                    classes.append(c[0][1])
                except IndexError:
                    pass
        f.close()
        return pkg_dir, classes

def generate(env, platform):
    """Add Builders and construction variables for javac to an Environment."""
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
        tlist = []
        for file in slist:
            pkg_dir, classes = parse_java(file, java_suffix)
            if pkg_dir:
                for c in classes:
                    tlist.append(os.path.join(target[0],
                                              pkg_dir,
                                              c + class_suffix))
            else:
                tlist.append(os.path.join(target[0],
                                          file[:-5] + class_suffix))
        return tlist, slist

    JavaBuilder = SCons.Builder.Builder(action = '$JAVACCOM',
                        emitter = emit_java_files,
                        target_factory = SCons.Node.FS.default_fs.File,
                        source_factory = SCons.Node.FS.default_fs.File)

    env['BUILDERS']['Java'] = JavaBuilder

    env['JAVAC']            = 'javac'
    env['JAVACFLAGS']       = ''
    env['JAVACCOM']         = '$JAVAC $JAVACFLAGS -d $_JAVACLASSDIR -sourcepath $_JAVASRCDIR $SOURCES'
    env['JAVACLASSSUFFIX']  = '.class'
    env['JAVASUFFIX']       = '.java'

def exists(env):
    return env.Detect('javac')
