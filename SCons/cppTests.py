# MIT License
#
# Copyright The SCons Foundation
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

import atexit
import unittest

import TestUnit

import cpp


basic_input = """
#include "file1-yes"
#include <file2-yes>
"""


substitution_input = """
#define FILE3   "file3-yes"
#define FILE4   <file4-yes>

#include FILE3
#include FILE4

#define XXX_FILE5       YYY_FILE5
#define YYY_FILE5       ZZZ_FILE5
#define ZZZ_FILE5       FILE5

#define FILE5   "file5-yes"
#define FILE6   <file6-yes>

#define XXX_FILE6       YYY_FILE6
#define YYY_FILE6       ZZZ_FILE6
#define ZZZ_FILE6       FILE6

#include XXX_FILE5
#include XXX_FILE6

#include SHELL_ESCAPED_H
"""


ifdef_input = """
#define DEFINED 0

#ifdef	DEFINED /* multi-line comment */
#include "file7-yes"
#else
#include "file7-no"
#endif

#ifdef	NOT_DEFINED
#include <file8-no>
#else
#include <file8-yes>
#endif
"""


if_boolean_input = """
#define ZERO	0  // single-line comment
#define ONE	1

#if ZERO
#include "file9-no"
#else
#include "file9-yes"
#endif

#if ONE
#include <file10-yes>
#else
#include <file10-no>
#endif

#if ZERO
#include "file11-no-1"
#elif ZERO
#include "file11-no-2"
#else
#include "file11-yes"
#endif

#if ZERO
#include <file12-no-1>
#elif ONE
#include <file12-yes>
#else
#include <file12-no-2>
#endif

#if ONE
#include "file13-yes"
#elif ZERO
#include "file13-no-1"
#else
#include "file13-no-2"
#endif

#if ONE
#include <file14-yes>
#elif ONE
#include <file14-no-1>
#else
#include <file14-no-2>
#endif
"""


if_defined_input = """
#define DEFINED_A 0
#define DEFINED_B 0

#if	defined(DEFINED_A)
#include "file15-yes"
#endif

#if	! defined(DEFINED_A)
#include <file16-no>
#else
#include <file16-yes>
#endif

#if	defined DEFINED_A
#include "file17-yes"
#endif

#if	! defined DEFINED_A
#include <file18-no>
#else
#include <file18-yes>
#endif

#if ! (defined (DEFINED_A) || defined (DEFINED_B)
#include <file19-no>
#else
#include <file19-yes>
#endif

"""


expression_input = """
#define ZERO	0
#define ONE	1

#if	ZERO && ZERO
#include "file19-no"
#else
#include "file19-yes"
#endif

#if	ZERO && ONE
#include <file20-no>
#else
#include <file20-yes>
#endif

#if	ONE && ZERO
#include "file21-no"
#else
#include "file21-yes"
#endif

#if	ONE && ONE
#include <file22-yes>
#else
#include <file22-no>
#endif

#if	ZERO || ZERO
#include "file23-no"
#else
#include "file23-yes"
#endif

#if	ZERO || ONE
#include <file24-yes>
#else
#include <file24-no>
#endif

#if	ONE || ZERO
#include "file25-yes"
#else
#include "file25-no"
#endif

#if	ONE || ONE
#include <file26-yes>
#else
#include <file26-no>
#endif

#if	ONE == ONE
#include "file27-yes"
#else
#include "file27-no"
#endif

#if	ONE != ONE
#include <file28-no>
#else
#include <file28-yes>
#endif

#if	! (ONE == ONE)
#include "file29-no"
#else
#include "file29-yes"
#endif

#if ! (ONE != ONE)
#include <file30-yes>
#else
#include <file30-no>
#endif

#if	123456789UL || 0x13L
#include <file301-yes>
#else
#include <file301-no>
#endif
"""


undef_input = """
#define	UNDEFINE	0

#ifdef	UNDEFINE
#include "file31-yes"
#else
#include "file31-no"
#endif

#undef	UNDEFINE

#ifdef	UNDEFINE
#include <file32-no>
#else
#include <file32-yes>
#endif
"""


macro_function_input = """
#define ZERO	0
#define ONE	1

#define	FUNC33(x)	"file33-yes"
#define	FUNC34(x)	<file34-yes>

#include FUNC33(ZERO)
#include FUNC34(ZERO)

#define FILE35		"file35-yes"
#define FILE36		<file36-yes>

#define	FUNC35(x, y)	FILE35
#define	FUNC36(x, y)	FILE36

#include FUNC35(ZERO, ONE)
#include FUNC36(ZERO, ONE)

#define FILE37		"file37-yes"
#define FILE38		<file38-yes>

#define	FUNC37a(x, y)	FILE37
#define	FUNC38a(x, y)	FILE38

#define	FUNC37b(x, y)	FUNC37a(x, y)
#define	FUNC38b(x, y)	FUNC38a(x, y)

#define	FUNC37c(x, y)	FUNC37b(x, y)
#define	FUNC38c(x, y)	FUNC38b(x, y)

#include FUNC37c(ZERO, ONE)
#include FUNC38c(ZERO, ONE)

#define FILE39		"file39-yes"
#define FILE40		<file40-yes>

#define	FUNC39a(x0, y0)	FILE39
#define	FUNC40a(x0, y0)	FILE40

#define	FUNC39b(x1, y2)	FUNC39a(x1, y1)
#define	FUNC40b(x1, y2)	FUNC40a(x1, y1)

#define	FUNC39c(x2, y2)	FUNC39b(x2, y2)
#define	FUNC40c(x2, y2)	FUNC40b(x2, y2)

#include FUNC39c(ZERO, ONE)
#include FUNC40c(ZERO, ONE)

/* Make sure we don't die if the expansion isn't a string. */
#define FUNC_INTEGER(x)       1

/* Make sure one-character names are recognized. */
#define _(x)       translate(x)
#undef _
"""


token_pasting_input = """
#define PASTE_QUOTE(q, name)	q##name##-yes##q
#define PASTE_ANGLE(name)	<##name##-yes>

#define FUNC41	PASTE_QUOTE(", file41)
#define FUNC42	PASTE_ANGLE(file42)

#include FUNC41
#include FUNC42
"""


no_space_input = """
#include<file43-yes>
#include"file44-yes"
"""


nested_ifs_input = """
#define DEFINED

#ifdef	NOT_DEFINED
    #include "file7-no"
    #ifdef DEFINED
        #include "file8-no"
    #else
        #include "file9-no"
    #endif
#else
    #include "file7-yes"
#endif
"""



ifndef_input = """
#define DEFINED 0

#ifndef	DEFINED
#include "file45-no"
#else
#include "file45-yes"
#endif

#ifndef	NOT_DEFINED
#include <file46-yes>
#else
#include <file46-no>
#endif
"""


if_defined_no_space_input = """
#define DEFINED 0

#if(defined DEFINED)
#include "file47-yes"
#endif

#if(!defined DEFINED)
#include <file48-no>
#elif(!defined DEFINED)
#include <file49-no>
#else
#include <file50-yes>
#endif

#if!(defined DEFINED)
#include "file51-no"
#elif!(defined DEFINED)
#include <file52-no>
#else
#include "file53-yes"
#endif
"""

if_no_space_input = """
#define DEFINED 0

#if(DEFINED)
#include "file54-no"
#endif

#if!(DEFINED)
#include <file55-yes>
#elif!(DEFINED)
#include <file56-no>
#endif

#if(DEFINED)
#include "file57-no"
#elif(!DEFINED)
#include <file58-yes>
#endif

#if!( DEFINED)
#include "file59-yes"
#elif!( DEFINED)
#include <file60-no>
#endif

#if( DEFINED)
#include "file61-no"
#elif(! DEFINED)
#include <file62-yes>
#endif
"""


#    pp_class = PreProcessor
#    #pp_class = DumbPreProcessor

#    pp = pp_class(current = ".",
#                  cpppath = ['/usr/include'],
#                  print_all = 1)
#    #pp(open(sys.argv[1]).read())
#    pp(input)


class cppTestCase(unittest.TestCase):
    def setUp(self):
        self.cpp = self.cpp_class(current = ".",
                                  cpppath = ['/usr/include'],
                                  dict={"SHELL_ESCAPED_H": '\\"file-shell-computed-yes\\"'})

    def test_basic(self):
        """Test basic #include scanning"""
        expect = self.basic_expect
        result = self.cpp.process_contents(basic_input)
        assert expect == result, (expect, result)

    def test_substitution(self):
        """Test substitution of #include files using CPP variables"""
        expect = self.substitution_expect
        result = self.cpp.process_contents(substitution_input)
        assert expect == result, (expect, result)

    def test_ifdef(self):
        """Test basic #ifdef processing"""
        expect = self.ifdef_expect
        result = self.cpp.process_contents(ifdef_input)
        assert expect == result, (expect, result)

    def test_if_boolean(self):
        """Test #if with Boolean values"""
        expect = self.if_boolean_expect
        result = self.cpp.process_contents(if_boolean_input)
        assert expect == result, (expect, result)

    def test_if_defined(self):
        """Test #if defined() idioms"""
        expect = self.if_defined_expect
        result = self.cpp.process_contents(if_defined_input)
        assert expect == result, (expect, result)

    def test_expression(self):
        """Test #if with arithmetic expressions"""
        expect = self.expression_expect
        result = self.cpp.process_contents(expression_input)
        assert expect == result, (expect, result)

    def test_undef(self):
        """Test #undef handling"""
        expect = self.undef_expect
        result = self.cpp.process_contents(undef_input)
        assert expect == result, (expect, result)

    def test_macro_function(self):
        """Test using macro functions to express file names"""
        expect = self.macro_function_expect
        result = self.cpp.process_contents(macro_function_input)
        assert expect == result, (expect, result)

    def test_token_pasting(self):
        """Test token-pasting to construct file names"""
        expect = self.token_pasting_expect
        result = self.cpp.process_contents(token_pasting_input)
        assert expect == result, (expect, result)

    def test_no_space(self):
        """Test no space between #include and the quote"""
        expect = self.no_space_expect
        result = self.cpp.process_contents(no_space_input)
        assert expect == result, (expect, result)

    def test_nested_ifs(self):
        expect = self.nested_ifs_expect
        result = self.cpp.process_contents(nested_ifs_input)
        assert expect == result, (expect, result)

    def test_ifndef(self):
        """Test basic #ifndef processing"""
        expect = self.ifndef_expect
        result = self.cpp.process_contents(ifndef_input)
        assert expect == result, (expect, result)

    def test_if_defined_no_space(self):
        """Test #if(defined, i.e.without space but parenthesis"""
        expect = self.if_defined_no_space_expect
        result = self.cpp.process_contents(if_defined_no_space_input)
        assert expect == result, (expect, result)

    def test_if_no_space(self):
        """Test #if(, i.e. without space but parenthesis"""
        expect = self.if_no_space_expect
        result = self.cpp.process_contents(if_no_space_input)
        assert expect == result, (expect, result)


class cppAllTestCase(cppTestCase):
    def setUp(self):
        self.cpp = self.cpp_class(current = ".",
                                  cpppath = ['/usr/include'],
                                  dict={"SHELL_ESCAPED_H": '\\"file-shell-computed-yes\\"'},
                                  all=1)

class PreProcessorTestCase(cppAllTestCase):
    cpp_class = cpp.PreProcessor

    basic_expect = [
        ('include', '"', 'file1-yes'),
        ('include', '<', 'file2-yes'),
    ]

    substitution_expect = [
        ('include', '"', 'file3-yes'),
        ('include', '<', 'file4-yes'),
        ('include', '"', 'file5-yes'),
        ('include', '<', 'file6-yes'),
        ('include', '"', 'file-shell-computed-yes'),
    ]

    ifdef_expect = [
        ('include', '"', 'file7-yes'),
        ('include', '<', 'file8-yes'),
    ]

    if_boolean_expect = [
        ('include', '"', 'file9-yes'),
        ('include', '<', 'file10-yes'),
        ('include', '"', 'file11-yes'),
        ('include', '<', 'file12-yes'),
        ('include', '"', 'file13-yes'),
        ('include', '<', 'file14-yes'),
    ]

    if_defined_expect = [
        ('include', '"', 'file15-yes'),
        ('include', '<', 'file16-yes'),
        ('include', '"', 'file17-yes'),
        ('include', '<', 'file18-yes'),
        ('include', '<', 'file19-yes'),
    ]

    expression_expect = [
        ('include', '"', 'file19-yes'),
        ('include', '<', 'file20-yes'),
        ('include', '"', 'file21-yes'),
        ('include', '<', 'file22-yes'),
        ('include', '"', 'file23-yes'),
        ('include', '<', 'file24-yes'),
        ('include', '"', 'file25-yes'),
        ('include', '<', 'file26-yes'),
        ('include', '"', 'file27-yes'),
        ('include', '<', 'file28-yes'),
        ('include', '"', 'file29-yes'),
        ('include', '<', 'file30-yes'),
        ('include', '<', 'file301-yes'),
    ]

    undef_expect = [
        ('include', '"', 'file31-yes'),
        ('include', '<', 'file32-yes'),
    ]

    macro_function_expect = [
        ('include', '"', 'file33-yes'),
        ('include', '<', 'file34-yes'),
        ('include', '"', 'file35-yes'),
        ('include', '<', 'file36-yes'),
        ('include', '"', 'file37-yes'),
        ('include', '<', 'file38-yes'),
        ('include', '"', 'file39-yes'),
        ('include', '<', 'file40-yes'),
    ]

    token_pasting_expect = [
        ('include', '"', 'file41-yes'),
        ('include', '<', 'file42-yes'),
    ]

    no_space_expect = [
        ('include', '<', 'file43-yes'),
        ('include', '"', 'file44-yes'),
    ]

    nested_ifs_expect = [
        ('include', '"', 'file7-yes'),
    ]

    ifndef_expect = [
        ('include', '"', 'file45-yes'),
        ('include', '<', 'file46-yes'),
    ]

    if_defined_no_space_expect = [
        ('include', '"', 'file47-yes'),
        ('include', '<', 'file50-yes'),
        ('include', '"', 'file53-yes'),
    ]

    if_no_space_expect = [
        ('include', '<', 'file55-yes'),
        ('include', '<', 'file58-yes'),
        ('include', '"', 'file59-yes'),
        ('include', '<', 'file62-yes'),
    ]

class DumbPreProcessorTestCase(cppAllTestCase):
    cpp_class = cpp.DumbPreProcessor

    basic_expect = [
        ('include', '"', 'file1-yes'),
        ('include', '<', 'file2-yes'),
    ]

    substitution_expect = [
        ('include', '"', 'file3-yes'),
        ('include', '<', 'file4-yes'),
        ('include', '"', 'file5-yes'),
        ('include', '<', 'file6-yes'),
        ('include', '"', 'file-shell-computed-yes'),
    ]

    ifdef_expect = [
        ('include', '"', 'file7-yes'),
        ('include', '"', 'file7-no'),
        ('include', '<', 'file8-no'),
        ('include', '<', 'file8-yes'),
    ]

    if_boolean_expect = [
        ('include', '"', 'file9-no'),
        ('include', '"', 'file9-yes'),
        ('include', '<', 'file10-yes'),
        ('include', '<', 'file10-no'),
        ('include', '"', 'file11-no-1'),
        ('include', '"', 'file11-no-2'),
        ('include', '"', 'file11-yes'),
        ('include', '<', 'file12-no-1'),
        ('include', '<', 'file12-yes'),
        ('include', '<', 'file12-no-2'),
        ('include', '"', 'file13-yes'),
        ('include', '"', 'file13-no-1'),
        ('include', '"', 'file13-no-2'),
        ('include', '<', 'file14-yes'),
        ('include', '<', 'file14-no-1'),
        ('include', '<', 'file14-no-2'),
    ]

    if_defined_expect = [
        ('include', '"', 'file15-yes'),
        ('include', '<', 'file16-no'),
        ('include', '<', 'file16-yes'),
        ('include', '"', 'file17-yes'),
        ('include', '<', 'file18-no'),
        ('include', '<', 'file18-yes'),
        ('include', '<', 'file19-no'),
        ('include', '<', 'file19-yes'),
    ]

    expression_expect = [
        ('include', '"', 'file19-no'),
        ('include', '"', 'file19-yes'),
        ('include', '<', 'file20-no'),
        ('include', '<', 'file20-yes'),
        ('include', '"', 'file21-no'),
        ('include', '"', 'file21-yes'),
        ('include', '<', 'file22-yes'),
        ('include', '<', 'file22-no'),
        ('include', '"', 'file23-no'),
        ('include', '"', 'file23-yes'),
        ('include', '<', 'file24-yes'),
        ('include', '<', 'file24-no'),
        ('include', '"', 'file25-yes'),
        ('include', '"', 'file25-no'),
        ('include', '<', 'file26-yes'),
        ('include', '<', 'file26-no'),
        ('include', '"', 'file27-yes'),
        ('include', '"', 'file27-no'),
        ('include', '<', 'file28-no'),
        ('include', '<', 'file28-yes'),
        ('include', '"', 'file29-no'),
        ('include', '"', 'file29-yes'),
        ('include', '<', 'file30-yes'),
        ('include', '<', 'file30-no'),
        ('include', '<', 'file301-yes'),
        ('include', '<', 'file301-no'),
    ]

    undef_expect = [
        ('include', '"', 'file31-yes'),
        ('include', '"', 'file31-no'),
        ('include', '<', 'file32-no'),
        ('include', '<', 'file32-yes'),
    ]

    macro_function_expect = [
        ('include', '"', 'file33-yes'),
        ('include', '<', 'file34-yes'),
        ('include', '"', 'file35-yes'),
        ('include', '<', 'file36-yes'),
        ('include', '"', 'file37-yes'),
        ('include', '<', 'file38-yes'),
        ('include', '"', 'file39-yes'),
        ('include', '<', 'file40-yes'),
    ]

    token_pasting_expect = [
        ('include', '"', 'file41-yes'),
        ('include', '<', 'file42-yes'),
    ]

    no_space_expect = [
        ('include', '<', 'file43-yes'),
        ('include', '"', 'file44-yes'),
    ]

    nested_ifs_expect = [
        ('include', '"', 'file7-no'),
        ('include', '"', 'file8-no'),
        ('include', '"', 'file9-no'),
        ('include', '"', 'file7-yes')
    ]

    ifndef_expect = [
        ('include', '"', 'file45-no'),
        ('include', '"', 'file45-yes'),
        ('include', '<', 'file46-yes'),
        ('include', '<', 'file46-no'),
    ]

    if_defined_no_space_expect = [
        ('include', '"', 'file47-yes'),
        ('include', '<', 'file48-no'),
        ('include', '<', 'file49-no'),
        ('include', '<', 'file50-yes'),
        ('include', '"', 'file51-no'),
        ('include', '<', 'file52-no'),
        ('include', '"', 'file53-yes'),
    ]

    if_no_space_expect = [
        ('include', '"', 'file54-no'),
        ('include', '<', 'file55-yes'),
        ('include', '<', 'file56-no'),
        ('include', '"', 'file57-no'),
        ('include', '<', 'file58-yes'),
        ('include', '"', 'file59-yes'),
        ('include', '<', 'file60-no'),
        ('include', '"', 'file61-no'),
        ('include', '<', 'file62-yes'),
    ]

import os
import re
import shutil
import tempfile

_Cleanup = []

def _clean():
    for dir in _Cleanup:
        if os.path.exists(dir):
            shutil.rmtree(dir)

atexit.register(_clean)

if os.name in ('posix', 'nt'):
    tmpprefix = 'cppTests.' + str(os.getpid()) + '.'
else:
    tmpprefix = 'cppTests.'

class fileTestCase(unittest.TestCase):
    cpp_class = cpp.DumbPreProcessor

    def setUp(self):
        path = tempfile.mkdtemp(prefix=tmpprefix)
        _Cleanup.append(path)
        self.tempdir = path
        self.orig_cwd = os.getcwd()
        os.chdir(path)

    def tearDown(self):
        os.chdir(self.orig_cwd)
        shutil.rmtree(self.tempdir)
        _Cleanup.remove(self.tempdir)

    def strip_initial_spaces(self, s):
        lines = s.split('\n')
        spaces = re.match(' *', lines[0]).group(0)
        def strip_spaces(l, spaces=spaces):
            if l[:len(spaces)] == spaces:
                l = l[len(spaces):]
            return l
        return '\n'.join(map(strip_spaces, lines))

    def write(self, file, contents):
        with open(file, 'w') as f:
            f.write(self.strip_initial_spaces(contents))

    def test_basic(self):
        """Test basic file inclusion"""
        self.write('f1.h', """\
        #include "f2.h"
        """)
        self.write('f2.h', """\
        #include <f3.h>
        """)
        self.write('f3.h', """\
        """)
        p = cpp.DumbPreProcessor(current = os.curdir,
                                 cpppath = [os.curdir])
        result = p('f1.h')
        assert result == ['f2.h', 'f3.h'], result

    def test_current_file(self):
        """Test use of the .current_file attribute"""
        self.write('f1.h', """\
        #include <f2.h>
        """)
        self.write('f2.h', """\
        #include "f3.h"
        """)
        self.write('f3.h', """\
        """)
        class MyPreProcessor(cpp.DumbPreProcessor):
            def __init__(self, *args, **kw):
                super().__init__(*args, **kw)
                self.files = []
            def __call__(self, file):
                self.files.append(file)
                return cpp.DumbPreProcessor.__call__(self, file)
            def scons_current_file(self, t):
                r = cpp.DumbPreProcessor.scons_current_file(self, t)
                self.files.append(self.current_file)
                return r
        p = MyPreProcessor(current = os.curdir, cpppath = [os.curdir])
        result = p('f1.h')
        assert result == ['f2.h', 'f3.h'], result
        assert p.files == ['f1.h', 'f2.h', 'f3.h', 'f2.h', 'f1.h'], p.files



if __name__ == '__main__':
    suite = unittest.TestSuite()
    tclasses = [ PreProcessorTestCase,
                 DumbPreProcessorTestCase,
                 fileTestCase,
               ]
    for tclass in tclasses:
        loader = unittest.TestLoader()
        loader.testMethodPrefix = 'test_'
        names = loader.getTestCaseNames(tclass)
        try:
            names = sorted(set(names))
        except NameError:
            pass
        suite.addTests(list(map(tclass, names)))
    TestUnit.run(suite)

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
