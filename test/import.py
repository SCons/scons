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

platforms = ['cygwin', 'irix', 'os2', 'posix', 'win32']

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
    'ar',
    'as',
    'bcc32',
    'BitKeeper',
    'c++',
    'cc',
    'CVS',
    'default',
    'dmd',
    'dvipdf',
    'dvips',
    'f77',
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
    'ifl',
    'ilink',
    'ilink32',
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
    'nasm',
    'pdflatex',
    'pdftex',
    'Perforce',
    'qt',
    'RCS',
    'rmic',
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

for tool in tools:
    if tool[0] in '0123456789' or '+' in tool:
        test.write('SConstruct', indirect_import % (tool, tool, tool))
    else:
        test.write('SConstruct', direct_import % (tool, tool, tool))
    test.run()

test.pass_test()
