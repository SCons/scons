"""engine.SCons.Options

This file defines the Options class that is used to add user-friendly customizable
variables to a scons build.
"""

#
# Copyright (c) 2001, 2002 Steven Knight
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
import os.path


class Options:
    """
    Holds all the options, updates the environment with the variables,
    and renders the help text.
    """
    def __init__(self, file=None):
        """
        file - [optional] the name of the customizable file.
        """

        self.options = []
        self.file = file

    def Add(self, key, help="", default=None, validater=None, converter=None):
        """
        Add an option.

        key - the name of the variable
        help - optional help text for the options
        default - optional default value
        validater - optional function that is called to validate the option's value
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
        if self.file and os.path.exists(self.file):
            execfile(self.file, values)

        # finally set the values specified on the command line
        values.update(args)

        # put the variables in the environment:
        for key in values.keys():
            env[key] = values[key]

        # Call the convert functions:
        for option in self.options:
            if option.converter:
                value = env.subst('${%s}'%option.key)
                try:
                    env[option.key] = option.converter(value)
                except ValueError, x:
                    raise SCons.Errors.UserError, 'Error converting option: %s\n%s'%(options.key, x)


        # Finally validate the values:
        for option in self.options:
            if option.validater:
                option.validater(option.key, env.subst('${%s}'%option.key))


    def GenerateHelpText(self, env):
        """
        Generate the help text for the options.

        env - an environment that is used to get the current values of the options.
        """

        help_text = ""

        for option in self.options:
            help_text = help_text + '\n%s: %s\n    default: %s\n    actual: %s\n'%(option.key, option.help, option.default, env.subst('${%s}'%option.key))

        return help_text

