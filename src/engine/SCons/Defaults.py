"""SCons.Defaults

Builders and other things for the local site.  Here's where we'll
duplicate the functionality of autoconf until we move it into the
installation procedure or use something like qmconf.

"""

#
# Copyright (c) 2001 Steven Knight
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



import SCons.Builder



Object = SCons.Builder.Builder(name = 'Object',
                               action = 'cc -c -o $target $sources',
                               input_suffix='.c',
                               output_suffix='.o')
Program = SCons.Builder.MultiStepBuilder(name = 'Program',
                                         action = 'cc -o $target $sources',
                                         builders = [ Object ])
Library = SCons.Builder.MultiStepBuilder(name = 'Library',
                                         action = 'ar r $target $sources\nranlib $target',
                                         builders = [ Object ])
  
Library = SCons.Builder.TargetNamingBuilder(builder = Library,
                                            prefix='lib',
                                            suffix='.a')

Builders = [Object, Program, Library]

ENV = { 'PATH' : '/usr/local/bin:/bin:/usr/bin' }
