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
Test the ability to create a simple msi package.
"""

import TestSCons

python = TestSCons.python

test = TestSCons.TestSCons()

try:
    from xml.dom.minidom import *
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
env  = Environment(tools=['default', 'packaging'])

f1  = env.Install( '/usr/' , 'file1.exe'  )
f2  = env.Install( '/usr/' , 'file2.exe'  )

env.Package( NAME         = 'foo',
             VERSION      = '1.2',
             PACKAGETYPE  = 'msi',
             SUMMARY      = 'balalalalal',
             DESCRIPTION  = 'this should be reallly really long',
             VENDOR       = 'Nanosoft_2000',
             source       = [ f1, f2 ],
            )

env.Alias( 'install', [ f1, f2 ] )
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

#
# build with file tags resulting in multiple components in the msi installer
#
test.write( 'file1.exe', "file1" )
test.write( 'file2.exe', "file2" )
test.write( 'file3.html', "file3" )
test.write( 'file4.dll', "file4" )
test.write( 'file5.dll', "file5" )

test.write('SConstruct', """
env = Environment(tools=['default', 'packaging'])
f1  = env.Install( '/usr/' , 'file1.exe'  )
f2  = env.Install( '/usr/' , 'file2.exe'  )
f3  = env.Install( '/usr/' , 'file3.html' )
f4  = env.Install( '/usr/' , 'file4.dll'  )
f5  = env.Install( '/usr/' , 'file5.dll'  )

env.Tag( f1, X_MSI_FEATURE = 'Java Part' )
env.Tag( f2, X_MSI_FEATURE = 'Java Part' )
env.Tag( f3, 'DOC' )
env.Tag( f4, X_MSI_FEATURE = 'default' )
env.Tag( f5, X_MSI_FEATURE = ('Another Feature', 'with a long description') )

env.Package( NAME        = 'foo',
             VERSION     = '1.2',
             PACKAGETYPE = 'msi',
             SUMMARY     = 'balalalalal',
             DESCRIPTION = 'this should be reallly really long',
             VENDOR      = 'Nanosoft_tx2000',
             source      = [ f1, f2, f3, f4, f5 ],
            )

env.Alias( 'install', [ f1, f2, f3, f4, f5 ] )
""")

test.run(arguments='', stderr = None)

test.must_exist( 'foo-1.2.wxs' )
test.must_exist( 'foo-1.2.msi' )

dom      = parse( test.workpath( 'foo-1.2.wxs' ) )
elements = dom.getElementsByTagName( 'Feature' )
test.fail_test( not elements[1].attributes['Title'].value == 'Main Part' )
test.fail_test( not elements[2].attributes['Title'].value == 'Documentation' )
test.fail_test( not elements[3].attributes['Title'].value == 'Another Feature' )
test.fail_test( not elements[3].attributes['Description'].value == 'with a long description' )
test.fail_test( not elements[4].attributes['Title'].value == 'Java Part' )



test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
