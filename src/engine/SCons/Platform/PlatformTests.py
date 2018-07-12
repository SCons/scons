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

import SCons.compat

import collections
import unittest

import SCons.Errors
import SCons.Platform
import SCons.Environment
import SCons.Action

class Environment(collections.UserDict):
    def Detect(self, cmd):
        return cmd
    
    def AppendENVPath(self, key, value):
        pass

class PlatformTestCase(unittest.TestCase):
    def test_Platform(self):
        """Test the Platform() function"""
        p = SCons.Platform.Platform('cygwin')
        assert str(p) == 'cygwin', p
        env = Environment()
        p(env)
        assert env['PROGSUFFIX'] == '.exe', env
        assert env['LIBSUFFIX'] == '.a', env
        assert env['SHELL'] == 'sh', env

        p = SCons.Platform.Platform('os2')
        assert str(p) == 'os2', p
        env = Environment()
        p(env)
        assert env['PROGSUFFIX'] == '.exe', env
        assert env['LIBSUFFIX'] == '.lib', env

        p = SCons.Platform.Platform('posix')
        assert str(p) == 'posix', p
        env = Environment()
        p(env)
        assert env['PROGSUFFIX'] == '', env
        assert env['LIBSUFFIX'] == '.a', env
        assert env['SHELL'] == 'sh', env

        p = SCons.Platform.Platform('irix')
        assert str(p) == 'irix', p
        env = Environment()
        p(env)
        assert env['PROGSUFFIX'] == '', env
        assert env['LIBSUFFIX'] == '.a', env
        assert env['SHELL'] == 'sh', env

        p = SCons.Platform.Platform('aix')
        assert str(p) == 'aix', p
        env = Environment()
        p(env)
        assert env['PROGSUFFIX'] == '', env
        assert env['LIBSUFFIX'] == '.a', env
        assert env['SHELL'] == 'sh', env

        p = SCons.Platform.Platform('sunos')
        assert str(p) == 'sunos', p
        env = Environment()
        p(env)
        assert env['PROGSUFFIX'] == '', env
        assert env['LIBSUFFIX'] == '.a', env
        assert env['SHELL'] == 'sh', env

        p = SCons.Platform.Platform('hpux')
        assert str(p) == 'hpux', p
        env = Environment()
        p(env)
        assert env['PROGSUFFIX'] == '', env
        assert env['LIBSUFFIX'] == '.a', env
        assert env['SHELL'] == 'sh', env

        p = SCons.Platform.Platform('win32')
        assert str(p) == 'win32', p
        env = Environment()
        p(env)
        assert env['PROGSUFFIX'] == '.exe', env
        assert env['LIBSUFFIX'] == '.lib', env
        assert str

        try:
            p = SCons.Platform.Platform('_does_not_exist_')
        except SCons.Errors.UserError:
            pass
        else:
            raise

        env = Environment()
        SCons.Platform.Platform()(env)
        assert env != {}, env

class TempFileMungeTestCase(unittest.TestCase):
    def test_MAXLINELENGTH(self):
        """ Test different values for MAXLINELENGTH with the same
            size command string to ensure that the temp file mechanism
            kicks in only at MAXLINELENGTH+1, or higher
        """
        # Init class with cmd, such that the fully expanded
        # string reads "a test command line".
        # Note, how we're using a command string here that is
        # actually longer than the substituted one. This is to ensure
        # that the TempFileMunge class internally really takes the
        # length of the expanded string into account.
        defined_cmd = "a $VERY $OVERSIMPLIFIED line"
        t = SCons.Platform.TempFileMunge(defined_cmd)
        env = SCons.Environment.SubstitutionEnvironment(tools=[])
        # Setting the line length high enough...
        env['MAXLINELENGTH'] = 1024
        env['VERY'] = 'test'
        env['OVERSIMPLIFIED'] = 'command'
        expanded_cmd = env.subst(defined_cmd)
        # Call the tempfile munger
        cmd = t(None,None,env,0)
        assert cmd == defined_cmd, cmd
        # Let MAXLINELENGTH equal the string's length
        env['MAXLINELENGTH'] = len(expanded_cmd)
        cmd = t(None,None,env,0)
        assert cmd == defined_cmd, cmd
        # Finally, let the actual tempfile mechanism kick in
        # Disable printing of actions...
        old_actions = SCons.Action.print_actions
        SCons.Action.print_actions = 0
        env['MAXLINELENGTH'] = len(expanded_cmd)-1
        cmd = t(None,None,env,0)
        # ...and restoring its setting.
        SCons.Action.print_actions = old_actions
        assert cmd != defined_cmd, cmd

    def test_tempfilecreation_once(self):
        # Init class with cmd, such that the fully expanded
        # string reads "a test command line".
        # Note, how we're using a command string here that is
        # actually longer than the substituted one. This is to ensure
        # that the TempFileMunge class internally really takes the
        # length of the expanded string into account.
        defined_cmd = "a $VERY $OVERSIMPLIFIED line"
        t = SCons.Platform.TempFileMunge(defined_cmd)
        env = SCons.Environment.SubstitutionEnvironment(tools=[])
        # Setting the line length high enough...
        env['VERY'] = 'test'
        env['OVERSIMPLIFIED'] = 'command'
        expanded_cmd = env.subst(defined_cmd)
        env['MAXLINELENGTH'] = len(expanded_cmd)-1
        # Disable printing of actions...
        old_actions = SCons.Action.print_actions
        SCons.Action.print_actions = 0
        # Create an instance of object derived class to allow setattrb
        class Node(object) :
            class Attrs(object): 
                pass
            def __init__(self): 
                self.attributes = self.Attrs()
        target = [Node()]
        cmd = t(target, None, env, 0)
        # ...and restoring its setting.
        SCons.Action.print_actions = old_actions
        assert cmd != defined_cmd, cmd
        assert cmd == getattr(target[0].attributes, 'tempfile_cmdlist', None)

class PlatformEscapeTestCase(unittest.TestCase):
    def test_posix_escape(self):
        """  Check that paths with parens are escaped properly
        """
        import SCons.Platform.posix

        test_string = "/my (really) great code/main.cpp"
        output = SCons.Platform.posix.escape(test_string)

        # We expect the escape function to wrap the string
        # in quotes, but not escape any internal characters
        # in the test_string. (Parens doesn't require shell
        # escaping if their quoted)
        assert output[1:-1] == test_string


if __name__ == "__main__":
    unittest.main()
    

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
