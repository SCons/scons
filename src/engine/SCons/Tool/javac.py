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

import os
import os.path
import re
import string

import SCons.Builder
from SCons.Node.FS import _my_normcase

java_parsing = 1

if java_parsing:
    # Parse Java files for class names.
    #
    # This is a really cool parser from Charles Crain
    # that finds appropriate class names in Java source.

    # A regular expression that will find, in a java file,
    # any alphanumeric token (keyword, class name, specifier); open or
    # close brackets; a single-line comment "//"; the multi-line comment
    # begin and end tokens /* and */; single or double quotes; and
    # single or double quotes preceeded by a backslash.
    _reToken = re.compile(r'(//[^\r\n]*|\\[\'"]|[\'"\{\}]|[A-Za-z_][\w\.]*|' +
                          r'/\*|\*/)')

    class OuterState:
        """The initial state for parsing a Java file for classes,
        interfaces, and anonymous inner classes."""
        def __init__(self):
            self.listClasses = []
            self.listOutputs = []
            self.stackBrackets = []
            self.brackets = 0
            self.nextAnon = 1
            self.package = None

        def __getClassState(self):
            try:
                return self.classState
            except AttributeError:
                ret = ClassState(self)
                self.classState = ret
                return ret

        def __getPackageState(self):
            try:
                return self.packageState
            except AttributeError:
                ret = PackageState(self)
                self.packageState = ret
                return ret

        def __getAnonClassState(self):
            try:
                return self.anonState
            except AttributeError:
                ret = SkipState(1, AnonClassState(self))
                self.anonState = ret
                return ret

        def __getSkipState(self):
            try:
                return self.skipState
            except AttributeError:
                ret = SkipState(1, self)
                self.skipState = ret
                return ret

        def parseToken(self, token):
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
            elif token == '"' or token == "'":
                return IgnoreState(token, self)
            elif token == "new":
                # anonymous inner class
                if len(self.listClasses) > 0:
                    return self.__getAnonClassState()
                return self.__getSkipState() # Skip the class name
            elif token == 'class' or token == 'interface':
                if len(self.listClasses) == 0:
                    self.nextAnon = 1
                self.stackBrackets.append(self.brackets)
                return self.__getClassState()
            elif token == 'package':
                return self.__getPackageState()
            return self

        def addAnonClass(self):
            """Add an anonymous inner class"""
            clazz = self.listClasses[0]
            self.listOutputs.append('%s$%d' % (clazz, self.nextAnon))
            self.brackets = self.brackets + 1
            self.nextAnon = self.nextAnon + 1

        def setPackage(self, package):
            self.package = package

    class AnonClassState:
        """A state that looks for anonymous inner classes."""
        def __init__(self, outer_state):
            # outer_state is always an instance of OuterState
            self.outer_state = outer_state
            self.tokens_to_find = 2
        def parseToken(self, token):
            # This is an anonymous class if and only if the next token is a bracket
            if token == '{':
                self.outer_state.addAnonClass()
            return self.outer_state

    class SkipState:
        """A state that will skip a specified number of tokens before
        reverting to the previous state."""
        def __init__(self, tokens_to_skip, old_state):
            self.tokens_to_skip = tokens_to_skip
            self.old_state = old_state
        def parseToken(self, token):
            self.tokens_to_skip = self.tokens_to_skip - 1
            if self.tokens_to_skip < 1:
                return self.old_state
            return self

    class ClassState:
        """A state we go into when we hit a class or interface keyword."""
        def __init__(self, outer_state):
            # outer_state is always an instance of OuterState
            self.outer_state = outer_state
        def parseToken(self, token):
            # the only token we get should be the name of the class.
            self.outer_state.listClasses.append(token)
            return self.outer_state

    class IgnoreState:
        """A state that will ignore all tokens until it gets to a
        specified token."""
        def __init__(self, ignore_until, old_state):
            self.ignore_until = ignore_until
            self.old_state = old_state
        def parseToken(self, token):
            if self.ignore_until == token:
                return self.old_state
            return self

    class PackageState:
        """The state we enter when we encounter the package keyword.
        We assume the next token will be the package name."""
        def __init__(self, outer_state):
            # outer_state is always an instance of OuterState
            self.outer_state = outer_state
        def parseToken(self, token):
            self.outer_state.setPackage(token)
            return self.outer_state

    def parse_java(fn):
        """Parse a .java file and return a double of package directory,
        plus a list of .class files that compiling that .java file will
        produce"""
        package = None
        initial = OuterState()
        currstate = initial
        for token in _reToken.findall(open(fn, 'r').read()):
            # The regex produces a bunch of groups, but only one will
            # have anything in it.
            currstate = currstate.parseToken(token)
        if initial.package:
            package = string.replace(initial.package, '.', os.sep)
        return (package, initial.listOutputs)

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

def classname(path):
    """Turn a string (path name) into a Java class name."""
    return string.replace(os.path.normpath(path), os.sep, '.')

def emit_java_classes(target, source, env):
    """Create and return lists of source java files
    and their corresponding target class files.
    """
    java_suffix = env.get('JAVASUFFIX', '.java')
    class_suffix = env.get('JAVACLASSSUFFIX', '.class')

    slist = []
    js = _my_normcase(java_suffix)
    def visit(arg, dirname, names, js=js, dirnode=source[0].rdir()):
        java_files = filter(lambda n, js=js:
                                   _my_normcase(n[-len(js):]) == js,
                            names)
        mydir = dirnode.Dir(dirname)
        java_paths = map(lambda f, d=mydir: d.File(f), java_files)
        arg.extend(java_paths)
    os.path.walk(source[0].rdir().get_abspath(), visit, slist)

    tlist = []
    for file in slist:
        pkg_dir, classes = parse_java(file.get_abspath())
        if pkg_dir:
            for c in classes:
                t = target[0].Dir(pkg_dir).File(c+class_suffix)
                t.attributes.java_classdir = target[0]
                t.attributes.java_classname = classname(pkg_dir + os.sep + c)
                tlist.append(t)
        elif classes:
            for c in classes:
                t = target[0].File(c+class_suffix)
                t.attributes.java_classdir = target[0]
                t.attributes.java_classname = classname(c)
                tlist.append(t)
        else:
            # This is an odd end case:  no package and no classes.
            # Just do our best based on the source file name.
            base = str(file)[:-len(java_suffix)]
            t = target[0].File(base + class_suffix)
            t.attributes.java_classdir = target[0]
            t.attributes.java_classname = classname(base)
            tlist.append(t)

    return tlist, slist

JavaBuilder = SCons.Builder.Builder(action = '$JAVACCOM',
                    emitter = emit_java_classes,
                    target_factory = SCons.Node.FS.default_fs.Dir,
                    source_factory = SCons.Node.FS.default_fs.Dir)

def generate(env):
    """Add Builders and construction variables for javac to an Environment."""
    env['BUILDERS']['Java'] = JavaBuilder

    env['JAVAC']            = 'javac'
    env['JAVACFLAGS']       = ''
    env['JAVACCOM']         = '$JAVAC $JAVACFLAGS -d ${TARGET.attributes.java_classdir} -sourcepath ${SOURCE.dir.rdir()} $SOURCES'
    env['JAVACLASSSUFFIX']  = '.class'
    env['JAVASUFFIX']       = '.java'

def exists(env):
    return env.Detect('javac')
