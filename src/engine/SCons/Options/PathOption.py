"""engine.SCons.Options.PathOption

This file defines an option type for SCons implementing 'package
activation'.

To be used whenever a 'package' may be enabled/disabled and the
package path may be specified.

Usage example:

  Examples:
      x11=no   (disables X11 support)
      x11=yes  (will search for the package installation dir)
      x11=/usr/local/X11 (will check this path for existance)

  To replace autoconf's --with-xxx=yyy 

  opts = Options()

  opts = Options()
  opts.Add(PathOption('qtdir',
                      'where the root of Qt is installed',
                      qtdir))
  opts.Add(PathOption('qt_includes',
                      'where the Qt includes are installed',
                      '$qtdir/includes'))
  opts.Add(PathOption('qt_libraries',
                      'where the Qt library is installed',
                      '$qtdir/lib'))

"""

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

import os
import os.path

import SCons.Errors

class _PathOptionClass:

    def PathIsDir(self, key, val, env):
        """Validator to check if Path is a directory."""
        if not os.path.isdir(val):
            if os.path.isfile(val):
                m = 'Directory path for option %s is a file: %s'
            else:
                m = 'Directory path for option %s does not exist: %s'
            raise SCons.Errors.UserError(m % (key, val))

    def PathIsDirCreate(self, key, val, env):
        """Validator to check if Path is a directory,
           creating it if it does not exist."""
        if os.path.isfile(val):
            m = 'Path for option %s is a file, not a directory: %s'
            raise SCons.Errors.UserError(m % (key, val))
        if not os.path.isdir(val):
            os.makedirs(val)

    def PathIsFile(self, key, val, env):
        """validator to check if Path is a file"""
        if not os.path.isfile(val):
            if os.path.isdir(val):
                m = 'File path for option %s is a directory: %s'
            else:
                m = 'File path for option %s does not exist: %s'
            raise SCons.Errors.UserError(m % (key, val))

    def PathExists(self, key, val, env):
        """validator to check if Path exists"""
        if not os.path.exists(val):
            m = 'Path for option %s does not exist: %s'
            raise SCons.Errors.UserError(m % (key, val))

    def __call__(self, key, help, default, validator=None):
        # NB: searchfunc is currenty undocumented and unsupported
        """
        The input parameters describe a 'path list' option, thus they
        are returned with the correct converter and validator appended. The
        result is usable for input to opts.Add() .

        A 'package list' option may either be 'all', 'none' or a list of
        package names (seperated by space).

        validator is a validator, see this file for examples
        """
        if validator is None:
            validator = self.PathExists
        return (key, '%s ( /path/to/%s )' % (help, key), default,
                validator, None)

PathOption = _PathOptionClass()
