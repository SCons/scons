#!/usr/bin/env python2
#
# scons_examples.py -   an SGML preprocessor for capturing SCons output
#                       and inserting into examples in our DocBook
#                       documentation
#

# This script looks for some SGML tags that describe SCons example
# configurations and commands to execute in those configurations, and
# uses TestCmd.py to execute the commands and insert the output into
# the output SGML.  This way, we can run a script and update all of
# our example output without having to do a lot of laborious by-hand
# checking.
#
# An "SCons example" looks like this, and essentially describes a set of
# input files (program source files as well as SConscript files):
#
#       <scons_example name="ex1">
#         <file name="SConstruct" printme="1">
#           env = Environment()
#           env.Program('foo')
#         </file>
#         <file name="foo.c">
#           int main() { printf("foo.c\n"); }
#         </file>
#       </scons_example>
#
# The <file> contents within the <scons_example> tag will get written
# into a temporary directory whenever example output needs to be
# generated.  By default, the <file> contents are not inserted into text
# directly, unless you set the "printme" attribute on one or more files,
# in which case they will get inserted within a <programlisting> tag.
# This makes it easy to define the example at the appropriate
# point in the text where you intend to show the SConstruct file.
#
# Note that you should usually give the <scons_example> a "name"
# attribute so that you can refer to the example configuration later to
# run SCons and generate output.
#
# If you just want to show a file's contents without worry about running
# SCons, there's a shorter <sconstruct> tag:
#
#       <sconstruct>
#         env = Environment()
#         env.Program('foo')
#       </sconstruct>
#
# This is essentially equivalent to <scons_example><file printme="1">,
# but it's more straightforward.
#
# SCons output is generated from the following sort of tag:
#
#       <scons_output example="ex1" os="posix">
#         <command>scons -Q foo</command>
#         <command>scons -Q foo</command>
#       </scons_output>
#
# You tell it which example to use with the "example" attribute, and
# then give it a list of <command> tags to execute.  You can also supply
# an "os" tag, which specifies the type of operating system this example
# is intended to show; if you omit this, default value is "posix".
#
# The generated SGML will show the command line (with the appropriate
# command-line prompt for the operating system), execute the command in
# a temporary directory with the example files, capture the standard
# output from SCons, and insert it into the text as appropriate.
# Error output gets passed through to your error output so you
# can see if there are any problems executing the command.

import os
import os.path
import re
import sgmllib
import sys

sys.path.append(os.path.join(os.getcwd(), 'etc'))
sys.path.append(os.path.join(os.getcwd(), 'build', 'etc'))

scons_py = os.path.join('bootstrap', 'src', 'script', 'scons.py')
if not os.path.exists(scons_py):
    scons_py = os.path.join('src', 'script', 'scons.py')

scons_lib_dir = os.path.join(os.getcwd(), 'bootstrap', 'src', 'engine')
if not os.path.exists(scons_lib_dir):
    scons_lib_dir = os.path.join(os.getcwd(), 'src', 'engine')

import TestCmd

# The regular expression that identifies entity references in the
# standard sgmllib omits the underscore from the legal characters.
# Override it with our own regular expression that adds underscore.
sgmllib.entityref = re.compile('&([a-zA-Z][-_.a-zA-Z0-9]*)[^-_a-zA-Z0-9]')

class DataCollector:
    """Generic class for collecting data between a start tag and end
    tag.  We subclass for various types of tags we care about."""
    def __init__(self):
        self.data = ""
    def afunc(self, data):
        self.data = self.data + data

class Example(DataCollector):
    """An SCons example.  This is essentially a list of files that
    will get written to a temporary directory to collect output
    from one or more SCons runs."""
    def __init__(self):
        DataCollector.__init__(self)
        self.files = []
        self.dirs = []

class File(DataCollector):
    """A file, that will get written out to a temporary directory
    for one or more SCons runs."""
    def __init__(self, name):
        DataCollector.__init__(self)
        self.name = name

class Directory(DataCollector):
    """A directory, that will get created in a temporary directory
    for one or more SCons runs."""
    def __init__(self, name):
        DataCollector.__init__(self)
        self.name = name

class Output(DataCollector):
    """Where the command output goes.  This is essentially
    a list of commands that will get executed."""
    def __init__(self):
        DataCollector.__init__(self)
        self.commandlist = []

class Command(DataCollector):
    """A tag for where the command output goes.  This is essentially
    a list of commands that will get executed."""
    pass

Prompt = {
    'posix' : '% ',
    'win32' : 'C:\\>'
}

# Magick SCons hackery.
#
# So that our examples can still use the default SConstruct file, we
# actually feed the following into SCons via stdin and then have it
# SConscript() the SConstruct file.  This stdin wrapper creates a set
# of ToolSurrogates for the tools for the appropriate platform.  These
# Surrogates print output like the real tools and behave like them
# without actually having to be on the right platform or have the right
# tool installed.
#
# The upshot:  We transparently change the world out from under the
# top-level SConstruct file in an example just so we can get the
# command output.

Stdin = """\
import SCons.Defaults

platform = '%s'

class Curry:
    def __init__(self, fun, *args, **kwargs):
        self.fun = fun
        self.pending = args[:]
        self.kwargs = kwargs.copy()

    def __call__(self, *args, **kwargs):
        if kwargs and self.kwargs:
            kw = self.kwargs.copy()
            kw.update(kwargs)
        else:
            kw = kwargs or self.kwargs

        return self.fun(*self.pending + args, **kw)

def Str(target, source, env, cmd=""):
    result = []
    for cmd in env.subst_list(cmd, target=target, source=source):
        result.append(" ".join(map(str, cmd)))
    return '\\n'.join(result)

class ToolSurrogate:
    def __init__(self, tool, variable, func):
        self.tool = tool
        self.variable = variable
        self.func = func
    def __call__(self, env):
        t = Tool(self.tool)
        t.generate(env)
        orig = env[self.variable]
        env[self.variable] = Action(self.func, strfunction=Curry(Str, cmd=orig))

def Null(target, source, env):
    pass

def Cat(target, source, env):
    target = str(target[0])
    f = open(target, "wb")
    for src in map(str, source):
        f.write(open(src, "rb").read())
    f.close()

ToolList = {
    'posix' :   [('cc', 'CCCOM', Cat),
                 ('link', 'LINKCOM', Cat),
                 ('tar', 'TARCOM', Null),
                 ('zip', 'ZIPCOM', Null)],
    'win32' :   [('msvc', 'CCCOM', Cat),
                 ('mslink', 'LINKCOM', Cat)]
}

tools = map(lambda t: ToolSurrogate(*t), ToolList[platform])

SCons.Defaults.ConstructionEnvironment.update({
    'PLATFORM' : platform,
    'TOOLS'    : tools,
})

SConscript('SConstruct')
"""

class MySGML(sgmllib.SGMLParser):
    """A subclass of the standard Python sgmllib SGML parser.
    """
    def __init__(self):
        sgmllib.SGMLParser.__init__(self)
        self.examples = {}
        self.afunclist = []

    def handle_data(self, data):
        try:
            f = self.afunclist[-1]
        except IndexError:
            sys.stdout.write(data)
        else:
            f(data)

    def handle_comment(self, data):
        sys.stdout.write('<!--' + data + '-->')

    def handle_decl(self, data):
        sys.stdout.write('<!' + data + '>')

    def unknown_starttag(self, tag, attrs):
        try:
            f = self.example.afunc
        except AttributeError:
            f = sys.stdout.write
        if not attrs:
            f('<' + tag + '>')
        else:
            f('<' + tag)
            for name, value in attrs:
                f(' ' + name + '=' + '"' + value + '"')
            f('>')

    def unknown_endtag(self, tag):
        sys.stdout.write('</' + tag + '>')

    def unknown_entityref(self, ref):
        sys.stdout.write('&' + ref + ';')

    def unknown_charref(self, ref):
        sys.stdout.write('&#' + ref + ';')

    def start_scons_example(self, attrs):
        t = [t for t in attrs if t[0] == 'name']
        if t:
            name = t[0][1]
            try:
               e = self.examples[name]
            except KeyError:
               e = self.examples[name] = Example()
        else:
            e = Example()
        for name, value in attrs:
            setattr(e, name, value)
        self.e = e
        self.afunclist.append(e.afunc)

    def end_scons_example(self):
        e = self.e
        files = [f for f in e.files if f.printme]
        if files:
            sys.stdout.write('<programlisting>')
            for f in files:
                if f.printme:
                    i = len(f.data) - 1
                    while f.data[i] == ' ':
                        i = i - 1
                    output = f.data[:i+1].replace('__ROOT__', '')
                    sys.stdout.write(output)
            if e.data and e.data[0] == '\n':
                e.data = e.data[1:]
            sys.stdout.write(e.data + '</programlisting>')
        delattr(self, 'e')
        self.afunclist = self.afunclist[:-1]

    def start_file(self, attrs):
        try:
            e = self.e
        except AttributeError:
            self.error("<file> tag outside of <scons_example>")
        t = [t for t in attrs if t[0] == 'name']
        if not t:
            self.error("no <file> name attribute found")
        try:
            e.prefix
        except AttributeError:
            e.prefix = e.data
            e.data = ""
        f = File(t[0][1])
        f.printme = None
        for name, value in attrs:
            setattr(f, name, value)
        e.files.append(f)
        self.afunclist.append(f.afunc)

    def end_file(self):
        self.e.data = ""
        self.afunclist = self.afunclist[:-1]

    def start_directory(self, attrs):
        try:
            e = self.e
        except AttributeError:
            self.error("<directory> tag outside of <scons_example>")
        t = [t for t in attrs if t[0] == 'name']
        if not t:
            self.error("no <directory> name attribute found")
        try:
            e.prefix
        except AttributeError:
            e.prefix = e.data
            e.data = ""
        d = Directory(t[0][1])
        for name, value in attrs:
            setattr(d, name, value)
        e.dirs.append(d)
        self.afunclist.append(d.afunc)

    def end_directory(self):
        self.e.data = ""
        self.afunclist = self.afunclist[:-1]

    def start_scons_example_file(self, attrs):
        t = [t for t in attrs if t[0] == 'example']
        if not t:
            self.error("no <scons_example_file> example attribute found")
        exname = t[0][1]
        try:
            e = self.examples[exname]
        except KeyError:
            self.error("unknown example name '%s'" % exname)
        fattrs = [t for t in attrs if t[0] == 'name']
        if not fattrs:
            self.error("no <scons_example_file> name attribute found")
        fname = fattrs[0][1]
        f = [f for f in e.files if f.name == fname]
        if not f:
            self.error("example '%s' does not have a file named '%s'" % (exname, fname))
        self.f = f[0]

    def end_scons_example_file(self):
        f = self.f
        sys.stdout.write('<programlisting>')
        i = len(f.data) - 1
        while f.data[i] == ' ':
            i = i - 1
        sys.stdout.write(f.data[:i+1] + '</programlisting>')
        delattr(self, 'f')

    def start_scons_output(self, attrs):
        t = [t for t in attrs if t[0] == 'example']
        if not t:
            self.error("no <scons_output> example attribute found")
        exname = t[0][1]
        try:
            e = self.examples[exname]
        except KeyError:
            self.error("unknown example name '%s'" % exname)
        # Default values for an example.
        o = Output()
        o.os = 'posix'
        o.e = e
        # Locally-set.
        for name, value in attrs:
            setattr(o, name, value)
        self.o = o
        self.afunclist.append(o.afunc)

    def end_scons_output(self):
        o = self.o
        e = o.e
        t = TestCmd.TestCmd(workdir='', combine=1)
        t.subdir('ROOT', 'WORK')
        for d in e.dirs:
            dir = t.workpath('WORK', d.name)
            if not os.path.exists(dir):
                os.makedirs(dir)
        for f in e.files:
            i = 0
            while f.data[i] == '\n':
                i = i + 1
            lines = f.data[i:].split('\n')
            i = 0
            while lines[0][i] == ' ':
                i = i + 1
            lines = [l[i:] for l in lines]
            path = f.name.replace('__ROOT__', t.workpath('ROOT'))
            dir, name = os.path.split(f.name)
            if dir:
                dir = t.workpath('WORK', dir)
                if not os.path.exists(dir):
                    os.makedirs(dir)
            content = '\n'.join(lines)
            content = content.replace('__ROOT__',
                                     t.workpath('ROOT'))
            t.write(t.workpath('WORK', f.name), content)
        i = len(o.prefix)
        while o.prefix[i-1] != '\n':
            i = i - 1
        sys.stdout.write('<literallayout>' + o.prefix[:i])
        p = o.prefix[i:]
        for c in o.commandlist:
            sys.stdout.write(p + Prompt[o.os])
            d = c.data.replace('__ROOT__', '')
            sys.stdout.write('<userinput>' + d + '</userinput>\n')
            e = c.data.replace('__ROOT__', t.workpath('ROOT'))
            args = e.split()[1:]
            os.environ['SCONS_LIB_DIR'] = scons_lib_dir
            t.run(interpreter = sys.executable,
                  program = scons_py,
                  arguments = '-f - ' + ' '.join(args),
                  chdir = t.workpath('WORK'),
                  stdin = Stdin % o.os)
            out = t.stdout().replace(t.workpath('ROOT'), '')
            if out:
                lines = out.split('\n')
                if lines:
                    while lines[-1] == '':
                        lines = lines[:-1]
                    for l in lines:
                        sys.stdout.write(p + l + '\n')
            #err = t.stderr()
            #if err:
            #    sys.stderr.write(err)
        if o.data[0] == '\n':
            o.data = o.data[1:]
        sys.stdout.write(o.data + '</literallayout>')
        delattr(self, 'o')
        self.afunclist = self.afunclist[:-1]

    def start_command(self, attrs):
        try:
            o = self.o
        except AttributeError:
            self.error("<command> tag outside of <scons_output>")
        try:
            o.prefix
        except AttributeError:
            o.prefix = o.data
            o.data = ""
        c = Command()
        o.commandlist.append(c)
        self.afunclist.append(c.afunc)

    def end_command(self):
        self.o.data = ""
        self.afunclist = self.afunclist[:-1]

    def start_sconstruct(self, attrs):
        sys.stdout.write('<programlisting>')

    def end_sconstruct(self):
        sys.stdout.write('</programlisting>')

try:
    file = sys.argv[1]
except IndexError:
    file = '-'

if file == '-':
    f = sys.stdin
else:
    try:
        f = open(file, 'r')
    except IOError, msg:
        print file, ":", msg
        sys.exit(1)

data = f.read()
if f is not sys.stdin:
    f.close()

x = MySGML()
for c in data:
    x.feed(c)
x.close()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
