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
import re
import string

import SCons.Builder

java_parsing = 1

if java_parsing:
    # Parse Java files for class names.
    #
    # This is a really simple and cool parser from Charles Crain
    # that finds appropriate class names in Java source.

    _reToken = re.compile(r'[^\\]([\'"])|([\{\}])|' +
                          r'(?:^|[\{\}\s;])((?:class|interface)'+
                          r'\s+[A-Za-z_]\w*)|' +
                          r'(new\s+[A-Za-z_]\w*\s*\([^\)]*\)\s*\{)|' +
                          r'(//[^\r\n]*)|(/\*|\*/)')

    class OuterState:
        def __init__(self):
            self.listClasses = []
            self.listOutputs = []
            self.stackBrackets = []
            self.brackets = 0
            self.nextAnon = 1

        def parseToken(self, token):
            #print token
            if token[:2] == '//':
                pass # ignore comment
            elif token == '/*':
                return IgnoreState('*/', self)
            elif token == '{':
                self.brackets = self.brackets + 1
            elif token == '}':
                self.brackets = self.brackets - 1
                if len(self.stackBrackets) and \
                   self.brackets == self.stackBrackets[-1]:
                    self.listOutputs.append(string.join(self.listClasses, '$'))
                    self.listClasses.pop()
                    self.stackBrackets.pop()
            elif token == '"':
                return IgnoreState('"', self)
            elif token == "'":
                return IgnoreState("'", self)
            elif token[:3] == "new":
                # anonymous inner class
                if len(self.listClasses) > 0:
                    clazz = self.listClasses[0]
                    self.listOutputs.append('%s$%d' % (clazz, self.nextAnon))
                    self.brackets = self.brackets + 1
                    self.nextAnon = self.nextAnon + 1
            elif token[:5] == 'class':
                if len(self.listClasses) == 0:
                    self.nextAnon = 1
                self.listClasses.append(string.join(string.split(token[6:])))
                self.stackBrackets.append(self.brackets)
            elif token[:9] == 'interface':
                if len(self.listClasses) == 0:
                    self.nextAnon = 1
                self.listClasses.append(string.join(string.split(token[10:])))
                self.stackBrackets.append(self.brackets)
            return self

    class IgnoreState:
        def __init__(self, ignore_until, old_state):
            self.ignore_until = ignore_until
            self.old_state = old_state
        def parseToken(self, token):
            if token == self.ignore_until:
                return self.old_state
            return self

    def parse_java(file):
        contents = open(file, 'r').read()

        # Is there a more efficient way to do this than to split
        # the contents like this?
        pkg_dir = None
        for line in string.split(contents, "\n"):
            if line[:7] == 'package':
                pkg = string.split(line)[1]
                if pkg[-1] == ';':
                    pkg = pkg[:-1]
                pkg_dir = apply(os.path.join, string.split(pkg, '.'))
                break

        initial = OuterState()
        currstate = initial
        for matches in _reToken.findall(contents):
            # The regex produces a bunch of groups, but only one will
            # have anything in it.
            token = filter(lambda x: x, matches)[0]
            currstate = currstate.parseToken(token)

        return pkg_dir, initial.listOutputs

else:
    # Don't actually parse Java files for class names.
    #
    # We might make this a configurable option in the future if
    # Java-file parsing takes too long (although it shouldn't relative
    # to how long the Java compiler itself seems to take...).

    def parse_java(file):
        """ "Parse" a .java file.

        This actually just splits the file name, so the assumption here
        is that the file name matches the public class name, and that
        the path to the file is the same as the package name.
        """
        return os.path.split(file)

def generate(env):
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
            pkg_dir, classes = parse_java(file)
            if pkg_dir:
                for c in classes:
                    tlist.append(os.path.join(target[0],
                                              pkg_dir,
                                              c + class_suffix))
            elif classes:
                for c in classes:
                    tlist.append(os.path.join(target[0], c + class_suffix))
            else:
                # This is an odd end case:  no package and no classes.
                # Just do our best based on the source file name.
                tlist.append(os.path.join(target[0],
                                          file[:-len(java_suffix)] + class_suffix))

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
