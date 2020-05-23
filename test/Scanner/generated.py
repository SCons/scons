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

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

"""
Verify that we only scan generated .h files once.

This originated as a real-life bug report submitted by Scott Lystig
Fritchie.  It's been left as-is, rather than stripped down to bare
minimum, partly because it wasn't completely clear what combination of
factors triggered the bug Scott saw, and partly because the real-world
complexity is valuable in its own right.
"""

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.subdir('reftree',
            ['reftree', 'include'],
            'src',
            ['src', 'lib_geng'])

test.write('SConstruct', """\
###
### QQQ !@#$!@#$!  I need to move the SConstruct file to be "above"
### both the source and install dirs, or the install dependencies
### don't seem to work well!  ARRGH!!!!
###

experimenttop = r"%s"
import os
import Mylib

BStaticLibMerge = Builder(generator = Mylib.Gen_StaticLibMerge)
builders = Environment().Dictionary('BUILDERS')
builders["StaticLibMerge"] = BStaticLibMerge

env = Environment(BUILDERS = builders)
e = env.Dictionary()    # Slightly easier to type

global_env = env
e["GlobalEnv"] = global_env

e["REF_INCLUDE"] = os.path.join(experimenttop, "reftree", "include")
e["REF_LIB"] = os.path.join(experimenttop, "reftree", "lib")
e["EXPORT_INCLUDE"] = os.path.join(experimenttop, "export", "include")
e["EXPORT_LIB"] = os.path.join(experimenttop, "export", "lib")
e["INSTALL_BIN"] = os.path.join(experimenttop, "install", "bin")

variant_dir = os.path.join(experimenttop, "tmp-bld-dir")
src_dir = os.path.join(experimenttop, "src")

env.Append(CPPPATH = [e["EXPORT_INCLUDE"]])
env.Append(CPPPATH = [e["REF_INCLUDE"]])
Mylib.AddLibDirs(env, "/via/Mylib.AddLibPath")
env.Append(LIBPATH = [e["EXPORT_LIB"]])
env.Append(LIBPATH = [e["REF_LIB"]])

Mylib.Subdirs(env, "src")
""" % test.workpath())

test.write('Mylib.py', """\
import os
import re

def Subdirs(env, dirlist):
    for file in _subconf_list(dirlist):
        env.SConscript(file, "env")

def _subconf_list(dirlist):
    return [os.path.join(x, "SConscript") for x in dirlist.split()]

def StaticLibMergeMembers(local_env, libname, hackpath, files):
    for file in files.split():
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
    env.StaticLibrary(target, source.split())

def SharedLibrary(env, target, source):
    env.SharedLibrary(target, source.split())

def ExportHeader(env, headers):
    env.Install(dir = env["EXPORT_INCLUDE"], source = headers.split())

def ExportLib(env, libs):
    env.Install(dir = env["EXPORT_LIB"], source = libs.split())

def InstallBin(env, bins):
    env.Install(dir = env["INSTALL_BIN"], source = bins.split())

def Program(env, target, source):
    env.Program(target, source.split())

def AddCFlags(env, str):
    env.Append(CPPFLAGS = " " + str)

# QQQ Synonym needed?
#def AddCFLAGS(env, str):
#    AddCFlags(env, str)

def AddIncludeDirs(env, str):
    env.Append(CPPPATH = str.split())

def AddLibs(env, str):
    env.Append(LIBS = str.split())

def AddLibDirs(env, str):
    env.Append(LIBPATH = str.split())

""")

test.write(['reftree', 'include', 'lib_a.h'], """\
char *a_letter(void);
""")

test.write(['reftree', 'include', 'lib_b.h'], """\
char *b_letter(void);
""")

test.write(['reftree', 'include', 'lib_ja.h'], """\
char *j_letter_a(void);
""")

test.write(['reftree', 'include', 'lib_jb.h.intentionally-moved'], """\
char *j_letter_b(void);
""")

test.write(['src', 'SConscript'], """\
# --- Begin SConscript boilerplate ---
import Mylib
Import("env")

#env = env.Clone()    # Yes, clobber intentionally
#Make environment changes, such as: Mylib.AddCFlags(env, "-g -D_TEST")
#Mylib.Subdirs(env, "lib_a lib_b lib_mergej prog_x")
Mylib.Subdirs(env, "lib_geng")

env = env.Clone()    # Yes, clobber intentionally
# --- End SConscript boilerplate ---

""")

test.write(['src', 'lib_geng', 'SConscript'], r"""
# --- Begin SConscript boilerplate ---
import sys
import Mylib
Import("env")

#env = env.Clone()    # Yes, clobber intentionally
#Make environment changes, such as: Mylib.AddCFlags(env, "-g -D_TEST")
#Mylib.Subdirs(env, "foo_dir")

env = env.Clone()    # Yes, clobber intentionally
# --- End SConscript boilerplate ---

Mylib.AddCFlags(env, "-DGOOFY_DEMO")
Mylib.AddIncludeDirs(env, ".")

# Not part of Scott Lystig Fritchies's original stuff:
# On Windows, it's import to use the original test environment
# when we invoke SCons recursively.
import os
recurse_env = env.Clone()
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
        # exception, which SCons would turn into a UserError.  They're
        # not important for this test, so just catch 'em.
        f = fromdict[k]
        try:
             todict[k] = env.subst(f)
        except SCons.Errors.UserError:
             pass
todict["CFLAGS"] = fromdict["CPPFLAGS"] + " " + \
    ' '.join(["-I" + x for x in env["CPPPATH"]]) + " " + \
    ' '.join(["-L" + x for x in env["LIBPATH"]])
todict["CXXFLAGS"] = todict["CFLAGS"]

generated_hdrs = "libg_gx.h libg_gy.h libg_gz.h"
static_hdrs = "libg_w.h"
#exported_hdrs = generated_hdrs + " " + static_hdrs
exported_hdrs = static_hdrs
lib_name = "g"
lib_fullname = env.subst("${LIBPREFIX}g${LIBSUFFIX}")
lib_srcs = "libg_1.c libg_2.c libg_3.c".split()
import re
lib_objs = [re.sub(r"\.c$", ".o", x) for x in lib_srcs]

Mylib.ExportHeader(env, exported_hdrs)
Mylib.ExportLib(env, lib_fullname)

# The following were the original commands from Scott Lystic Fritchie,
# making use of a shell script and a Makefile to build the library.
# These have been preserved, commented out below, but in order to make
# this test portable, we've replaced them with a Python script and a
# recursive invocation of SCons (!).
#cmd_both = "cd %s ; make generated ; make" % Dir(".")
#cmd_generated = "cd %s ; sh MAKE-HEADER.sh" % Dir(".")
#cmd_justlib = "cd %s ; make" % Dir(".")

_ws = re.compile(r'\s')

def escape(s):
    if _ws.search(s):
        s = '"' + s + '"'
    return s

cmd_generated = "%s $SOURCE" % escape(sys.executable)
cmd_justlib = "%s %s -C ${SOURCES[0].dir}" % (escape(sys.executable),
                                              escape(sys.argv[0]))

##### Deps appear correct ... but wacky scanning?
# Why?
#
# SCons bug??

env.Command(generated_hdrs.split(),
            ["MAKE-HEADER.py"],
            cmd_generated)
recurse_env.Command([lib_fullname] + lib_objs,
                    lib_srcs + (generated_hdrs + " " + static_hdrs).split(),
                    cmd_justlib)
""")

test.write(['src', 'lib_geng', 'MAKE-HEADER.py'], """\
#!%(_python_)s

import os
import os.path
import sys

# chdir to the directory in which this script lives
os.chdir(os.path.split(sys.argv[0])[0])

for h in ['libg_gx.h', 'libg_gy.h', 'libg_gz.h']:
    with open(h, 'w') as f:
        f.write('')
""" % locals())

test.write(['src', 'lib_geng', 'SConstruct'], """\
import os

Scanned = {}

def write_out(fname, dict):
    with open(fname, 'w') as f:
        for k in sorted(dict.keys()):
            name = os.path.split(k)[1]
            f.write(name + ": " + str(dict[k]) + "\\n")

# A hand-coded new-style class proxy to wrap the underlying C Scanner
# with a method that counts the calls.
#
# This is more complicated than it used to be with old-style classes
# because the .__*__() methods in new-style classes are not looked
# up on the instance, but resolve to the actual wrapped class methods,
# so we have to handle those directly.
class CScannerCounter:
    def __init__(self, original_CScanner, *args, **kw):
        self.original_CScanner = original_CScanner
    def __eq__(self, *args, **kw):
        return self.original_CScanner.__eq__(*args, **kw)
    def __hash__(self, *args, **kw):
        return self.original_CScanner.__hash__(*args, **kw)
    def __str__(self, *args, **kw):
        return self.original_CScanner.__str__(*args, **kw)
    def __getattr__(self, *args, **kw):
        return self.original_CScanner.__getattribute__(*args, **kw)
    def __call__(self, node, *args, **kw):
        global Scanned
        n = str(node)
        try:
            Scanned[n] = Scanned[n] + 1
        except KeyError:
            Scanned[n] = 1
        write_out(r'%s', Scanned)
        return self.original_CScanner(node, *args, **kw)

import SCons.Tool
MyCScanner = CScannerCounter(SCons.Script.CScanner)
SCons.Tool.SourceFileScanner.add_scanner('.c', MyCScanner)
SCons.Tool.SourceFileScanner.add_scanner('.h', MyCScanner)

env = Environment(CPPPATH = ".")
l = env.StaticLibrary("g", Split("libg_1.c libg_2.c libg_3.c"))
Default(l)
""" % test.workpath('MyCScan.out'))

# These were the original shell script and Makefile from SLF's original
# bug report.  We're not using them--in order to make this script as
# portable as possible, we're using a Python script and a recursive
# invocation of SCons--but we're preserving them here for history.
#test.write(['src', 'lib_geng', 'MAKE-HEADER.sh'], """\
##!/bin/sh
#
#exec touch $*
#""")
#
#test.write(['src', 'lib_geng', 'Makefile'], """\
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

test.write(['src', 'lib_geng', 'libg_w.h'], """\
""")

test.write(['src', 'lib_geng', 'libg_1.c'], """\
#include <libg_w.h>
#include <libg_gx.h>

int g_1()
{
    return 1;
}
""")

test.write(['src', 'lib_geng', 'libg_2.c'], """\
#include <libg_w.h>
#include <libg_gx.h>
#include <libg_gy.h>
#include <libg_gz.h>

int g_2()
{
        return 2;
}
""")

test.write(['src', 'lib_geng', 'libg_3.c'], """\
#include <libg_w.h>
#include <libg_gx.h>

int g_3()
{
    return 3;
}
""")

test.run(stderr=TestSCons.noisy_ar,
         match=TestSCons.match_re_dotall)

# Note that the generated .h files still get scanned twice,
# but that's really once each as a child of libg_1.o and libg_2.o.
#
# TODO(sgk):  can the duplication be eliminated safely?  Batch build
# support "eliminated" the duplication before in a way that broke a
# use case that ended up in test/Depends/no-Builder.py (issue 2647).

test.must_match("MyCScan.out", """\
libg_1.c: 1
libg_2.c: 1
libg_3.c: 1
libg_gx.h: 2
libg_gy.h: 1
libg_gz.h: 1
libg_w.h: 2
""", mode='r')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
