#!/usr/bin/env python
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

"""
This test verifies that Scanners are called just once.

This is actually a shotgun marriage of two separate tests, the simple
test originally created for this, plus a more complicated test based
on a real-life bug report submitted by Scott Lystig Fritchie.  Both
have value: the simple test will be easier to debug if there are basic
scanning problems, while Scott's test has a lot of cool real-world
complexity that is valuable in its own right, including scanning of
generated .h files.

"""

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import os.path
import sys

import TestCmd
import TestSCons

test = TestSCons.TestSCons(match=TestSCons.match_re_dotall)

test.subdir('simple',
            'SLF',
            ['SLF', 'reftree'], ['SLF', 'reftree', 'include'],
            ['SLF', 'src'], ['SLF', 'src', 'lib_geng'])

test.write('SConstruct', """\
SConscript('simple/SConscript')
SConscript('SLF/SConscript')
""")

test.write(['simple', 'SConscript'], r"""
import os.path

def scan(node, env, envkey, arg):
    print 'XScanner: node =', os.path.split(str(node))[1]
    return []

def exists_check(node, env):
    return os.path.exists(str(node))

XScanner = Scanner(name = 'XScanner',
                   function = scan,
                   argument = None,
                   scan_check = exists_check,
		   skeys = ['.x'])

def echo(env, target, source):
    t = os.path.split(str(target[0]))[1]
    s = os.path.split(str(source[0]))[1]
    print 'create %s from %s' % (t, s)

Echo = Builder(action = Action(echo, None),
               src_suffix = '.x',
	       suffix = '.x')

env = Environment(BUILDERS = {'Echo':Echo}, SCANNERS = [XScanner])

f1 = env.Echo(source=['file1'], target=['file2'])
f2 = env.Echo(source=['file2'], target=['file3'])
f3 = env.Echo(source=['file3'], target=['file4'])
""")

test.write(['simple', 'file1.x'], 'simple/file1.x\n')

test.write(['SLF', 'SConscript'], """\
###
### QQQ !@#$!@#$!  I need to move the SConstruct file to be "above"
### both the source and install dirs, or the install dependencies
### don't seem to work well!  ARRGH!!!!
###

experimenttop = "%s"

import os
import os.path
import string
import Mylib

BStaticLibMerge = Builder(generator = Mylib.Gen_StaticLibMerge)
builders = Environment().Dictionary('BUILDERS')
builders["StaticLibMerge"] = BStaticLibMerge

env = Environment(BUILDERS = builders)
e = env.Dictionary()	# Slightly easier to type

global_env = env
e["GlobalEnv"] = global_env

e["REF_INCLUDE"] = os.path.join(experimenttop, "reftree", "include")
e["REF_LIB"] = os.path.join(experimenttop, "reftree", "lib")
e["EXPORT_INCLUDE"] = os.path.join(experimenttop, "export", "include")
e["EXPORT_LIB"] = os.path.join(experimenttop, "export", "lib")
e["INSTALL_BIN"] = os.path.join(experimenttop, "install", "bin")

build_dir = os.path.join(experimenttop, "tmp-bld-dir")
src_dir = os.path.join(experimenttop, "src")

env.Append(CPPPATH = [e["EXPORT_INCLUDE"]])
env.Append(CPPPATH = [e["REF_INCLUDE"]])
Mylib.AddLibDirs(env, "/via/Mylib.AddLibPath")
env.Append(LIBPATH = [e["EXPORT_LIB"]])
env.Append(LIBPATH = [e["REF_LIB"]])

Mylib.Subdirs(env, "src")
""" % test.workpath('SLF'))

test.write(['SLF', 'Mylib.py'], """\
import os
import string
import re

def Subdirs(env, dirlist):
    for file in _subconf_list(dirlist):
        env.SConscript(file, "env")

def _subconf_list(dirlist):
    return map(lambda x: os.path.join(x, "SConscript"), string.split(dirlist))

def StaticLibMergeMembers(local_env, libname, hackpath, files):
    for file in string.split(files):
        # QQQ Fix limits in grok'ed regexp
        tmp = re.sub(".c$", ".o", file)
        objname = re.sub(".cpp", ".o", tmp)
        local_env.Object(target = objname, source = file)
        e = 'local_env["GlobalEnv"].Append(%s = ["%s"])' % (libname, os.path.join(hackpath, objname))
        exec(e)

def CreateMergedStaticLibrary(env, libname):
    objpaths = env["GlobalEnv"][libname]
    libname = "lib%s.a" % (libname)
    env.StaticLibMerge(target = libname, source = objpaths)

# I put the main body of the generator code here to avoid
# namespace problems
def Gen_StaticLibMerge(source, target, env, for_signature):
    target_string = ""
    for t in target:
        target_string = str(t)
    subdir = os.path.dirname(target_string)
    srclist = []
    for src in source:
        srclist.append(src)
    return [["ar", "cq"] + target + srclist, ["ranlib"] + target]

def StaticLibrary(env, target, source):
    env.StaticLibrary(target, string.split(source))

def SharedLibrary(env, target, source):
    env.SharedLibrary(target, string.split(source))

def ExportHeader(env, headers):
    env.Install(dir = env["EXPORT_INCLUDE"], source = string.split(headers))

def ExportLib(env, libs):
    env.Install(dir = env["EXPORT_LIB"], source = string.split(libs))

def InstallBin(env, bins):
    env.Install(dir = env["INSTALL_BIN"], source = string.split(bins))

def Program(env, target, source):
    env.Program(target, string.split(source))

def AddCFlags(env, str):
    env.Append(CPPFLAGS = " " + str)

# QQQ Synonym needed?
#def AddCFLAGS(env, str):
#    AddCFlags(env, str)

def AddIncludeDirs(env, str):
    env.Append(CPPPATH = string.split(str))

def AddLibs(env, str):
    env.Append(LIBS = string.split(str))

def AddLibDirs(env, str):
    env.Append(LIBPATH = string.split(str))

""")

test.write(['SLF', 'reftree', 'include', 'lib_a.h'], """\
char *a_letter(void);
""")

test.write(['SLF', 'reftree', 'include', 'lib_b.h'], """\
char *b_letter(void);
""")

test.write(['SLF', 'reftree', 'include', 'lib_ja.h'], """\
char *j_letter_a(void);
""")

test.write(['SLF', 'reftree', 'include', 'lib_jb.h.intentionally-moved'], """\
char *j_letter_b(void);
""")

test.write(['SLF', 'src', 'SConscript'], """\
# --- Begin SConscript boilerplate ---
import Mylib
Import("env")

#env = env.Copy()    # Yes, clobber intentionally
#Make environment changes, such as: Mylib.AddCFlags(env, "-g -D_TEST")
#Mylib.Subdirs(env, "lib_a lib_b lib_mergej prog_x")
Mylib.Subdirs(env, "lib_geng")

env = env.Copy()    # Yes, clobber intentionally
# --- End SConscript boilerplate ---

""")

test.write(['SLF', 'src', 'lib_geng', 'SConscript'], """\
# --- Begin SConscript boilerplate ---
import string
import sys
import Mylib
Import("env")

#env = env.Copy()    # Yes, clobber intentionally
#Make environment changes, such as: Mylib.AddCFlags(env, "-g -D_TEST")
#Mylib.Subdirs(env, "foo_dir")

env = env.Copy()    # Yes, clobber intentionally
# --- End SConscript boilerplate ---

Mylib.AddCFlags(env, "-DGOOFY_DEMO")
Mylib.AddIncludeDirs(env, ".")

# Not part of SLF's original stuff: On Win32, it's import to use the
# original test environment when we invoke SCons recursively.
import os
recurse_env = env.Copy()
recurse_env["ENV"] = os.environ

# Icky code to set up process environment for "make"
# I really ought to drop this into Mylib....

fromdict = env.Dictionary()
todict = env["ENV"]
import SCons.Util
import re
for k in fromdict.keys():
    if k != "ENV" and k != "SCANNERS" and k != "CFLAGS" and k != "CXXFLAGS" \
    and not SCons.Util.is_Dict(fromdict[k]):
        # The next line can fail on some systems because it would try to
        # do env.subst on:
        #       $RMIC $RMICFLAGS -d ${TARGET.attributes.java_lookupdir} ...
        # When $TARGET is None, so $TARGET.attributes would throw an
        # exception.
        f = fromdict[k]
        if SCons.Util.is_String(f) and string.find(f, "TARGET") == -1:
             todict[k] = env.subst(f)
todict["CFLAGS"] = fromdict["CPPFLAGS"] + " " + \
    string.join(map(lambda x: "-I" + x, env["CPPPATH"])) + " " + \
    string.join(map(lambda x: "-L" + x, env["LIBPATH"])) 
todict["CXXFLAGS"] = todict["CFLAGS"]

generated_hdrs = "libg_gx.h libg_gy.h libg_gz.h"
static_hdrs = "libg_w.h"
#exported_hdrs = generated_hdrs + " " + static_hdrs
exported_hdrs = static_hdrs
lib_name = "g"
lib_fullname = "libg.a"
lib_srcs = string.split("libg_1.c libg_2.c libg_3.c")
import re
lib_objs = map(lambda x: re.sub("\.c$", ".o", x), lib_srcs)

Mylib.ExportHeader(env, exported_hdrs)
Mylib.ExportLib(env, lib_fullname)

# The following were the original commands from SLF, making use of
# a shell script and a Makefile to build the library.  These have
# been preserved, commented out below, but in order to make this
# test portable, we've replaced them with a Python script and a
# recursive invocation of SCons (!).
#cmd_both = "cd %s ; make generated ; make" % Dir(".")
#cmd_generated = "cd %s ; sh MAKE-HEADER.sh" % Dir(".")
#cmd_justlib = "cd %s ; make" % Dir(".")

_ws = re.compile('\s')

def escape(s):
    if _ws.search(s):
        s = '"' + s + '"'
    return s

cmd_generated = "%s $SOURCE" % (escape(sys.executable),)
cmd_justlib = "%s %s -C ${SOURCES[0].dir}" % ((sys.executable),
                                              escape(sys.argv[0]))

##### Deps appear correct ... but wacky scanning?
# Why?
#
# SCons bug??

env.Command(string.split(generated_hdrs),
            ["MAKE-HEADER.py"],
            cmd_generated)
recurse_env.Command([lib_fullname] + lib_objs,
                    lib_srcs + string.split(generated_hdrs + " " + static_hdrs),
                    cmd_justlib) 
""")

test.write(['SLF', 'src', 'lib_geng', 'MAKE-HEADER.py'], """\
#!/usr/bin/env python

import os
import os.path
import sys

# chdir to the directory in which this script lives
os.chdir(os.path.split(sys.argv[0])[0])

for h in ['libg_gx.h', 'libg_gy.h', 'libg_gz.h']:
    open(h, 'w').write('')
""")

test.write(['SLF', 'src', 'lib_geng', 'SConstruct'], """\
import os

Scanned = {}

def write_out(file, dict):
    keys = dict.keys()
    keys.sort()
    f = open(file, 'wb')
    for k in keys:
        file = os.path.split(k)[1]
        f.write(file + ": " + str(dict[k]) + "\\n")
    f.close()

orig_function = CScan.function

def MyCScan(node, env, target, orig_function=orig_function):
    deps = orig_function(node, env, target)

    global Scanned
    n = str(node)
    try:
        Scanned[n] = Scanned[n] + 1
    except KeyError:
        Scanned[n] = 1
    write_out(r'%s', Scanned)

    return deps

CScan.function = MyCScan

env = Environment(CPPPATH = ".")
l = env.StaticLibrary("g", Split("libg_1.c libg_2.c libg_3.c"))
Default(l)
""" % test.workpath('MyCScan.out'))

# These were the original shell script and Makefile from SLF's original
# bug report.  We're not using them--in order to make this script as
# portable as possible, we're using a Python script and a recursive
# invocation of SCons--but we're preserving them here for history.
#test.write(['SLF', 'src', 'lib_geng', 'MAKE-HEADER.sh'], """\
##!/bin/sh
#
#exec touch $*
#""")
#
#test.write(['SLF', 'src', 'lib_geng', 'Makefile'], """\
#all: libg.a
#
#GEN_HDRS = libg_gx.h libg_gy.h libg_gz.h
#STATIC_HDRS = libg_w.h
#
#$(GEN_HDRS): generated
#
#generated: MAKE-HEADER.sh
#	sh ./MAKE-HEADER.sh $(GEN_HDRS)
#
#libg.a: libg_1.o libg_2.o libg_3.o
#	ar r libg.a libg_1.o libg_2.o libg_3.o
#
#libg_1.c: $(STATIC_HDRS) $(GEN_HDRS)
#libg_2.c: $(STATIC_HDRS) $(GEN_HDRS)
#libg_3.c: $(STATIC_HDRS) $(GEN_HDRS)
#
#clean:
#	-rm -f $(GEN_HDRS)
#	-rm -f libg.a *.o core core.*
#""")

test.write(['SLF', 'src', 'lib_geng', 'libg_w.h'], """\
""")

test.write(['SLF', 'src', 'lib_geng', 'libg_1.c'], """\
#include <libg_w.h>
#include <libg_gx.h>

int g_1()
{
    return 1;
}
""")

test.write(['SLF', 'src', 'lib_geng', 'libg_2.c'], """\
#include <libg_w.h>
#include <libg_gx.h> 
#include <libg_gy.h>
#include <libg_gz.h>

int g_2()
{
        return 2;
}
""")

test.write(['SLF', 'src', 'lib_geng', 'libg_3.c'], """\
#include <libg_w.h>
#include <libg_gx.h>

int g_3()
{
    return 3;
}
""")

test.run(arguments = 'simple',
         stdout = test.wrap_stdout("""\
XScanner: node = file1.x
create file2.x from file1.x
create file3.x from file2.x
create file4.x from file3.x
"""))

test.write(['simple', 'file2.x'], 'simple/file2.x\n')

test.run(arguments = 'simple',
         stdout = test.wrap_stdout("""\
XScanner: node = file1.x
XScanner: node = file2.x
create file3.x from file2.x
create file4.x from file3.x
"""))

test.write(['simple', 'file3.x'], 'simple/file3.x\n')

test.run(arguments = 'simple',
         stdout = test.wrap_stdout("""\
XScanner: node = file1.x
XScanner: node = file2.x
XScanner: node = file3.x
create file4.x from file3.x
"""))

test.run(arguments = 'SLF', stderr=TestSCons.noisy_ar)

# XXX Note that the generated .h files still get scanned twice,
# once before they're generated and once after.  That's the
# next thing to fix here.
test.fail_test(test.read("MyCScan.out", "rb") != """\
libg_1.c: 1
libg_2.c: 1
libg_3.c: 1
libg_gx.h: 1
libg_gy.h: 1
libg_gz.h: 1
libg_w.h: 1
""")

test.pass_test()
