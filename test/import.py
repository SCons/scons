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

import TestSCons

test = TestSCons.TestSCons()

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
env = Environment(platform = '%s')
import SCons.Platform.%s
x = SCons.Platform.%s.generate
""" % (platform, platform, platform))
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

# Intel no top dir warning, 32 bit version.
intel_no_top_dir_32_warning = """
scons: warning: Can't find Intel compiler top dir for version='None', abi='ia32'
File "SConstruct", line 1, in ?
"""

# Intel no top dir warning, 64 bit version.
intel_no_top_dir_64_warning = """
scons: warning: Can't find Intel compiler top dir for version='None', abi='x86_64'
File "SConstruct", line 1, in ?
"""

# Intel no license directory warning
intel_license_warning = """
scons: warning: Intel license dir was not found.  Tried using the INTEL_LICENSE_FILE environment variable (), the registry () and the default path (C:\Program Files\Common Files\Intel\Licenses).  Using the default path as a last resort.
File "SConstruct", line 1, in ?
"""

intel_warnings = [
    intel_license_warning,
    intel_no_top_dir_32_warning,
    intel_no_top_dir_32_warning + intel_license_warning,
    intel_no_top_dir_64_warning,
    intel_no_top_dir_64_warning + intel_license_warning,
]

moc = test.where_is('moc')
if moc:
    import os.path
    qt_err = """
scons: warning: Could not detect qt, using moc executable as a hint (QTDIR=%s)
File "SConstruct", line 1, in ?
""" % os.path.dirname(os.path.dirname(moc))
else:
    qt_err = """
scons: warning: Could not detect qt, using empty QTDIR
File "SConstruct", line 1, in ?
"""

error_output = {
    'icl' : intel_warnings,
    'intelc' : intel_warnings,
    'qt' : [qt_err],
}

# An SConstruct for importing Tool names that have illegal characters
# for Python variable names.
indirect_import = """\
env = Environment(tools = ['%s'])
SCons = __import__('SCons.Tool.%s', globals(), locals(), [])
m = getattr(SCons.Tool, '%s')
x = m.generate
"""

# An SConstruct for importing Tool names "normally."
direct_import = """\
env = Environment(tools = ['%s'])
import SCons.Tool.%s
x = SCons.Tool.%s.generate
"""

failures = []
for tool in tools:
    if tool[0] in '0123456789' or '+' in tool:
        test.write('SConstruct', indirect_import % (tool, tool, tool))
    else:
        test.write('SConstruct', direct_import % (tool, tool, tool))
    test.run(stderr=None)
    stderr = test.stderr()
    if not stderr in [''] + error_output.get(tool, []):
        print "Failed importing '%s', stderr:" % tool
        print stderr
        failures.append(tool)

test.fail_test(len(failures))

test.pass_test()
