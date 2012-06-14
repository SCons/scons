#!/usr/bin/env python
#
# Copyright (c) 2010 The SCons Foundation
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
# scons-doc.py -    an SGML preprocessor for capturing SCons output
#                   and inserting it into examples in our DocBook
#                   documentation
#
# Synopsis:
#
#  scons-doc [OPTIONS] [.in files]
#
#   When no input files are given, the folder doc/user/* is searched for .in files.
#
# Available options:
#
#   -d, --diff            create examples for the .in file and output a unified
#                         diff against the related .xml file
#   -r, --run             create examples for the .in file, but do not change
#                         any files
#   -s, --simple_diff     use a simpler output for the diff mode (no unified
#                         diff!)
#   -u, --update          create examples for the .in file and update the
#                         related .xml file
#
# This script looks for some SGML tags that describe SCons example
# configurations and commands to execute in those configurations, and
# uses TestCmd.py to execute the commands and insert the output from
# those commands into the SGML that we output.  This way, we can run a
# script and update all of our example documentation output without
# a lot of laborious by-hand checking.
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
#         <scons_output_command>scons -Q foo</scons_output_command>
#         <scons_output_command>scons -Q foo</scons_output_command>
#       </scons_output>
#
# You tell it which example to use with the "example" attribute, and then
# give it a list of <scons_output_command> tags to execute.  You can also
# supply an "os" tag, which specifies the type of operating system this
# example is intended to show; if you omit this, default value is "posix".
#
# The generated SGML will show the command line (with the appropriate
# command-line prompt for the operating system), execute the command in
# a temporary directory with the example files, capture the standard
# output from SCons, and insert it into the text as appropriate.
# Error output gets passed through to your error output so you
# can see if there are any problems executing the command.
#

import optparse
import os
import re
import sgmllib
import sys
import time
import glob

sys.path.append(os.path.join(os.getcwd(), 'QMTest'))
sys.path.append(os.path.join(os.getcwd(), 'build', 'QMTest'))

scons_py = os.path.join('bootstrap', 'src', 'script', 'scons.py')
if not os.path.exists(scons_py):
    scons_py = os.path.join('src', 'script', 'scons.py')

scons_lib_dir = os.path.join(os.getcwd(), 'bootstrap', 'src', 'engine')
if not os.path.exists(scons_lib_dir):
    scons_lib_dir = os.path.join(os.getcwd(), 'src', 'engine')

os.environ['SCONS_LIB_DIR'] = scons_lib_dir

import TestCmd

# The regular expression that identifies entity references in the
# standard sgmllib omits the underscore from the legal characters.
# Override it with our own regular expression that adds underscore.
sgmllib.entityref = re.compile('&([a-zA-Z][-_.a-zA-Z0-9]*)[^-_a-zA-Z0-9]')

# Classes for collecting different types of data we're interested in.
class DataCollector(object):
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
    def __init__(self):
        DataCollector.__init__(self)
        self.output = None

Prompt = {
    'posix' : '% ',
    'win32' : 'C:\\>'
}

# The magick SCons hackery that makes this work.
#
# So that our examples can still use the default SConstruct file, we
# actually feed the following into SCons via stdin and then have it
# SConscript() the SConstruct file.  This stdin wrapper creates a set
# of ToolSurrogates for the tools for the appropriate platform.  These
# Surrogates print output like the real tools and behave like them
# without actually having to be on the right platform or have the right
# tool installed.
#
# The upshot:  The wrapper transparently changes the world out from
# under the top-level SConstruct file in an example just so we can get
# the command output.

Stdin = """\
import os
import re
import SCons.Action
import SCons.Defaults
import SCons.Node.FS

platform = '%(osname)s'

Sep = {
    'posix' : '/',
    'win32' : '\\\\',
}[platform]


#  Slip our own __str__() method into the EntryProxy class used to expand
#  $TARGET{S} and $SOURCE{S} to translate the path-name separators from
#  what's appropriate for the system we're running on to what's appropriate
#  for the example system.
orig = SCons.Node.FS.EntryProxy
class MyEntryProxy(orig):
    def __str__(self):
        return str(self._subject).replace(os.sep, Sep)
SCons.Node.FS.EntryProxy = MyEntryProxy

# Slip our own RDirs() method into the Node.FS.File class so that the
# expansions of $_{CPPINC,F77INC,LIBDIR}FLAGS will have the path-name
# separators translated from what's appropriate for the system we're
# running on to what's appropriate for the example system.
orig_RDirs = SCons.Node.FS.File.RDirs
def my_RDirs(self, pathlist, orig_RDirs=orig_RDirs):
    return [str(x).replace(os.sep, Sep) for x in orig_RDirs(self, pathlist)]
SCons.Node.FS.File.RDirs = my_RDirs

class Curry(object):
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
        result.append(' '.join(map(str, cmd)))
    return '\\n'.join(result)

class ToolSurrogate(object):
    def __init__(self, tool, variable, func, varlist):
        self.tool = tool
        if not isinstance(variable, list):
            variable = [variable]
        self.variable = variable
        self.func = func
        self.varlist = varlist
    def __call__(self, env):
        t = Tool(self.tool)
        t.generate(env)
        for v in self.variable:
            orig = env[v]
            try:
                strfunction = orig.strfunction
            except AttributeError:
                strfunction = Curry(Str, cmd=orig)
            # Don't call Action() through its global function name, because
            # that leads to infinite recursion in trying to initialize the
            # Default Environment.
            env[v] = SCons.Action.Action(self.func,
                                         strfunction=strfunction,
                                         varlist=self.varlist)
    def __repr__(self):
        # This is for the benefit of printing the 'TOOLS'
        # variable through env.Dump().
        return repr(self.tool)

def Null(target, source, env):
    pass

def Cat(target, source, env):
    target = str(target[0])
    f = open(target, "wb")
    for src in map(str, source):
        f.write(open(src, "rb").read())
    f.close()

def CCCom(target, source, env):
    target = str(target[0])
    fp = open(target, "wb")
    def process(source_file, fp=fp):
        for line in open(source_file, "rb").readlines():
            m = re.match(r'#include\s[<"]([^<"]+)[>"]', line)
            if m:
                include = m.group(1)
                for d in [str(env.Dir('$CPPPATH')), '.']:
                    f = os.path.join(d, include)
                    if os.path.exists(f):
                        process(f)
                        break
            elif line[:11] != "STRIP CCCOM":
                fp.write(line)
    for src in map(str, source):
        process(src)
        fp.write('debug = ' + ARGUMENTS.get('debug', '0') + '\\n')
    fp.close()

public_class_re = re.compile('^public class (\S+)', re.MULTILINE)

def JavaCCom(target, source, env):
    # This is a fake Java compiler that just looks for
    #   public class FooBar
    # lines in the source file(s) and spits those out
    # to .class files named after the class.
    tlist = list(map(str, target))
    not_copied = {}
    for t in tlist:
       not_copied[t] = 1
    for src in map(str, source):
        contents = open(src, "rb").read()
        classes = public_class_re.findall(contents)
        for c in classes:
            for t in [x for x in tlist if x.find(c) != -1]:
                open(t, "wb").write(contents)
                del not_copied[t]
    for t in not_copied.keys():
        open(t, "wb").write("\\n")

def JavaHCom(target, source, env):
    tlist = map(str, target)
    slist = map(str, source)
    for t, s in zip(tlist, slist):
        open(t, "wb").write(open(s, "rb").read())

def JarCom(target, source, env):
    target = str(target[0])
    class_files = []
    for src in map(str, source):
        for dirpath, dirnames, filenames in os.walk(src):
            class_files.extend([ os.path.join(dirpath, f)
                                 for f in filenames if f.endswith('.class') ])
    f = open(target, "wb")
    for cf in class_files:
        f.write(open(cf, "rb").read())
    f.close()

# XXX Adding COLOR, COLORS and PACKAGE to the 'cc' varlist(s) by hand
# here is bogus.  It's for the benefit of doc/user/command-line.in, which
# uses examples that want  to rebuild based on changes to these variables.
# It would be better to figure out a way to do it based on the content of
# the generated command-line, or else find a way to let the example markup
# language in doc/user/command-line.in tell this script what variables to
# add, but that's more difficult than I want to figure out how to do right
# now, so let's just use the simple brute force approach for the moment.

ToolList = {
    'posix' :   [('cc', ['CCCOM', 'SHCCCOM'], CCCom, ['CCFLAGS', 'CPPDEFINES', 'COLOR', 'COLORS', 'PACKAGE']),
                 ('link', ['LINKCOM', 'SHLINKCOM'], Cat, []),
                 ('ar', ['ARCOM', 'RANLIBCOM'], Cat, []),
                 ('tar', 'TARCOM', Null, []),
                 ('zip', 'ZIPCOM', Null, []),
                 ('BitKeeper', 'BITKEEPERCOM', Cat, []),
                 ('CVS', 'CVSCOM', Cat, []),
                 ('RCS', 'RCS_COCOM', Cat, []),
                 ('SCCS', 'SCCSCOM', Cat, []),
                 ('javac', 'JAVACCOM', JavaCCom, []),
                 ('javah', 'JAVAHCOM', JavaHCom, []),
                 ('jar', 'JARCOM', JarCom, []),
                 ('rmic', 'RMICCOM', Cat, []),
                ],
    'win32' :   [('msvc', ['CCCOM', 'SHCCCOM', 'RCCOM'], CCCom, ['CCFLAGS', 'CPPDEFINES', 'COLOR', 'COLORS', 'PACKAGE']),
                 ('mslink', ['LINKCOM', 'SHLINKCOM'], Cat, []),
                 ('mslib', 'ARCOM', Cat, []),
                 ('tar', 'TARCOM', Null, []),
                 ('zip', 'ZIPCOM', Null, []),
                 ('BitKeeper', 'BITKEEPERCOM', Cat, []),
                 ('CVS', 'CVSCOM', Cat, []),
                 ('RCS', 'RCS_COCOM', Cat, []),
                 ('SCCS', 'SCCSCOM', Cat, []),
                 ('javac', 'JAVACCOM', JavaCCom, []),
                 ('javah', 'JAVAHCOM', JavaHCom, []),
                 ('jar', 'JARCOM', JarCom, []),
                 ('rmic', 'RMICCOM', Cat, []),
                ],
}

toollist = ToolList[platform]
filter_tools = '%(tools)s'.split()
if filter_tools:
    toollist = [x for x in toollist if x[0] in filter_tools]

toollist = [ToolSurrogate(*t) for t in toollist]

toollist.append('install')

def surrogate_spawn(sh, escape, cmd, args, env):
    pass

def surrogate_pspawn(sh, escape, cmd, args, env, stdout, stderr):
    pass

SCons.Defaults.ConstructionEnvironment.update({
    'PLATFORM' : platform,
    'TOOLS'    : toollist,
    'SPAWN'    : surrogate_spawn,
    'PSPAWN'   : surrogate_pspawn,
})

SConscript('SConstruct')
"""

# "Commands" that we will execute in our examples.
def command_scons(args, c, test, dict):
    save_vals = {}
    delete_keys = []
    try:
        ce = c.environment
    except AttributeError:
        pass
    else:
        for arg in c.environment.split():
            key, val = arg.split('=')
            try:
                save_vals[key] = os.environ[key]
            except KeyError:
                delete_keys.append(key)
            os.environ[key] = val
    test.run(interpreter = sys.executable,
             program = scons_py,
             # We use ToolSurrogates to capture win32 output by "building"
             # examples using a fake win32 tool chain.  Suppress the
             # warnings that come from the new revamped VS support so
             # we can build doc on (Linux) systems that don't have
             # Visual C installed.
             arguments = '--warn=no-visual-c-missing -f - ' + ' '.join(args),
             chdir = test.workpath('WORK'),
             stdin = Stdin % dict)
    os.environ.update(save_vals)
    for key in delete_keys:
        del(os.environ[key])
    out = test.stdout()
    out = out.replace(test.workpath('ROOT'), '')
    out = out.replace(test.workpath('WORK/SConstruct'),
                              '/home/my/project/SConstruct')
    lines = out.split('\n')
    if lines:
        while lines[-1] == '':
            lines = lines[:-1]
    #err = test.stderr()
    #if err:
    #    sys.stderr.write(err)
    return lines

def command_touch(args, c, test, dict):
    if args[0] == '-t':
        t = int(time.mktime(time.strptime(args[1], '%Y%m%d%H%M')))
        times = (t, t)
        args = args[2:]
    else:
        time.sleep(1)
        times = None
    for file in args:
        if not os.path.isabs(file):
            file = os.path.join(test.workpath('WORK'), file)
        if not os.path.exists(file):
            open(file, 'wb')
        os.utime(file, times)
    return []

def command_edit(args, c, test, dict):
    try:
        add_string = c.edit[:]
    except AttributeError:
        add_string = 'void edit(void) { ; }\n'
    if add_string[-1] != '\n':
        add_string = add_string + '\n'
    for file in args:
        if not os.path.isabs(file):
            file = os.path.join(test.workpath('WORK'), file)
        contents = open(file, 'rb').read()
        open(file, 'wb').write(contents + add_string)
    return []

def command_ls(args, c, test, dict):
    def ls(a):
        return ['  '.join(sorted([x for x in os.listdir(a) if x[0] != '.']))]
    if args:
        l = []
        for a in args:
            l.extend(ls(test.workpath('WORK', a)))
        return l
    else:
        return ls(test.workpath('WORK'))

def command_sleep(args, c, test, dict):
    time.sleep(int(args[0]))

CommandDict = {
    'scons' : command_scons,
    'touch' : command_touch,
    'edit'  : command_edit,
    'ls'    : command_ls,
    'sleep' : command_sleep,
}

def ExecuteCommand(args, c, t, dict):
    try:
        func = CommandDict[args[0]]
    except KeyError:
        func = lambda args, c, t, dict: []
    return func(args[1:], c, t, dict)

class MySGML(sgmllib.SGMLParser):
    """A subclass of the standard Python sgmllib SGML parser.

    This extends the standard sgmllib parser to recognize, and do cool
    stuff with, the added tags that describe our SCons examples,
    commands, and other stuff.
    """
    def __init__(self, outfp):
        sgmllib.SGMLParser.__init__(self)
        self.examples = {}
        self.afunclist = []
        self.outfp = outfp

    # The first set of methods here essentially implement pass-through
    # handling of most of the stuff in an SGML file.  We're really
    # only concerned with the tags specific to SCons example processing,
    # the methods for which get defined below.

    def handle_data(self, data):
        try:
            f = self.afunclist[-1]
        except IndexError:
            self.outfp.write(data)
        else:
            f(data)

    def handle_comment(self, data):
        self.outfp.write('<!--' + data + '-->')

    def handle_decl(self, data):
        self.outfp.write('<!' + data + '>')

    def unknown_starttag(self, tag, attrs):
        try:
            f = self.example.afunc
        except AttributeError:
            f = self.outfp.write
        if not attrs:
            f('<' + tag + '>')
        else:
            f('<' + tag)
            for name, value in attrs:
                f(' ' + name + '=' + '"' + value + '"')
            f('>')

    def unknown_endtag(self, tag):
        self.outfp.write('</' + tag + '>')

    def unknown_entityref(self, ref):
        self.outfp.write('&' + ref + ';')

    def unknown_charref(self, ref):
        self.outfp.write('&#' + ref + ';')

    # Here is where the heavy lifting begins.  The following methods
    # handle the begin-end tags of our SCons examples.

    def for_display(self, contents):
        contents = contents.replace('__ROOT__', '')
        contents = contents.replace('<', '&lt;')
        contents = contents.replace('>', '&gt;')
        return contents

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
            self.outfp.write('<programlisting>')
            for f in files:
                if f.printme:
                    i = len(f.data) - 1
                    while f.data[i] == ' ':
                        i = i - 1
                    output = self.for_display(f.data[:i+1])
                    self.outfp.write(output)
            if e.data and e.data[0] == '\n':
                e.data = e.data[1:]
            self.outfp.write(e.data + '</programlisting>')
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
        self.outfp.write('<programlisting>')
        self.outfp.write(f.data + '</programlisting>')
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
        o.preserve = None
        o.os = 'posix'
        o.tools = ''
        o.e = e
        # Locally-set.
        for name, value in attrs:
            setattr(o, name, value)
        self.o = o
        self.afunclist.append(o.afunc)

    def end_scons_output(self):
        # The real raison d'etre for this script, this is where we
        # actually execute SCons to fetch the output.
        o = self.o
        e = o.e
        t = TestCmd.TestCmd(workdir='', combine=1)
        if o.preserve:
            t.preserve()
        t.subdir('ROOT', 'WORK')
        t.rootpath = t.workpath('ROOT').replace('\\', '\\\\')

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
            path = f.name.replace('__ROOT__', t.rootpath)
            if not os.path.isabs(path):
                path = t.workpath('WORK', path)
            dir, name = os.path.split(path)
            if dir and not os.path.exists(dir):
                os.makedirs(dir)
            content = '\n'.join(lines)
            content = content.replace('__ROOT__', t.rootpath)
            path = t.workpath('WORK', path)
            t.write(path, content)
            if hasattr(f, 'chmod'):
                os.chmod(path, int(f.chmod, 0))

        i = len(o.prefix)
        while o.prefix[i-1] != '\n':
            i = i - 1

        self.outfp.write('<screen>' + o.prefix[:i])
        p = o.prefix[i:]

        # Regular expressions for making the doc output consistent,
        # regardless of reported addresses or Python version.

        # Massage addresses in object repr strings to a constant.
        address_re = re.compile(r' at 0x[0-9a-fA-F]*\>')

        # Massage file names in stack traces (sometimes reported as absolute
        # paths) to a consistent relative path.
        engine_re = re.compile(r' File ".*/src/engine/SCons/')

        # Python 2.5 changed the stack trace when the module is read
        # from standard input from read "... line 7, in ?" to
        # "... line 7, in <module>".
        file_re = re.compile(r'^( *File ".*", line \d+, in) \?$', re.M)

        # Python 2.6 made UserList a new-style class, which changes the
        # AttributeError message generated by our NodeList subclass.
        nodelist_re = re.compile(r'(AttributeError:) NodeList instance (has no attribute \S+)')

        for c in o.commandlist:
            self.outfp.write(p + Prompt[o.os])
            d = c.data.replace('__ROOT__', '')
            self.outfp.write('<userinput>' + d + '</userinput>\n')

            e = c.data.replace('__ROOT__', t.workpath('ROOT'))
            args = e.split()
            lines = ExecuteCommand(args, c, t, {'osname':o.os, 'tools':o.tools})
            content = None
            if c.output:
                content = c.output
            elif lines:
                content = ( '\n' + p).join(lines)
            if content:
                content = address_re.sub(r' at 0x700000&gt;', content)
                content = engine_re.sub(r' File "bootstrap/src/engine/SCons/', content)
                content = file_re.sub(r'\1 <module>', content)
                content = nodelist_re.sub(r"\1 'NodeList' object \2", content)
                content = self.for_display(content)
                self.outfp.write(p + content + '\n')

        if o.data[0] == '\n':
            o.data = o.data[1:]
        self.outfp.write(o.data + '</screen>')
        delattr(self, 'o')
        self.afunclist = self.afunclist[:-1]

    def start_scons_output_command(self, attrs):
        try:
            o = self.o
        except AttributeError:
            self.error("<scons_output_command> tag outside of <scons_output>")
        try:
            o.prefix
        except AttributeError:
            o.prefix = o.data
            o.data = ""
        c = Command()
        for name, value in attrs:
            setattr(c, name, value)
        o.commandlist.append(c)
        self.afunclist.append(c.afunc)

    def end_scons_output_command(self):
        self.o.data = ""
        self.afunclist = self.afunclist[:-1]

    def start_sconstruct(self, attrs):
        f = File('')
        self.f = f
        self.afunclist.append(f.afunc)

    def end_sconstruct(self):
        f = self.f
        self.outfp.write('<programlisting>')
        output = self.for_display(f.data)
        self.outfp.write(output + '</programlisting>')
        delattr(self, 'f')
        self.afunclist = self.afunclist[:-1]

def process(filename, fout=sys.stdout):
    if filename == '-':
        f = sys.stdin
    else:
        try:
            f = open(filename, 'r')
        except EnvironmentError, e:
            sys.stderr.write('%s: %s\n' % (filename, e))
            return 1

    data = f.read()
    if f is not sys.stdin:
        f.close()

    if data.startswith('<?xml '):
        first_line, data = data.split('\n', 1)
        fout.write(first_line + '\n')

    x = MySGML(fout)
    for c in data:
        x.feed(c)
    x.close()

    return 0

def main(argv=None):
    if argv is None:
        argv = sys.argv

    parser = optparse.OptionParser()
    parser.add_option('-d', '--diff',
                  action='store_true', dest='diff', default=False,
                  help='create examples for the .in file and output a unified diff against the related .xml file')
    parser.add_option('-r', '--run',
                  action='store_true', dest='run', default=False,
                  help='create examples for the .in file, but do not change any files')
    parser.add_option('-s', '--simple_diff',
                  action='store_true', dest='simple', default=False,
                  help='use a simpler output for the diff mode (no unified diff!)')
    parser.add_option('-u', '--update',
                  action='store_true', dest='update', default=False,
                  help='create examples for the .in file and update the related .xml file')

    opts, args = parser.parse_args(argv[1:])

    if opts.diff:
        import StringIO
        import difflib
        
        if not args:
            args = glob.glob('doc/user/*.in')
        for arg in sorted(args):
            diff = None
            s = StringIO.StringIO()
            process(arg,s)
            filename = arg[:-2]+'xml'
            try:
                fxml = open(filename, 'r')
                xmlcontent = fxml.read()
                fxml.close()
                if opts.simple:
                    diff = list(difflib.context_diff(xmlcontent.splitlines(),
                                                     s.getvalue().splitlines(),
                                                     fromfile=arg, tofile=filename))
                else:
                    diff = list(difflib.unified_diff(xmlcontent.splitlines(),
                                                     s.getvalue().splitlines(),
                                                     fromfile=arg, tofile=filename, 
                                                     lineterm=''))
            except EnvironmentError, e:
                sys.stderr.write('%s: %s\n' % (filename, e))
                
            s.close()
            if diff:
                print "%s:" % arg
                print '\n'.join(diff)
    elif opts.run:
        if not args:
            args = glob.glob('doc/user/*.in')
        for arg in sorted(args):
            print "%s:" % arg
            process(arg)
    elif opts.update:
        if not args:
            args = glob.glob('doc/user/*.in')
        for arg in sorted(args):
            print "%s:" % arg
            filename = arg[:-2]+'xml'
            try:
                fxml = open(filename, 'w')
                process(arg, fxml)
                fxml.close()
            except EnvironmentError, e:
                sys.stderr.write('%s: %s\n' % (filename, e))
    else:
        if not args:
            args = ['-']
    
        for arg in args:
            process(arg)

if __name__ == "__main__":
    sys.exit(main())

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
