"""engine.SCons.Options

This file defines the Options class that is used to add user-friendly customizable
variables to a scons build.
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

import SCons.Errors
import SCons.Util
import os.path


class Options:
    """
    Holds all the options, updates the environment with the variables,
    and renders the help text.
    """
    def __init__(self, files=None):
        """
        files - [optional] List of option configuration files to load
            (backward compatibility) If a single string is passed it is 
                                     automatically placed in a file list
        """

        self.options = []
        self.files = None
        if SCons.Util.is_String(files):
           self.files = [ files ]
        elif files:
           self.files = files


    def Add(self, key, help="", default=None, validater=None, converter=None):
        """
        Add an option.

        key - the name of the variable
        help - optional help text for the options
        default - optional default value
        validater - optional function that is called to validate the option's value
                    Called with (key, value, environment)
        converter - optional function that is called to convert the option's value before
                    putting it in the environment.
        """

        class Option:
            pass

        option = Option()
        option.key = key
        option.help = help
        option.default = default
        option.validater = validater
        option.converter = converter
        option.should_save = 0

        self.options.append(option)

    def Update(self, env, args):
        """
        Update an environment with the option variables.

        env - the environment to update.
        args - the dictionary to get the command line arguments from.
        """

        values = {}

        # first set the defaults:
        for option in self.options:
            if not option.default is None:
                values[option.key] = option.default

        # next set the value specified in the options file
        if self.files:
           for filename in self.files:
              if os.path.exists(filename):
                 execfile(filename, values)

        # finally set the values specified on the command line
        values.update(args)
        
        # Update the should save state
        # This will mark options that have either been set on command line
        # or in a loaded option file
        # KeyError occurs when an option has default of None and has not been set
        for option in self.options:
            try:
                if values[option.key] != option.default:
                    option.should_save = 1
            except KeyError:
                pass

        # put the variables in the environment:
        # (don't copy over variables that are not declared
        #  as options)
        for option in self.options:
            try:
                env[option.key] = values[option.key]
            except KeyError:
                pass

        # Call the convert functions:
        for option in self.options:
            if option.converter:
                value = env.subst('${%s}'%option.key)
                try:
                    env[option.key] = option.converter(value)
                except ValueError, x:
                    raise SCons.Errors.UserError, 'Error converting option: %s\n%s'%(option.key, x)


        # Finally validate the values:
        for option in self.options:
            if option.validater:
                option.validater(option.key, env.subst('${%s}'%option.key), env)
                
    

    def Save(self, filename, env):
        """
        Saves all the options in the given file.  This file can
        then be used to load the options next run.  This can be used
        to create an option cache file.

        filename - Name of the file to save into
        env - the environment get the option values from
        """

        # Create the file and write out the header
        try:
            fh = open(filename, 'w')

            # Make an assignment in the file for each option within the environment
            # that was assigned a value other than the default.
            for option in self.options:
                try:
                    value = env[option.key]
                    if option.should_save:
                        fh.write('%s = \'%s\'\n' % (option.key, value))
                except KeyError:
                    pass

            fh.close()

        except IOError, x:
            raise SCons.Errors.UserError, 'Error writing options to file: %s\n%s' % (filename, x)

    def GenerateHelpText(self, env):
        """
        Generate the help text for the options.

        env - an environment that is used to get the current values of the options.
        """

        help_text = ""

        for option in self.options:
            help_text = help_text + '\n%s: %s\n    default: %s\n'%(option.key, option.help, option.default)
            if env.has_key(option.key):
                help_text = help_text + '    actual: %s\n'%env.subst('${%s}'%option.key)
            else:
                help_text = help_text + '    actual: None\n'

        return help_text

