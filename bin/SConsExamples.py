# !/usr/bin/env python
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
#
# This script looks for some XML tags that describe SCons example
# configurations and commands to execute in those configurations, and
# uses TestCmd.py to execute the commands and insert the output from
# those commands into the XML that we output.  This way, we can run a
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
#           int main(void) { printf("foo.c\n"); }
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
#         <scons_output_command suffix="1">scons -Q foo</scons_output_command>
#         <scons_output_command suffix="2">scons -Q foo</scons_output_command>
#       </scons_output>
#
# You tell it which example to use with the "example" attribute, and then
# give it a list of <scons_output_command> tags to execute.  You can also
# supply an "os" tag, which specifies the type of operating system this
# example is intended to show; if you omit this, default value is "posix".
#
# The generated XML will show the command line (with the appropriate
# command-line prompt for the operating system), execute the command in
# a temporary directory with the example files, capture the standard
# output from SCons, and insert it into the text as appropriate.
# Error output gets passed through to your error output so you
# can see if there are any problems executing the command.
#

import os
import re
import sys
import time

import SConsDoc
from SConsDoc import tf as stf

#
# The available types for ExampleFile entries
#
FT_FILE = 0  # a physical file (=<file>)
FT_FILEREF = 1  # a reference     (=<scons_example_file>)

class ExampleFile:
    def __init__(self, type_=FT_FILE):
        self.type = type_
        self.name = ''
        self.content = ''
        self.chmod = ''

    def isFileRef(self):
        return self.type == FT_FILEREF

class ExampleFolder:
    def __init__(self):
        self.name = ''
        self.chmod = ''

class ExampleCommand:
    def __init__(self):
        self.edit = None
        self.environment = ''
        self.output = ''
        self.cmd = ''

class ExampleOutput:
    def __init__(self):
        self.name = ''
        self.tools = ''
        self.os = 'posix'
        self.preserve = None
        self.suffix = ''
        self.commands = []

class ExampleInfo:
    def __init__(self):
        self.name = ''
        self.files = []
        self.folders = []
        self.outputs = []

    def getFileContents(self, fname):
        for f in self.files:
            if fname == f.name and not f.isFileRef():
                return f.content

        return ''

def readExampleInfos(fpath, examples):
    """ Add the example infos for the file fpath to the
        global dictionary examples.
    """

    # Create doctree
    t = SConsDoc.SConsDocTree()
    t.parseXmlFile(fpath)

    # Parse scons_examples
    for e in stf.findAll(t.root, "scons_example", SConsDoc.dbxid,
                         t.xpath_context, t.nsmap):
        n = ''
        if stf.hasAttribute(e, 'name'):
            n = stf.getAttribute(e, 'name')
        if n and n not in examples:
            i = ExampleInfo()
            i.name = n
            examples[n] = i

        # Parse file and directory entries
        for f in stf.findAll(e, "file", SConsDoc.dbxid,
                             t.xpath_context, t.nsmap):
            fi = ExampleFile()
            if stf.hasAttribute(f, 'name'):
                fi.name = stf.getAttribute(f, 'name')
            if stf.hasAttribute(f, 'chmod'):
                fi.chmod = stf.getAttribute(f, 'chmod')
            fi.content = stf.getText(f)
            examples[n].files.append(fi)
        for d in stf.findAll(e, "directory", SConsDoc.dbxid,
                             t.xpath_context, t.nsmap):
            di = ExampleFolder()
            if stf.hasAttribute(d, 'name'):
                di.name = stf.getAttribute(d, 'name')
            if stf.hasAttribute(d, 'chmod'):
                di.chmod = stf.getAttribute(d, 'chmod')
            examples[n].folders.append(di)


    # Parse scons_example_files
    for f in stf.findAll(t.root, "scons_example_file", SConsDoc.dbxid,
                         t.xpath_context, t.nsmap):
        if stf.hasAttribute(f, 'example'):
            e = stf.getAttribute(f, 'example')
        else:
            continue
        fi = ExampleFile(FT_FILEREF)
        if stf.hasAttribute(f, 'name'):
            fi.name = stf.getAttribute(f, 'name')
        if stf.hasAttribute(f, 'chmod'):
            fi.chmod = stf.getAttribute(f, 'chmod')
        fi.content = stf.getText(f)
        examples[e].files.append(fi)


    # Parse scons_output
    for o in stf.findAll(t.root, "scons_output", SConsDoc.dbxid,
                         t.xpath_context, t.nsmap):
        if stf.hasAttribute(o, 'example'):
            n = stf.getAttribute(o, 'example')
        else:
            continue

        eout = ExampleOutput()
        if stf.hasAttribute(o, 'name'):
            eout.name = stf.getAttribute(o, 'name')
        if stf.hasAttribute(o, 'tools'):
            eout.tools = stf.getAttribute(o, 'tools')
        if stf.hasAttribute(o, 'os'):
            eout.os = stf.getAttribute(o, 'os')
        if stf.hasAttribute(o, 'suffix'):
            eout.suffix = stf.getAttribute(o, 'suffix')

        for c in stf.findAll(o, "scons_output_command", SConsDoc.dbxid,
                         t.xpath_context, t.nsmap):
            oc = ExampleCommand()
            if stf.hasAttribute(c, 'edit'):
                oc.edit = stf.getAttribute(c, 'edit')
            if stf.hasAttribute(c, 'environment'):
                oc.environment = stf.getAttribute(c, 'environment')
            if stf.hasAttribute(c, 'output'):
                oc.output = stf.getAttribute(c, 'output')
            if stf.hasAttribute(c, 'cmd'):
                oc.cmd = stf.getAttribute(c, 'cmd')
            else:
                oc.cmd = stf.getText(c)

            eout.commands.append(oc)

        examples[n].outputs.append(eout)

def readAllExampleInfos(dpath):
    """ Scan for XML files in the given directory and
        collect together all relevant infos (files/folders,
        output commands) in a map, which gets returned.
    """
    examples = {}
    for path, dirs, files in os.walk(dpath):
        for f in files:
            if f.endswith('.xml'):
                fpath = os.path.join(path, f)
                if SConsDoc.isSConsXml(fpath):
                    readExampleInfos(fpath, examples)

    return examples

generated_examples = os.path.join('doc', 'generated', 'examples')

def ensureExampleOutputsExist(dpath):
    """ Scan for XML files in the given directory and
        ensure that for every example output we have a
        corresponding output file in the 'generated/examples'
        folder.
    """
    # Ensure that the output folder exists
    if not os.path.isdir(generated_examples):
        os.mkdir(generated_examples)

    examples = readAllExampleInfos(dpath)
    for key, value in examples.items():
        # Process all scons_output tags
        for o in value.outputs:
            cpath = os.path.join(generated_examples,
                                 key + '_' + o.suffix + '.xml')
            if not os.path.isfile(cpath):
                # Start new XML file
                s = stf.newXmlTree("screen")
                stf.setText(s, "NO OUTPUT YET! Run the script to generate/update all examples.")
                # Write file
                stf.writeTree(s, cpath)

        # Process all scons_example_file tags
        for r in value.files:
            if r.isFileRef():
                # Get file's content
                content = value.getFileContents(r.name)
                fpath = os.path.join(generated_examples,
                                     key + '_' + r.name.replace("/", "_"))
                # Write file
                with open(fpath, 'w') as f:
                    f.write("%s\n" % content)

perc = "%"

def createAllExampleOutputs(dpath):
    """ Scan for XML files in the given directory and
        creates all output files for every example in
        the 'generated/examples' folder.
    """
    # Ensure that the output folder exists
    if not os.path.isdir(generated_examples):
        os.mkdir(generated_examples)

    examples = readAllExampleInfos(dpath)
    total = len(examples)
    idx = 0

    if len(sys.argv) > 1:
        examples_to_run = sys.argv[1:]
        examples = { k:v for k,v in examples.items() if k in examples_to_run }

    for key, value in examples.items():
        # Process all scons_output tags
        print("%.2f%s (%d/%d) %s" % (float(idx + 1) * 100.0 / float(total),
                                     perc, idx + 1, total, key))

        create_scons_output(value)
        # Process all scons_example_file tags
        for r in value.files:
            if r.isFileRef():
                # Get file's content
                content = value.getFileContents(r.name)
                fpath = os.path.join(generated_examples,
                                     key + '_' + r.name.replace("/", "_"))
                # Write file
                with open(fpath, 'w') as f:
                    f.write("%s\n" % content)
        idx += 1

def collectSConsExampleNames(fpath):
    """ Return a set() of example names, used in the given file fpath.
    """
    names = set()
    suffixes = {}
    failed_suffixes = False

    # Create doctree
    t = SConsDoc.SConsDocTree()
    t.parseXmlFile(fpath)

    # Parse it
    for e in stf.findAll(t.root, "scons_example", SConsDoc.dbxid,
                         t.xpath_context, t.nsmap):
        n = ''
        if stf.hasAttribute(e, 'name'):
            n = stf.getAttribute(e, 'name')
        if n:
            names.add(n)
            if n not in suffixes:
                suffixes[n] = []
        else:
            print("Error: Example in file '%s' is missing a name!" % fpath)
            failed_suffixes = True

    for o in stf.findAll(t.root, "scons_output", SConsDoc.dbxid,
                         t.xpath_context, t.nsmap):
        n = ''
        if stf.hasAttribute(o, 'example'):
            n = stf.getAttribute(o, 'example')
        else:
            print("Error: scons_output in file '%s' is missing an example name!" % fpath)
            failed_suffixes = True

        if n not in suffixes:
            print("Error: scons_output in file '%s' is referencing non-existent example '%s'!" % (fpath, n))
            failed_suffixes = True
            continue

        s = ''
        if stf.hasAttribute(o, 'suffix'):
            s = stf.getAttribute(o, 'suffix')
        else:
            print("Error: scons_output in file '%s' (example '%s') is missing a suffix!" % (fpath, n))
            failed_suffixes = True

        if s not in suffixes[n]:
            suffixes[n].append(s)
        else:
            print("Error: scons_output in file '%s' (example '%s') is using a duplicate suffix '%s'!" % (fpath, n, s))
            failed_suffixes = True

    return names, failed_suffixes

def exampleNamesAreUnique(dpath):
    """ Scan for XML files in the given directory and
        check whether the scons_example names are unique.
    """
    unique = True
    allnames = set()
    for path, dirs, files in os.walk(dpath):
        for f in files:
            if f.endswith('.xml'):
                fpath = os.path.join(path, f)
                if SConsDoc.isSConsXml(fpath):
                    names, failed_suffixes = collectSConsExampleNames(fpath)
                    if failed_suffixes:
                        unique = False
                    i = allnames.intersection(names)
                    if i:
                        print("Not unique in %s are: %s" % (fpath, ', '.join(i)))
                        unique = False

                    allnames |= names

    return unique

# ###############################################################
#
# In the second half of this module (starting here)
# we define the variables and functions that are required
# to actually run the examples, collect their output and
# write it into the files in doc/generated/examples...
# which then get included by our UserGuide.
#
# ###############################################################

sys.path.append(os.path.join(os.getcwd(), 'testing/framework'))
sys.path.append(os.path.join(os.getcwd(), 'build', 'testing/framework'))

scons_py = os.path.join('scripts', 'scons.py')
scons_py = os.path.join(os.getcwd(), scons_py)
scons_lib_dir = os.path.join(os.getcwd(), 'SCons')

os.environ['SCONS_LIB_DIR'] = scons_lib_dir

import TestCmd

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
import shutil

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
        result.append(' '.join(map(str, cmd)))
    return '\\n'.join(result)

class ToolSurrogate:
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
    for src in map(str, source):
        shutil.copy(src, target)

def CCCom(target, source, env):
    def process(source_file, ofp):
        with open(source_file, "r") as ifp:
            for line in ifp.readlines():
                m = re.match(r'#include\s[<"]([^<"]+)[>"]', line)
                if m:
                    include = m.group(1)
                    for d in [str(env.Dir('$CPPPATH')), '.']:
                        f = os.path.join(d, include)
                        if os.path.exists(f):
                            process(f, ofp)
                            break
                elif line[:11] != "STRIP CCCOM":
                    ofp.write(line)

    with open(str(target[0]), "w") as fp:
        for src in map(str, source):
            process(src, fp)
            fp.write('debug = ' + ARGUMENTS.get('debug', '0') + '\\n')

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
        with open(src, "r") as f:
            contents = f.read()
        classes = public_class_re.findall(contents)
        for c in classes:
            for t in [x for x in tlist if x.find(c) != -1]:
                with open(t, "w") as f:
                    f.write(contents)
                del not_copied[t]
    for t in not_copied.keys():
        with open(t, "w") as f:
            f.write("\\n")

def JavaHCom(target, source, env):
    tlist = map(str, target)
    slist = map(str, source)
    for t, s in zip(tlist, slist):
        shutil.copy(s, t)

def JarCom(target, source, env):
    target = str(target[0])
    class_files = []
    for src in map(str, source):
        for dirpath, dirnames, filenames in os.walk(src):
            class_files.extend([ os.path.join(dirpath, f)
                                 for f in filenames if f.endswith('.class') ])
    for cf in class_files:
        shutil.copy(cf, target)

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
def command_scons(args, command, test, values):
    """
    Fake scons command
    """
    save_vals = {}
    delete_keys = []
    try:
        ce = command.environment
    except AttributeError:
        pass
    else:
        for arg in command.environment.split():
            key, val = arg.split('=')
            try:
                save_vals[key] = os.environ[key]
            except KeyError:
                delete_keys.append(key)
            os.environ[key] = val

    test.write(test.workpath('WORK/SConstruct_created'), Stdin % values)

    test.run(interpreter=sys.executable,
             program=scons_py,
             # We use ToolSurrogates to capture win32 output by "building"
             # examples using a fake win32 tool chain.  Suppress the
             # warnings that come from the new revamped VS support so
             # we can build doc on (Linux) systems that don't have
             # Visual C installed.
             arguments='--warn=no-visual-c-missing -f - ' + ' '.join(args),
             chdir=test.workpath('WORK'),
             stdin=Stdin % values)
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
    # err = test.stderr()
    # if err:
    #    sys.stderr.write(err)
    return lines

def command_touch(args, command, test, values):
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
            with open(file, 'w'):
                pass
        os.utime(file, times)
    return []

def command_edit(args, c, test, values):
    if c.edit is None:
        add_string = 'void edit(void) { ; }\n'
    else:
        add_string = c.edit[:]
    if add_string[-1] != '\n':
        add_string = add_string + '\n'
    for file in args:
        if not os.path.isabs(file):
            file = os.path.join(test.workpath('WORK'), file)
        with open(file, 'a') as f:
            f.write(add_string)
    return []

def command_ls(args, c, test, values):
    def ls(a):
        try:
            return ['  '.join(sorted([x for x in os.listdir(a) if x[0] != '.']))]
        except OSError as e:
            # This should never happen. Pop into debugger
            import pdb; pdb.set_trace()
    if args:
        l = []
        for a in args:
            l.extend(ls(test.workpath('WORK', a)))
        return l
    return ls(test.workpath('WORK'))

def command_sleep(args, c, test, values):
    time.sleep(int(args[0]))

CommandDict = {
    'scons' : command_scons,
    'touch' : command_touch,
    'edit'  : command_edit,
    'ls'    : command_ls,
    'sleep' : command_sleep,
}

def ExecuteCommand(args, c, t, values):
    try:
        func = CommandDict[args[0]]
    except KeyError:
        func = lambda args, c, t, values: []
    return func(args[1:], c, t, values)


def create_scons_output(e):
    """
    The real raison d'etre for this script, this is where we
    actually execute SCons to fetch the output.
    """

    # Loop over all outputs for the example
    for o in e.outputs:
        # Create new test directory
        t = TestCmd.TestCmd(workdir='', combine=1)
        if o.preserve:
            t.preserve()
        t.subdir('ROOT', 'WORK')
        t.rootpath = t.workpath('ROOT').replace('\\', '\\\\')

        for d in e.folders:
            dir = t.workpath('WORK', d.name)
            if not os.path.exists(dir):
                os.makedirs(dir)

        for f in e.files:
            if f.isFileRef():
                continue
            #
            # Left-align file's contents, starting on the first
            # non-empty line
            #
            data = f.content.split('\n')
            i = 0
            # Skip empty lines
            while data[i] == '':
                i = i + 1
            lines = data[i:]
            i = 0
            # Scan first line for the number of spaces
            # that this block is indented
            while lines[0][i] == ' ':
                i = i + 1
            # Left-align block
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
                if len(f.chmod):
                    os.chmod(path, int(f.chmod, base=8))

        # Regular expressions for making the doc output consistent,
        # regardless of reported addresses or Python version.

        # Massage addresses in object repr strings to a constant.
        address_re = re.compile(r' at 0x[0-9a-fA-F]*>')

        # Massage file names in stack traces (sometimes reported as absolute
        # paths) to a consistent relative path.
        engine_re = re.compile(r' File ".*/SCons/')

        # Python 2.5 changed the stack trace when the module is read
        # from standard input from read "... line 7, in ?" to
        # "... line 7, in <module>".
        file_re = re.compile(r'^( *File ".*", line \d+, in) \?$', re.M)

        # Python 2.6 made UserList a new-style class, which changes the
        # AttributeError message generated by our NodeList subclass.
        nodelist_re = re.compile(r'(AttributeError:) NodeList instance (has no attribute \S+)')

        # Root element for our subtree
        sroot = stf.newEtreeNode("screen", True)
        curchild = None
        content = ""
        for command in o.commands:
            content += Prompt[o.os]
            if curchild is not None:
                if not command.output:
                    # Append content as tail
                    curchild.tail = content
                    content = "\n"
                    # Add new child for userinput tag
                    curchild = stf.newEtreeNode("userinput")
                    d = command.cmd.replace('__ROOT__', '')
                    curchild.text = d
                    sroot.append(curchild)
                else:
                    content += command.output + '\n'
            else:
                if not command.output:
                    # Add first text to root
                    sroot.text = content
                    content = "\n"
                    # Add new child for userinput tag
                    curchild = stf.newEtreeNode("userinput")
                    d = command.cmd.replace('__ROOT__', '')
                    curchild.text = d
                    sroot.append(curchild)
                else:
                    content += command.output + '\n'
            # Execute command and capture its output
            cmd_work = command.cmd.replace('__ROOT__', t.workpath('ROOT'))
            args = cmd_work.split()
            lines = ExecuteCommand(args, command, t, {'osname':o.os, 'tools':o.tools})
            if not command.output and lines:
                ncontent = '\n'.join(lines)
                ncontent = address_re.sub(r' at 0x700000>', ncontent)
                ncontent = engine_re.sub(r' File "SCons/', ncontent)
                ncontent = file_re.sub(r'\1 <module>', ncontent)
                ncontent = nodelist_re.sub(r"\1 'NodeList' object \2", ncontent)
                ncontent = ncontent.replace('__ROOT__', '')
                content += ncontent + '\n'
        # Add last piece of content
        if len(content):
            if curchild is not None:
                curchild.tail = content
            else:
                sroot.text = content

        # Construct filename
        fpath = os.path.join(generated_examples,
                             e.name + '_' + o.suffix + '.xml')
        # Expand Element tree
        s = stf.decorateWithHeader(stf.convertElementTree(sroot)[0])
        # Write it to file
        stf.writeTree(s, fpath)


# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
