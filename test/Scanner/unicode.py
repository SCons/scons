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
Verify that we can scan Unicode-encoded files for implicit
dependencies.
"""

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

try:
    unicode
except NameError:
    import sys
    msg = "Unicode not supported by Python version %s; skipping test\n"
    test.skip_test(msg % sys.version[:3])

import codecs

test.write('build.py', r"""
import codecs
import sys

# TODO(2.2):  Remove when 2.3 becomes the minimal supported version.
try:
    codecs.BOM_UTF8
except AttributeError:
    codecs.BOM_UTF8 = '\xef\xbb\xbf'
try:
    codecs.BOM_UTF16_LE
    codecs.BOM_UTF16_BE
except AttributeError:
    codecs.BOM_UTF16_LE = '\xff\xfe'
    codecs.BOM_UTF16_BE = '\xfe\xff'

try:
    ''.decode
except AttributeError:
    # 2.0 through 2.2:  strings have no .decode() method
    try:
        codecs.lookup('ascii').decode
    except AttributeError:
        # 2.0 and 2.1:  encodings are a tuple of functions, and the
        # decode() function returns a (result, length) tuple.
        def my_decode(contents, encoding):
            return codecs.lookup(encoding)[1](contents)[0]
    else:
        # 2.2:  encodings are an object with methods, and the .decode()
        # and .decode() returns just the decoded bytes.
        def my_decode(contents, encoding):
            return codecs.lookup(encoding).decode(contents)
else:
    # 2.3 or later:  use the .decode() string method
    def my_decode(contents, encoding):
        return contents.decode(encoding)

def process(outfp, infile):
    contents = open(infile, 'rb').read()
    if contents.startswith(codecs.BOM_UTF8):
        contents = contents[len(codecs.BOM_UTF8):]
        # TODO(2.2):  Remove when 2.3 becomes the minimal supported version.
        #contents = contents.decode('utf-8')
        contents = my_decode(contents, 'utf-8')
    elif contents.startswith(codecs.BOM_UTF16_LE):
        contents = contents[len(codecs.BOM_UTF16_LE):]
        # TODO(2.2):  Remove when 2.3 becomes the minimal supported version.
        #contents = contents.decode('utf-16-le')
        contents = my_decode(contents, 'utf-16-le')
    elif contents.startswith(codecs.BOM_UTF16_BE):
        contents = contents[len(codecs.BOM_UTF16_BE):]
        # TODO(2.2):  Remove when 2.3 becomes the minimal supported version.
        #contents = contents.decode('utf-16-be')
        contents = my_decode(contents, 'utf-16-be')
    for line in contents.split('\n')[:-1]:
        if line[:8] == 'include ':
            process(outfp, line[8:])
        elif line[:8] == 'getfile ':
            outfp.write('include ' + line[8:] + '\n')
            # note: converted, but not acted upon
        else:
            outfp.write(line + '\n')

output = open(sys.argv[2], 'wb')
process(output, sys.argv[1])

sys.exit(0)
""")

test.write('SConstruct', """
import re

include_re = re.compile(r'^include\s+(\S+)$', re.M)

def kfile_scan(node, env, scanpaths, arg):
    contents = node.get_text_contents()
    includes = include_re.findall(contents)
    return includes

kscan = Scanner(name = 'kfile',
                function = kfile_scan,
                argument = None,
                skeys = ['.k'],
                recursive = True)

env = Environment()
env.Append(SCANNERS = kscan)

env.Command('foo', 'foo.k', r'%(_python_)s build.py $SOURCES $TARGET')
""" % locals())

test.write('foo.k', """\
foo.k 1 line 1
include ascii.k
include utf8.k
include utf16le.k
include utf16be.k
foo.k 1 line 4
""")

contents = unicode("""\
ascii.k 1 line 1
include ascii.inc
ascii.k 1 line 3
""")
test.write('ascii.k', contents.encode('ascii'))

contents = unicode("""\
utf8.k 1 line 1
include utf8.inc
utf8.k 1 line 3
""")
test.write('utf8.k', codecs.BOM_UTF8 + contents.encode('utf-8'))

contents = unicode("""\
utf16le.k 1 line 1
include utf16le.inc
utf16le.k 1 line 3
""")
test.write('utf16le.k', codecs.BOM_UTF16_LE + contents.encode('utf-16-le'))

contents = unicode("""\
utf16be.k 1 line 1
include utf16be.inc
utf16be.k 1 line 3
""")
test.write('utf16be.k', codecs.BOM_UTF16_BE + contents.encode('utf-16-be'))

test.write('ascii.inc', "ascii.inc 1\n")
test.write('utf8.inc', "utf8.inc 1\n")
test.write('utf16le.inc', "utf16le.inc 1\n")
test.write('utf16be.inc', "utf16be.inc 1\n")

test.run(arguments='foo')

expect = """\
foo.k 1 line 1
ascii.k 1 line 1
ascii.inc 1
ascii.k 1 line 3
utf8.k 1 line 1
utf8.inc 1
utf8.k 1 line 3
utf16le.k 1 line 1
utf16le.inc 1
utf16le.k 1 line 3
utf16be.k 1 line 1
utf16be.inc 1
utf16be.k 1 line 3
foo.k 1 line 4
"""

test.must_match('foo', expect)

test.up_to_date(arguments='foo')



test.write('ascii.inc', "ascii.inc 2\n")

test.not_up_to_date(arguments = 'foo')

expect = """\
foo.k 1 line 1
ascii.k 1 line 1
ascii.inc 2
ascii.k 1 line 3
utf8.k 1 line 1
utf8.inc 1
utf8.k 1 line 3
utf16le.k 1 line 1
utf16le.inc 1
utf16le.k 1 line 3
utf16be.k 1 line 1
utf16be.inc 1
utf16be.k 1 line 3
foo.k 1 line 4
"""

test.must_match('foo', expect)

test.up_to_date(arguments = 'foo')



test.write('utf8.inc', "utf8.inc 2\n")

test.not_up_to_date(arguments = 'foo')

expect = """\
foo.k 1 line 1
ascii.k 1 line 1
ascii.inc 2
ascii.k 1 line 3
utf8.k 1 line 1
utf8.inc 2
utf8.k 1 line 3
utf16le.k 1 line 1
utf16le.inc 1
utf16le.k 1 line 3
utf16be.k 1 line 1
utf16be.inc 1
utf16be.k 1 line 3
foo.k 1 line 4
"""

test.must_match('foo', expect)

test.up_to_date(arguments = 'foo')



test.write('utf16le.inc', "utf16le.inc 2\n")

test.not_up_to_date(arguments = 'foo')

expect = """\
foo.k 1 line 1
ascii.k 1 line 1
ascii.inc 2
ascii.k 1 line 3
utf8.k 1 line 1
utf8.inc 2
utf8.k 1 line 3
utf16le.k 1 line 1
utf16le.inc 2
utf16le.k 1 line 3
utf16be.k 1 line 1
utf16be.inc 1
utf16be.k 1 line 3
foo.k 1 line 4
"""

test.must_match('foo', expect)

test.up_to_date(arguments = 'foo')



test.write('utf16be.inc', "utf16be.inc 2\n")

test.not_up_to_date(arguments = 'foo')

expect = """\
foo.k 1 line 1
ascii.k 1 line 1
ascii.inc 2
ascii.k 1 line 3
utf8.k 1 line 1
utf8.inc 2
utf8.k 1 line 3
utf16le.k 1 line 1
utf16le.inc 2
utf16le.k 1 line 3
utf16be.k 1 line 1
utf16be.inc 2
utf16be.k 1 line 3
foo.k 1 line 4
"""

test.must_match('foo', expect)

test.up_to_date(arguments = 'foo')



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
