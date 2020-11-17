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
Test the ability to use a explicit target package name and the use
of FindInstalledFiles() in conjunction with .msi packages.
"""

import TestSCons

python = TestSCons.python

test = TestSCons.TestSCons()

try:
    from xml.dom.minidom import parse
except ImportError:
    test.skip_test('Canoot import xml.dom.minidom skipping test\n')

wix = test.Environment().WhereIs('candle')

if not wix:
    test.skip_test("No 'candle' found; skipping test\n")

#
# build with minimal tag set and test for the given package meta-data
#
test.write( 'file1.exe', "file1" )
test.write( 'file2.exe', "file2" )

test.write('SConstruct', """
import os

env  = Environment(tools=['default', 'packaging'])

f1  = env.Install( '/usr/' , 'file1.exe'  )
f2  = env.Install( '/usr/' , 'file2.exe'  )

env.Alias( 'install', [ f1, f2 ] )

env.Package( NAME         = 'foo',
             VERSION      = '1.2',
             PACKAGETYPE  = 'msi',
             SUMMARY      = 'balalalalal',
             DESCRIPTION  = 'this should be reallly really long',
             VENDOR       = 'Nanosoft_2000',
             source       = env.FindInstalledFiles(),
             target       = "mypackage.msi",
            )
""")

test.run(arguments='', stderr = None)

test.must_exist( 'foo-1.2.wxs' )
test.must_exist( 'foo-1.2.msi' )

dom     = parse( test.workpath( 'foo-1.2.wxs' ) )
Product = dom.getElementsByTagName( 'Product' )[0]
Package = dom.getElementsByTagName( 'Package' )[0]

test.fail_test( not Product.attributes['Manufacturer'].value == 'Nanosoft_2000' )
test.fail_test( not Product.attributes['Version'].value      == '1.2' )
test.fail_test( not Product.attributes['Name'].value         == 'foo' )

test.fail_test( not Package.attributes['Description'].value == 'balalalalal' )
test.fail_test( not Package.attributes['Comments'].value    == 'this should be reallly really long' )

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
