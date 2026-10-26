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

"""Dependency scanner for Fortran code."""

import re

import SCons.Node
import SCons.Node.FS
import SCons.Util
import SCons.Warnings
from . import Classic, Current, FindPathDirs

class F90Scanner(Classic):
    """
    A Classic Scanner subclass for Fortran source files which takes
    into account both USE and INCLUDE statements.  This scanner will
    work for both F77 and F90 (and beyond) compilers.

    Currently, this scanner assumes that the include files do not contain
    USE statements.  To enable the ability to deal with USE statements
    in include files, add logic right after the module names are found
    to loop over each include file, search for and locate each USE
    statement, and append each module name to the list of dependencies.
    Caching the search results in a common dictionary somewhere so that
    the same include file is not searched multiple times would be a
    smart thing to do.
    """

    def __init__(self, name, suffixes, path_variable,
                 use_regex, incl_regex, def_regex, *args, **kwargs) -> None:

        self.cre_use = re.compile(use_regex, re.M)
        self.cre_incl = re.compile(incl_regex, re.M)
        self.cre_def = re.compile(def_regex, re.M)

        def _scan(node, env, path, self=self):
            node = node.rfile()

            if not node.exists():
                return []

            return self.scan(node, env, path)

        kwargs['function'] = _scan
        kwargs['path_function'] = FindPathDirs(path_variable)
        kwargs['recursive'] = 1
        kwargs['skeys'] = suffixes
        kwargs['name'] = name

        # bypasses the parent Classic initializer
        Current.__init__(self, *args, **kwargs)

    def _strip_comments(self, contents):
        """Remove ! comments without changing character literals or include paths.

        The scanner does not know the source form. Leave ! in column 6 alone,
        since it can be a fixed-form continuation marker.
        """
        lines = []
        quote = None
        continued = False
        for line in contents.splitlines(keepends=True):
            newline = line[len(line.rstrip('\r\n')):]
            if not line.strip() or (
                line.lstrip().startswith('!') and line.index('!') != 5
            ):
                lines.append(newline)
                continue
            if quote and not continued and line[:1] in ('c', 'C', '*'):
                lines.append(line)
                continue

            fixed_continuation = (
                len(line) > 5
                and not line[:5].strip(' 0123456789')
                and line[5] not in ' 0\r\n'
            )
            if not (continued or fixed_continuation):
                quote = None

            # Preserve the angle-bracket include syntax supported by Absoft.
            include_paths = []
            if '<' in line and '!' in line:
                include_paths = [
                    match.span(1) for match in self.cre_incl.finditer(line)
                    if line[match.start(1) - 1] == '<'
                ]
            for index, char in enumerate(line):
                if fixed_continuation and index == 5:
                    # Quotes can be fixed-form markers, but can also start a
                    # literal in a free-form statement continued after &.
                    if char == '!' or (
                        char in "'\"" and (quote is not None or not continued)
                    ):
                        continue
                if quote:
                    # Doubled delimiters toggle twice, keeping the literal open.
                    if char == quote:
                        quote = None
                elif char in "'\"":
                    quote = char
                elif char == '!':
                    if any(start <= index < end for start, end in include_paths):
                        continue
                    line = line[:index] + newline
                    break

            continued = line.rstrip().endswith('&')
            # A column-one fixed-form comment must not open a character literal
            # on a following continuation line.
            if not continued and line[:1] in ('c', 'C', '*'):
                quote = None
            lines.append(line)
        return ''.join(lines)

    def scan(self, node, env, path=()):

        # cache the includes list in node so we only scan it once:
        if node.includes is not None:
            mods_and_includes = node.includes
        else:
            contents = self._strip_comments(node.get_text_contents())
            # retrieve all included filenames
            includes = self.cre_incl.findall(contents)
            # retrieve all USE'd module names
            modules = self.cre_use.findall(contents)
            # retrieve all defined module names
            defmodules = self.cre_def.findall(contents)

            # Remove all USE'd module names that are defined in the same file
            # (case-insensitively)
            d = {}
            for m in defmodules:
                d[m.lower()] = 1
            modules = [m for m in modules if m.lower() not in d]

            # Convert module name to a .mod filename
            suffix = env.subst('$FORTRANMODSUFFIX')
            modules = [x.lower() + suffix for x in modules]
            # Remove unique items from the list
            mods_and_includes = SCons.Util.unique(includes+modules)
            node.includes = mods_and_includes

        # This is a hand-coded DSU (decorate-sort-undecorate, or
        # Schwartzian transform) pattern.  The sort key is the raw name
        # of the file as specifed on the USE or INCLUDE line, which lets
        # us keep the sort order constant regardless of whether the file
        # is actually found in a Repository or locally.
        nodes = []
        source_dir = node.get_dir()
        if callable(path):
            path = path()
        for dep in mods_and_includes:
            n, i = self.find_include(dep, source_dir, path)

            if n is None:
                SCons.Warnings.warn(SCons.Warnings.DependencyWarning,
                                    "No dependency generated for file: %s (referenced by: %s) -- file not found" % (i, node))
            else:
                sortkey = self.sort_key(dep)
                nodes.append((sortkey, n))

        return [pair[1] for pair in sorted(nodes)]

def FortranScan(path_variable: str="FORTRANPATH"):
    """Return a prototype Scanner instance for scanning source files
    for Fortran USE & INCLUDE statements"""

#   The USE statement regex matches the following:
#
#   USE module_name
#   USE :: module_name
#   USE, INTRINSIC :: module_name
#   USE, NON_INTRINSIC :: module_name
#
#   Limitations
#
#   --  I question whether or not we need to detect dependencies to
#       INTRINSIC modules because these are built-in to the compiler.
#       If we consider them a dependency, will SCons look for them, not
#       find them, and kill the build?  Or will we there be standard
#       compiler-specific directories we will need to point to so the
#       compiler and SCons can locate the proper object and mod files?

#   Here is a breakdown of the regex:
#
#   (?i)               : regex is case insensitive
#   ^                  : start of line
#   (?:                : group a collection of regex symbols without saving the match as a "group"
#      ^|;             : matches either the start of the line or a semicolon - semicolon
#   )                  : end the unsaved grouping
#   \s*                : any amount of white space
#   USE                : match the string USE, case insensitive
#   (?:                : group a collection of regex symbols without saving the match as a "group"
#      \s+|            : match one or more whitespace OR ....  (the next entire grouped set of regex symbols)
#      (?:             : group a collection of regex symbols without saving the match as a "group"
#         (?:          : establish another unsaved grouping of regex symbols
#            \s*          : any amount of white space
#            ,         : match a comma
#            \s*       : any amount of white space
#            (?:NON_)? : optionally match the prefix NON_, case insensitive
#            INTRINSIC : match the string INTRINSIC, case insensitive
#         )?           : optionally match the ", INTRINSIC/NON_INTRINSIC" grouped expression
#         \s*          : any amount of white space
#         ::           : match a double colon that must appear after the INTRINSIC/NON_INTRINSIC attribute
#      )               : end the unsaved grouping
#   )                  : end the unsaved grouping
#   \s*                : match any amount of white space
#   (\w+)              : match the module name that is being USE'd
#
#
    use_regex = r"(?i)(?:^|;)\s*USE(?:\s+|(?:(?:\s*,\s*(?:NON_)?INTRINSIC)?\s*::))\s*(\w+)"


#   The INCLUDE statement regex matches the following:
#
#   INCLUDE 'some_Text'
#   INCLUDE "some_Text"
#   INCLUDE "some_Text" ; INCLUDE "some_Text"
#   INCLUDE kind_"some_Text"
#   INCLUDE kind_'some_Text"
#
#   where some_Text can include any alphanumeric and/or special character
#   as defined by the Fortran 2003 standard.
#
#   Limitations:
#
#   --  The Fortran standard dictates that a " or ' in the INCLUDE'd
#       string must be represented as a "" or '', if the quotes that wrap
#       the entire string are either a ' or ", respectively.   While the
#       regular expression below can detect the ' or " characters just fine,
#       the scanning logic, presently is unable to detect them and reduce
#       them to a single instance.  This probably isn't an issue since,
#       in practice, ' or " are not generally used in filenames.
#
#   Here is a breakdown of the regex:
#
#   (?i)               : regex is case insensitive
#   (?:                : begin a non-saving group that matches the following:
#      ^               :    either the start of the line
#      |               :                or
#      ['">]\s*;       :    a semicolon that follows a single quote,
#                           double quote or greater than symbol (with any
#                           amount of whitespace in between).  This will
#                           allow the regex to match multiple INCLUDE
#                           statements per line (although it also requires
#                           the positive lookahead assertion that is
#                           used below).  It will even properly deal with
#                           (i.e. ignore) cases in which the additional
#                           INCLUDES are part of an in-line comment, ala
#                                           "  INCLUDE 'someFile' ! ; INCLUDE 'someFile2' "
#   )                  : end of non-saving group
#   \s*                : any amount of white space
#   INCLUDE            : match the string INCLUDE, case insensitive
#   \s+                : match one or more white space characters
#   (?\w+_)?           : match the optional "kind-param _" prefix allowed by the standard
#   [<"']              : match the include delimiter - an apostrophe, double quote, or less than symbol
#   (.+?)              : match one or more characters that make up
#                        the included path and file name and save it
#                        in a group.  The Fortran standard allows for
#                        any non-control character to be used.  The dot
#                        operator will pick up any character, including
#                        control codes, but I can't conceive of anyone
#                        putting control codes in their file names.
#                        The question mark indicates it is non-greedy so
#                        that regex will match only up to the next quote,
#                        double quote, or greater than symbol
#   (?=["'>])          : positive lookahead assertion to match the include
#                        delimiter - an apostrophe, double quote, or
#                        greater than symbol.  This level of complexity
#                        is required so that the include delimiter is
#                        not consumed by the match, thus allowing the
#                        sub-regex discussed above to uniquely match a
#                        set of semicolon-separated INCLUDE statements
#                        (as allowed by the F2003 standard)

    include_regex = r"""(?i)(?:^|['">]\s*;)\s*INCLUDE\s+(?:\w+_)?[<"'](.+?)(?=["'>])"""

#   The MODULE statement regex finds module definitions by matching
#   the following:
#
#   MODULE module_name
#
#   but *not* the following:
#
#   MODULE PROCEDURE procedure_name
#   MODULE SUBROUTINE subroutine_name
#   MODULE FUNCTION function_name
#   MODULE PURE SUBROUTINE|FUNCTION subroutine_name|function_name
#   MODULE ELEMENTAL SUBROUTINE|FUNCTION subroutine_name|function_name
#
#   Here is a breakdown of the regex:
#
#   (?i)                               : regex is case insensitive
#   ^\s*                               : any amount of white space
#   MODULE                             : match the string MODULE, case
#                                        insensitive
#   \s+                                : match one or more white space
#                                        characters
#   (?!PROCEDURE|SUBROUTINE|FUNCTION|PURE|ELEMENTAL)
#                                      : but *don't* match if the next word
#                                        matches PROCEDURE, SUBROUTINE,
#                                        FUNCTION, PURE or ELEMENTAL (negative
#                                        lookahead assertion), case insensitive
#   (\w+)                              : match one or more alphanumeric
#                                        characters that make up the defined
#                                        module name and save it in a group

    def_regex = r"""(?i)^\s*MODULE\s+(?!PROCEDURE|SUBROUTINE|FUNCTION|PURE|ELEMENTAL)(\w+)"""

    scanner = F90Scanner("FortranScan",
                         "$FORTRANSUFFIXES",
                         path_variable,
                         use_regex,
                         include_regex,
                         def_regex)
    return scanner
