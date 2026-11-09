#
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

"""Unit tests for the generic TeX source scanner selection in SCons.Tool.tex."""

import unittest

import SCons.Environment
import SCons.Scanner
import SCons.Scanner.LaTeX


def selected_scanner(env):
    """Return the concrete LaTeX scanner the environment uses for .tex files."""
    return env.get_scanner('.tex').select(env.File('main.tex'))


class LaTeXSourceScannerTestCase(unittest.TestCase):

    def test_no_scanner_without_tool(self) -> None:
        """A bare environment has no scanner for .tex files."""
        env = SCons.Environment.Environment(tools=[])
        assert env.get_scanner('.tex') is None

    def test_tex_tool_registers_one_scanner(self) -> None:
        """Loading the tex tool adds exactly one source scanner."""
        env = SCons.Environment.Environment(tools=[])
        before = len(env['SCANNERS'])
        env.Tool('tex')
        assert len(env['SCANNERS']) == before + 1
        assert selected_scanner(env).graphics_extensions == ['.eps', '.ps']

    def test_repeated_loads_do_not_duplicate(self) -> None:
        """Loading tex-family tools repeatedly does not grow SCANNERS."""
        env = SCons.Environment.Environment(tools=[])
        env.Tool('tex')
        count = len(env['SCANNERS'])
        for tool in ('tex', 'latex'):
            env.Tool(tool)
            assert len(env['SCANNERS']) == count
        env.Tool('pdftex')
        assert len(env['SCANNERS']) == count + 1
        env.Tool('pdflatex')
        assert len(env['SCANNERS']) == count + 1

    def test_tex_tool_uses_eps_graphics(self) -> None:
        """The tex tool scans for .eps/.ps graphics."""
        env = SCons.Environment.Environment(tools=['tex'])
        scanner = selected_scanner(env)
        assert scanner.name == 'LaTeXScanner', scanner.name
        assert scanner.graphics_extensions == ['.eps', '.ps'], scanner.graphics_extensions

    def test_pdflatex_tool_uses_raster_graphics(self) -> None:
        """The pdflatex tool scans for raster graphics."""
        env = SCons.Environment.Environment(tools=['pdflatex'])
        scanner = selected_scanner(env)
        assert scanner.name == 'PDFLaTeXScanner', scanner.name
        assert scanner.graphics_extensions == ['.png', '.jpg', '.gif', '.tif'], scanner.graphics_extensions

    def test_first_loaded_tool_wins(self) -> None:
        """When both families are loaded, the first one loaded supplies the scanner."""
        env = SCons.Environment.Environment(tools=['tex', 'pdflatex'])
        assert selected_scanner(env).name == 'LaTeXScanner'

        env = SCons.Environment.Environment(tools=['pdflatex', 'tex'])
        assert selected_scanner(env).name == 'PDFLaTeXScanner'

    def test_pdftex_matches_tex_family(self) -> None:
        """Loading pdftex after tex does not change the selected scanner."""
        env = SCons.Environment.Environment(tools=[])
        env.Tool('tex')
        env.Tool('pdftex')
        assert selected_scanner(env).name == 'LaTeXScanner'

    def test_latex_matches_tex_family(self) -> None:
        """Loading latex after tex does not change the selected scanner."""
        env = SCons.Environment.Environment(tools=['tex', 'latex'])
        assert selected_scanner(env).name == 'LaTeXScanner'

    def test_user_scanner_takes_precedence(self) -> None:
        """A user scanner prepended to SCANNERS wins over the tool scanners."""
        custom = SCons.Scanner.Base(function=lambda node, env, path: [], skeys=['.tex'])
        env = SCons.Environment.Environment(tools=[])
        env.Prepend(SCANNERS=[custom])
        env.Tool('tex')
        env.Tool('pdflatex')
        assert env.get_scanner('.tex') is custom

    def test_clone_keeps_selected_scanner(self) -> None:
        """Cloning an environment keeps its scanner, and a tool added to the clone does not leak back."""
        plain = SCons.Environment.Environment(tools=[], LATEXSUFFIXES=['.tex'])
        tex = SCons.Environment.Environment(tools=['tex'])
        pdf_clone = plain.Clone(tools=['pdflatex'])
        tex_clone = tex.Clone()

        assert plain.get_scanner('.tex') is None
        assert selected_scanner(pdf_clone).name == 'PDFLaTeXScanner'
        assert selected_scanner(tex).name == 'LaTeXScanner'
        assert selected_scanner(tex_clone).name == 'LaTeXScanner'


if __name__ == "__main__":
    unittest.main()
