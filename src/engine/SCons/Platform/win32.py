"""SCons.Platform.win32

Platform-specific initialization for Win32 systems.

There normally shouldn't be any need to import this module directly.  It
will usually be imported through the generic SCons.Platform.Platform()
selection method.
"""

#
# Copyright (c) 2001, 2002 Steven Knight
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

import SCons.Util

def tool_list():
    masm = SCons.Util.WhereIs('ml')
    nasm =  SCons.Util.WhereIs('nasm')
    if nasm and not masm:
        assembler = 'nasm'
    else:
        assembler = 'masm'
    return ['dvipdf', 'dvips', 'g77',
            'latex', 'lex', 'lib', 'mslink', 'msvc',
            'pdflatex', 'pdftex', 'tar', 'tex', 'yacc',
            assembler]

def generate(env):
    if not env.has_key('ENV'):
        env['ENV']        = {}
    env['ENV']['PATHEXT'] = '.COM;.EXE;.BAT;.CMD'
    env['OBJPREFIX']      = ''
    env['OBJSUFFIX']      = '.obj'
    env['PROGPREFIX']     = ''
    env['PROGSUFFIX']     = '.exe'
    env['LIBPREFIX']      = ''
    env['LIBSUFFIX']      = '.lib'
    env['SHLIBPREFIX']    = ''
    env['SHLIBSUFFIX']    = '.dll'
    env['LIBPREFIXES']    = [ '$LIBPREFIX', '$SHLIBPREFIX' ]
    env['LIBSUFFIXES']    = [ '$LIBSUFFIX', '$SHLIBSUFFIX' ]
