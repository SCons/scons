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
Verify that we can import and use the contents of Platform and Tool
modules directly.
"""

import re
import sys

import TestSCons

test = TestSCons.TestSCons()

SConstruct_path = test.workpath('SConstruct')

platforms = [
    'aix',
    'cygwin',
    'darwin',
    'hpux',
    'irix',
    'os2',
    'posix',
    'sunos',
    'win32'
]

for platform in platforms:
    test.write('SConstruct', """
print "Platform %(platform)s"
env = Environment(platform = '%(platform)s')
import SCons.Platform.%(platform)s
x = SCons.Platform.%(platform)s.generate
""" % locals())
    test.run()

tools = [
    # Can't import '386asm' everywhere due to Windows registry dependency.
    'aixc++',
    'aixcc',
    'aixf77',
    'aixlink',
    'applelink',
    'ar',
    'as',
    'bcc32',
    'BitKeeper',
    'c++',
    'cc',
    'cvf',
    'CVS',
    'default',
    'dmd',
    'dvi',
    'dvipdf',
    'dvips',
    'f77',
    'f90',
    'f95',
    'fortran',
    'g++',
    'g77',
    'gas',
    'gcc',
    'gnulink',
    'gs',
    'hpc++',
    'hpcc',
    'hplink',
    'icc',
    'icl',
    'ifort',
    'ifl',
    'ilink',
    'ilink32',
    'intelc',
    'jar',
    'javac',
    'javah',
    'latex',
    'lex',
    'link',
    # Can't import 'linkloc' everywhere due to Windows registry dependency.
    'm4',
    'masm',
    'midl',
    'mingw',
    'mslib',
    'mslink',
    'msvc',
    'msvs',
    'mwcc',
    'mwld',
    'nasm',
    'pdf',
    'pdflatex',
    'pdftex',
    'Perforce',
    'qt',
    'RCS',
    'rmic',
    'rpcgen',
    'SCCS',
    'sgiar',
    'sgic++',
    'sgicc',
    'sgilink',
    'Subversion',
    'sunar',
    'sunc++',
    'suncc',
    'sunlink',
    'swig',
    'tar',
    'tex',
    'tlib',
    'yacc',
    'zip',
]

#if sys.platform == 'win32':
# Just comment out (for now?) due to registry dependency.
#    tools.extend([
#        '386asm',
#        'linkloc',
#    ])

# Intel no compiler warning..
intel_no_compiler_warning = """
scons: warning: Failed to find Intel compiler for version='None', abi='[^']*'
""" + TestSCons.file_expr

# Intel no top dir warning.
intel_no_top_dir_warning = """
scons: warning: Can't find Intel compiler top dir for version='None', abi='[^']*'
""" + TestSCons.file_expr

# Intel no license directory warning
intel_license_warning = re.escape("""
scons: warning: Intel license dir was not found.  Tried using the INTEL_LICENSE_FILE environment variable (), the registry () and the default path (C:\Program Files\Common Files\Intel\Licenses).  Using the default path as a last resort.
""") + TestSCons.file_expr

intel_warnings = [
    re.compile(intel_license_warning),
    re.compile(intel_no_compiler_warning),
    re.compile(intel_no_compiler_warning + intel_license_warning),
    re.compile(intel_no_top_dir_warning),
    re.compile(intel_no_top_dir_warning + intel_license_warning),
]

moc = test.where_is('moc')
if moc:
    import os.path

    qtdir = os.path.dirname(os.path.dirname(moc))

    qt_err = """
scons: warning: Could not detect qt, using moc executable as a hint (QTDIR=%(qtdir)s)
""" % locals()

else:

    qt_err = """
scons: warning: Could not detect qt, using empty QTDIR
"""

qt_warnings = [ re.compile(qt_err + TestSCons.file_expr) ]

error_output = {
    'icl' : intel_warnings,
    'intelc' : intel_warnings,
    'qt' : qt_warnings,
}

# An SConstruct for importing Tool names that have illegal characters
# for Python variable names.
indirect_import = """\
print "Tool %(tool)s (indirect)"
env = Environment(tools = ['%(tool)s'])

SCons = __import__('SCons.Tool.%(tool)s', globals(), locals(), [])
m = getattr(SCons.Tool, '%(tool)s')
env = Environment()
m.generate(env)
"""

# An SConstruct for importing Tool names "normally."
direct_import = """\
print "Tool %(tool)s (direct)"
env = Environment(tools = ['%(tool)s'])

import SCons.Tool.%(tool)s
env = Environment()
SCons.Tool.%(tool)s.generate(env)
"""

failures = []
for tool in tools:
    if tool[0] in '0123456789' or '+' in tool:
        test.write('SConstruct', indirect_import % locals())
    else:
        test.write('SConstruct', direct_import % locals())
    test.run(stderr=None)
    stderr = test.stderr()
    if stderr:
        matched = None
        for expression in error_output.get(tool, []):
            if expression.match(stderr):
                matched = 1
                break
        if not matched:
            print "Failed importing '%s', stderr:" % tool
            print stderr
            failures.append(tool)

test.fail_test(len(failures))

test.pass_test()
