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

import os
import unittest
from unittest import mock

import SCons.Scanner.Fortran
import SCons.Node.FS
import SCons.Warnings

import TestCmd

original = os.getcwd()

test = TestCmd.TestCmd(workdir='')

os.chdir(test.workpath(''))

# create some source files and headers:

test.write('fff1.f', """
      PROGRAM FOO
      INCLUDE 'f1.f'
      include 'f2.f'
      STOP
      END
""")

test.write('fff2.f', """
      PROGRAM FOO
      INCLUDE 'f2.f'
      include 'd1/f2.f'
      INCLUDE 'd2/f2.f'
      STOP
      END
""")

test.write('fff3.f', """
      PROGRAM FOO
      INCLUDE 'f3.f' ; INCLUDE\t'd1/f3.f'
      STOP
      END
""")

# for Emacs -> "

test.subdir('d1', ['d1', 'd2'])

test_headers = ['fi.f', 'never.f',
                'd1/f1.f', 'd1/f2.f', 'd1/f3.f', 'd1/fi.f',
                'd1/d2/f1.f', 'd1/d2/f2.f', 'd1/d2/f3.f',
                'd1/d2/f4.f', 'd1/d2/fi.f']

for h in test_headers:
    test.write(h, "\n")

test.subdir('include', 'subdir', ['subdir', 'include'])

test.write('fff4.f', """
      PROGRAM FOO
      INCLUDE 'f4.f'
      STOP
      END
""")

test.write('include/f4.f', "\n")
test.write('subdir/include/f4.f', "\n")

test.write('fff5.f', """
      PROGRAM FOO
      INCLUDE 'f5.f'
      INCLUDE 'not_there.f'
      STOP
      END
""")

test.write('f5.f', "\n")

test.subdir('repository', ['repository', 'include'],
            ['repository', 'src'])
test.subdir('work', ['work', 'src'])

test.write(['repository', 'include', 'iii.f'], "\n")

test.write(['work', 'src', 'fff.f'], """
      PROGRAM FOO
      INCLUDE 'iii.f'
      INCLUDE 'jjj.f'
      STOP
      END
""")

test.write(['work', 'src', 'aaa.f'], """
      PROGRAM FOO
      INCLUDE 'bbb.f'
      STOP
      END
""")

test.write(['work', 'src', 'bbb.f'], "\n")

test.write(['repository', 'src', 'ccc.f'], """
      PROGRAM FOO
      INCLUDE 'ddd.f'
      STOP
      END
""")

test.write(['repository', 'src', 'ddd.f'], "\n")

test.write('fff90a.f90', """
      PROGRAM FOO

!  Test comments - these includes should NOT be picked up
C     INCLUDE 'fi.f'
#     INCLUDE 'fi.f'
  !   INCLUDE 'fi.f'

      INCLUDE 'f1.f'  ! in-line comments are valid syntax
      INCLUDE"fi.f"   ! space is significant - this should be ignored
      INCLUDE  <f2.f>  ! Absoft compiler allows greater than/less than delimiters
!
!  Allow kind type parameters
      INCLUDE kindType_"f3.f"
      INCLUDE kind_Type_"f4.f"
!
!  Test multiple statements per line - use various spacings between semicolons
      incLUDE 'f5.f';include "f6.f"  ;  include <f7.f>; include 'f8.f' ;include kindType_'f9.f'
!
!  Test various USE statement syntaxes
!
      USE Mod01
      use mod02
      use use
      USE mOD03, ONLY : someVar
      USE MOD04 ,only:someVar
      USE Mod05 , ONLY: someVar ! in-line comment
      USE Mod06,ONLY :someVar,someOtherVar

      USE  mod07;USE  mod08; USE mod09 ;USE mod10 ; USE mod11  ! Test various semicolon placements
      use mod12 ;use mod13! Test comment at end of line

!     USE modi
!     USE modia ; use modib    ! Both modules are in a comment
    ! USE modic ; ! use modid  ! Scanner regexp should ignore both modules
      USE mod14 !; USE modi    ! Only ignore the second
      USE mod15!;USE modi
      USE mod16  !  ;  USE  modi

!  Test semicolon syntax - use various spacings
      USE :: mod17
      USE::mod18
      USE ::mod19 ; USE:: mod20

      use, non_intrinsic :: mod21, ONLY : someVar ; use,intrinsic:: mod22
      USE, NON_INTRINSIC::mod23 ; USE ,INTRINSIC ::mod24

USE mod25  ! Test USE statement at the beginning of line


; USE modi   ! The scanner does not validate leading-semicolon syntax
      USEmodi   ! No space in between USE and module name - ignore it
      USE mod01   ! This one is a duplicate - there should only be one dependency to it.

      STOP
      END
""")

test_modules = ['mod01.mod', 'mod02.mod', 'mod03.mod', 'mod04.mod', 'mod05.mod',
                'mod06.mod', 'mod07.mod', 'mod08.mod', 'mod09.mod', 'mod10.mod',
                'mod11.mod', 'mod12.mod', 'mod13.mod', 'mod14.mod', 'mod15.mod',
                'mod16.mod', 'mod17.mod', 'mod18.mod', 'mod19.mod', 'mod20.mod',
                'mod21.mod', 'mod22.mod', 'mod23.mod', 'mod24.mod', 'mod25.mod']

for m in test_modules:
    test.write(m, "\n")

test.subdir('modules')
test.write(['modules', 'use.mod'], "\n")


# define some helpers:

class DummyEnvironment:
    def __init__(self, listCppPath) -> None:
        self.path = listCppPath
        self.fs = SCons.Node.FS.FS(test.workpath(''))

    def Dictionary(self, *args):
        if not args:
            return {'FORTRANPATH': self.path, 'FORTRANMODSUFFIX': ".mod"}
        elif len(args) == 1 and args[0] == 'FORTRANPATH':
            return self.path
        else:
            raise KeyError("Dummy environment only has FORTRANPATH attribute.")

    def __contains__(self, key) -> bool:
        return key in self.Dictionary()

    def __getitem__(self, key):
        return self.Dictionary()[key]

    def __setitem__(self, key, value) -> None:
        self.Dictionary()[key] = value

    def __delitem__(self, key) -> None:
        del self.Dictionary()[key]

    def subst(self, arg, target=None, source=None, conv=None):
        if arg[0] == '$':
            return self[arg[1:]]
        return arg

    def subst_path(self, path, target=None, source=None, conv=None):
        if not isinstance(path, list):
            path = [path]
        return list(map(self.subst, path))

    def get_calculator(self):
        return None

    def get_factory(self, factory):
        return factory or self.fs.File

    def Dir(self, filename):
        return self.fs.Dir(filename)

    def File(self, filename):
        return self.fs.File(filename)


def deps_match(self, deps, headers) -> None:
    scanned = list(map(os.path.normpath, list(map(str, deps))))
    expect = list(map(os.path.normpath, headers))
    self.assertTrue(scanned == expect, "expect %s != scanned %s" % (expect, scanned))


# define some tests:

class FortranScannerTestCase1(unittest.TestCase):
    def runTest(self) -> None:
        test.write('f1.f', "\n")
        test.write('f2.f', "      INCLUDE 'fi.f'\n")
        env = DummyEnvironment([])
        s = SCons.Scanner.Fortran.FortranScan()
        path = s.path(env)
        deps = s(env.File('fff1.f'), env, path)
        headers = ['f1.f', 'f2.f']
        deps_match(self, deps, headers)
        test.unlink('f1.f')
        test.unlink('f2.f')


class FortranScannerTestCase2(unittest.TestCase):
    def runTest(self) -> None:
        test.write('f1.f', "\n")
        test.write('f2.f', "      INCLUDE 'fi.f'\n")
        env = DummyEnvironment([test.workpath("d1")])
        s = SCons.Scanner.Fortran.FortranScan()
        path = s.path(env)
        deps = s(env.File('fff1.f'), env, path)
        headers = ['f1.f', 'f2.f']
        deps_match(self, deps, headers)
        test.unlink('f1.f')
        test.unlink('f2.f')


class FortranScannerTestCase3(unittest.TestCase):
    def runTest(self) -> None:
        env = DummyEnvironment([test.workpath("d1")])
        s = SCons.Scanner.Fortran.FortranScan()
        path = s.path(env)
        deps = s(env.File('fff1.f'), env, path)
        headers = ['d1/f1.f', 'd1/f2.f']
        deps_match(self, deps, headers)


class FortranScannerTestCase4(unittest.TestCase):
    def runTest(self) -> None:
        test.write(['d1', 'f2.f'], "      INCLUDE 'fi.f'\n")
        env = DummyEnvironment([test.workpath("d1")])
        s = SCons.Scanner.Fortran.FortranScan()
        path = s.path(env)
        deps = s(env.File('fff1.f'), env, path)
        headers = ['d1/f1.f', 'd1/f2.f']
        deps_match(self, deps, headers)
        test.write(['d1', 'f2.f'], "\n")


class FortranScannerTestCase5(unittest.TestCase):
    def runTest(self) -> None:
        env = DummyEnvironment([test.workpath("d1")])
        s = SCons.Scanner.Fortran.FortranScan()
        path = s.path(env)
        deps = s(env.File('fff2.f'), env, path)
        headers = ['d1/f2.f', 'd1/d2/f2.f', 'd1/f2.f']
        deps_match(self, deps, headers)


class FortranScannerTestCase6(unittest.TestCase):
    def runTest(self) -> None:
        test.write('f2.f', "\n")
        env = DummyEnvironment([test.workpath("d1")])
        s = SCons.Scanner.Fortran.FortranScan()
        path = s.path(env)
        deps = s(env.File('fff2.f'), env, path)
        headers = ['d1/f2.f', 'd1/d2/f2.f', 'f2.f']
        deps_match(self, deps, headers)
        test.unlink('f2.f')


class FortranScannerTestCase7(unittest.TestCase):
    def runTest(self) -> None:
        env = DummyEnvironment([test.workpath("d1/d2"), test.workpath("d1")])
        s = SCons.Scanner.Fortran.FortranScan()
        path = s.path(env)
        deps = s(env.File('fff2.f'), env, path)
        headers = ['d1/f2.f', 'd1/d2/f2.f', 'd1/d2/f2.f']
        deps_match(self, deps, headers)


class FortranScannerTestCase8(unittest.TestCase):
    def runTest(self) -> None:
        test.write('f2.f', "\n")
        env = DummyEnvironment([test.workpath("d1/d2"), test.workpath("d1")])
        s = SCons.Scanner.Fortran.FortranScan()
        path = s.path(env)
        deps = s(env.File('fff2.f'), env, path)
        headers = ['d1/f2.f', 'd1/d2/f2.f', 'f2.f']
        deps_match(self, deps, headers)
        test.unlink('f2.f')


class FortranScannerTestCase9(unittest.TestCase):
    def runTest(self) -> None:
        test.write('f3.f', "\n")
        env = DummyEnvironment([])
        s = SCons.Scanner.Fortran.FortranScan()
        path = s.path(env)

        n = env.File('fff3.f')

        def my_rexists(s):
            s.Tag('rexists_called', 1)
            return SCons.Node._rexists_map[s.GetTag('old_rexists')](s)

        n.Tag('old_rexists', n._func_rexists)
        SCons.Node._rexists_map[3] = my_rexists
        n._func_rexists = 3

        deps = s(n, env, path)

        # Make sure rexists() got called on the file node being
        # scanned, essential for cooperation with VariantDir functionality.
        assert n.GetTag('rexists_called')

        headers = ['d1/f3.f', 'f3.f']
        deps_match(self, deps, headers)
        test.unlink('f3.f')


class FortranScannerTestCase10(unittest.TestCase):
    def runTest(self) -> None:
        env = DummyEnvironment(["include"])
        s = SCons.Scanner.Fortran.FortranScan()
        path = s.path(env)
        deps1 = s(env.File('fff4.f'), env, path)
        env.fs.chdir(env.Dir('subdir'))
        test_dir = env.fs.getcwd()
        env.fs.chdir(env.Dir(''))
        path = s.path(env, test_dir)
        deps2 = s(env.File('#fff4.f'), env, path)
        headers1 = [test.workpath(f) for f in ['include/f4.f']]
        headers2 = ['include/f4.f']
        deps_match(self, deps1, headers1)
        deps_match(self, deps2, headers2)


class FortranScannerTestCase11(unittest.TestCase):
    def runTest(self) -> None:
        SCons.Warnings.enableWarningClass(SCons.Warnings.DependencyWarning)

        class TestOut:
            def __call__(self, x) -> None:
                self.out = x

        to = TestOut()
        to.out = None
        SCons.Warnings._warningOut = to
        env = DummyEnvironment([])
        s = SCons.Scanner.Fortran.FortranScan()
        path = s.path(env)
        deps = s(env.File('fff5.f'), env, path)

        # Did we catch the warning from not finding not_there.f?
        assert to.out

        deps_match(self, deps, ['f5.f'])


class FortranScannerTestCase12(unittest.TestCase):
    def runTest(self) -> None:
        env = DummyEnvironment([])
        env.fs.chdir(env.Dir('include'))
        s = SCons.Scanner.Fortran.FortranScan()
        path = s.path(env)
        test.write('include/fff4.f', test.read('fff4.f'))
        deps = s(env.File('#include/fff4.f'), env, path)
        env.fs.chdir(env.Dir(''))
        deps_match(self, deps, ['f4.f'])
        test.unlink('include/fff4.f')


class FortranScannerTestCase13(unittest.TestCase):
    def runTest(self) -> None:
        os.chdir(test.workpath('work'))
        fs = SCons.Node.FS.FS(test.workpath('work'))
        fs.Repository(test.workpath('repository'))

        # Create a derived file in a directory that does not exist yet.
        # This was a bug at one time.
        f1 = fs.File('include2/jjj.f')
        f1.builder = 1
        env = DummyEnvironment(['include', 'include2'])
        env.fs = fs
        s = SCons.Scanner.Fortran.FortranScan()
        path = s.path(env)
        deps = s(fs.File('src/fff.f'), env, path)
        deps_match(self, deps, [test.workpath('repository/include/iii.f'), 'include2/jjj.f'])
        os.chdir(test.workpath(''))


class FortranScannerTestCase14(unittest.TestCase):
    def runTest(self) -> None:
        os.chdir(test.workpath('work'))
        fs = SCons.Node.FS.FS(test.workpath('work'))
        fs.VariantDir('build1', 'src', 1)
        fs.VariantDir('build2', 'src', 0)
        fs.Repository(test.workpath('repository'))
        env = DummyEnvironment([])
        env.fs = fs
        s = SCons.Scanner.Fortran.FortranScan()
        path = s.path(env)
        deps1 = s(fs.File('build1/aaa.f'), env, path)
        deps_match(self, deps1, ['build1/bbb.f'])
        deps2 = s(fs.File('build2/aaa.f'), env, path)
        deps_match(self, deps2, ['src/bbb.f'])
        deps3 = s(fs.File('build1/ccc.f'), env, path)
        deps_match(self, deps3, ['build1/ddd.f'])
        deps4 = s(fs.File('build2/ccc.f'), env, path)
        deps_match(self, deps4, [test.workpath('repository/src/ddd.f')])
        os.chdir(test.workpath(''))


class FortranScannerTestCase15(unittest.TestCase):
    def runTest(self) -> None:
        class SubstEnvironment(DummyEnvironment):
            def subst(self, arg, target=None, source=None, conv=None, test=test):
                if arg == "$junk":
                    return test.workpath("d1")
                else:
                    return arg

        test.write(['d1', 'f2.f'], "      INCLUDE 'fi.f'\n")
        env = SubstEnvironment(["$junk"])
        s = SCons.Scanner.Fortran.FortranScan()
        path = s.path(env)
        deps = s(env.File('fff1.f'), env, path)
        headers = ['d1/f1.f', 'd1/f2.f']
        deps_match(self, deps, headers)
        test.write(['d1', 'f2.f'], "\n")


class FortranScannerTestCase16(unittest.TestCase):
    def runTest(self) -> None:
        test.write('f1.f', "\n")
        test.write('f2.f', "\n")
        test.write('f3.f', "\n")
        test.write('f4.f', "\n")
        test.write('f5.f', "\n")
        test.write('f6.f', "\n")
        test.write('f7.f', "\n")
        test.write('f8.f', "\n")
        test.write('f9.f', "\n")
        test.write('f10.f', "\n")
        env = DummyEnvironment([test.workpath('modules')])
        s = SCons.Scanner.Fortran.FortranScan()
        path = s.path(env)
        deps = s(env.File('fff90a.f90'), env, path)
        headers = ['f1.f', 'f2.f', 'f3.f', 'f4.f', 'f5.f', 'f6.f', 'f7.f', 'f8.f', 'f9.f']
        modules = ['mod01.mod', 'mod02.mod', 'mod03.mod', 'mod04.mod', 'mod05.mod',
                   'mod06.mod', 'mod07.mod', 'mod08.mod', 'mod09.mod', 'mod10.mod',
                   'mod11.mod', 'mod12.mod', 'mod13.mod', 'mod14.mod', 'mod15.mod',
                   'mod16.mod', 'mod17.mod', 'mod18.mod', 'mod19.mod', 'mod20.mod',
                   'mod21.mod', 'mod22.mod', 'mod23.mod', 'mod24.mod', 'mod25.mod', 'modules/use.mod']
        deps_expected = headers + modules
        deps_match(self, deps, deps_expected)
        test.unlink('f1.f')
        test.unlink('f2.f')
        test.unlink('f3.f')
        test.unlink('f4.f')
        test.unlink('f5.f')
        test.unlink('f6.f')
        test.unlink('f7.f')
        test.unlink('f8.f')
        test.unlink('f9.f')
        test.unlink('f10.f')

class FortranScannerCommentsTestCase(unittest.TestCase):
    def setUp(self) -> None:
        for name in ['comment_real.mod', 'comment_phantom.mod',
                     'comment_second.mod', 'comment_local.mod', 'x.mod',
                     'comment_real.inc', 'comment_second.inc',
                     'comment_phantom.inc', 'comment!semi;.inc']:
            test.write(name, "\n")

    def scan(self, contents, suffix='.f90'):
        filename = 'comment_test' + suffix
        test.write(filename, contents)
        env = DummyEnvironment([])
        scanner = SCons.Scanner.Fortran.FortranScan()
        return scanner(env.File(filename), env, scanner.path(env))

    def test_comment_dependencies(self) -> None:
        cases = [
            ("! USE comment_phantom; USE comment_phantom\n", []),
            ("    ! USE comment_phantom; USE comment_phantom\n", []),
            ("      ! USE comment_phantom; USE comment_phantom\n", []),
            ("      USE comment_real !; USE comment_phantom\n",
             ['comment_real.mod']),
            ("      USE comment_real; USE comment_real!; USE comment_phantom\n",
             ['comment_real.mod']),
            ("USE x!; USE comment_phantom\n", ['x.mod']),
            ("! INCLUDE 'comment_real.inc'; INCLUDE 'comment_phantom.inc'\n", []),
            ("      INCLUDE 'comment_real.inc' !; INCLUDE 'comment_phantom.inc'\n",
             ['comment_real.inc']),
            ("! A comment's quote must not affect the next line\n"
             "USE comment_real !; USE comment_phantom", ['comment_real.mod']),
            ("USE comment_real !; USE comment_phantom\r\n"
             "USE comment_second\r\n", ['comment_real.mod', 'comment_second.mod']),
        ]
        for contents, expected in cases:
            with self.subTest(contents=contents):
                deps_match(self, self.scan(contents), expected)

    def test_character_literals(self) -> None:
        cases = [
            "PRINT *, 'a!;b'; USE comment_real !; USE comment_phantom\n",
            'PRINT *, "a!;b"; USE comment_real !; USE comment_phantom\n',
            "PRINT *, 'a''!;b'; USE comment_real !; USE comment_phantom\n",
            'PRINT *, "a""!;b"; USE comment_real !; USE comment_phantom\n',
            "PRINT *, 'a\"!;b'; USE comment_real !; USE comment_phantom\n",
            'PRINT *, "a\'!;b"; USE comment_real !; USE comment_phantom\n',
            "PRINT *, 'a&\n! A comment's quote in a continued literal\n"
            "&!b'; USE comment_real !; USE comment_phantom\n",
            "PRINT *, 'a&\n  \n&!b'; USE comment_real !; USE comment_phantom\n",
            "      PRINT *, 'a\n"
            "     &!b'; USE comment_real !; USE comment_phantom\n",
            "      PRINT *, 'a\n\n"
            "     &!b'; USE comment_real !; USE comment_phantom\n",
        ]
        for contents in cases:
            with self.subTest(contents=contents):
                deps_match(self, self.scan(contents), ['comment_real.mod'])

    def test_include_paths(self) -> None:
        cases = [
            "INCLUDE 'comment!semi;.inc'; INCLUDE 'comment_second.inc'\n",
            'INCLUDE "comment!semi;.inc"; INCLUDE "comment_second.inc"\n',
            'INCLUDE <comment!semi;.inc>; INCLUDE <comment_second.inc>\n',
            'INCLUDE kind_"comment!semi;.inc"; INCLUDE "comment_second.inc"\n',
        ]
        for contents in cases:
            with self.subTest(contents=contents):
                contents = contents.rstrip('\n') + " !; USE comment_phantom\n"
                deps_match(self, self.scan(contents),
                           ['comment!semi;.inc', 'comment_second.inc'])

    def test_free_form_column_six_quote(self) -> None:
        test.write('real!file.inc', "\n")
        for quote in ["'", '"']:
            with self.subTest(quote=quote):
                contents = f"""\
program p
print *, &
     {quote}a{quote}
     include 'real!file.inc'
end
"""
                deps_match(self, self.scan(contents), ['real!file.inc'])

    def test_semicolons_and_module_definitions(self) -> None:
        contents = """\
MODULE comment_local
END MODULE comment_local
USE COMMENT_LOCAL; USE comment_real; USE comment_second !; USE comment_phantom
"""
        deps_match(self, self.scan(contents), ['comment_real.mod', 'comment_second.mod'])

    def test_column_six_continuation(self) -> None:
        cases = [
            "      PRINT *, 'a'\n     ! ; USE comment_real\n",
            "      PRINT *,\nC A comment's quote\n"
            "     & '!'; USE comment_real !; USE comment_phantom\n",
            "      PRINT *, 'a\nC A comment's quote\n"
            "     &!b'; USE comment_real !; USE comment_phantom\n",
        ]
        for contents in cases:
            with self.subTest(contents=contents):
                deps_match(self, self.scan(contents, '.f'), ['comment_real.mod'])

    def test_column_six_quote_marker(self) -> None:
        for quote in ["'", '"']:
            for first_line, continuation in [
                ("      PRINT *,\n", f' {quote}!a{quote}'),
                (f'      PRINT *, {quote}a\n', f'!b{quote}'),
                (f'      PRINT *, {quote}a&\n', f'!b{quote}'),
            ]:
                with self.subTest(quote=quote, first_line=first_line):
                    contents = (first_line + '     ' + quote + continuation
                                + '; USE comment_real !; USE comment_phantom\n')
                    deps_match(self, self.scan(contents, '.f'), ['comment_real.mod'])

    def test_cached_dependencies(self) -> None:
        test.write('comment_cached.f90',
                   "USE comment_real !; USE comment_phantom\n")
        env = DummyEnvironment([])
        scanner = SCons.Scanner.Fortran.FortranScan()
        node = env.File('comment_cached.f90')
        path = scanner.path(env)
        deps_match(self, scanner.scan(node, env, path), ['comment_real.mod'])
        cached = node.includes
        with mock.patch.object(type(node), 'get_text_contents',
                               side_effect=AssertionError('cached scan reread source')):
            deps_match(self, scanner.scan(node, env, path), ['comment_real.mod'])
        self.assertIs(node.includes, cached)


if __name__ == "__main__":
    unittest.main()
