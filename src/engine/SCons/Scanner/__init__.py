"""SCons.Scanner

The Scanner package for the SCons software construction utility.

"""

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

__version__ = "__VERSION__"

class _Null:
    pass

# This is used instead of None as a default argument value so None can be
# used as an actual argument value.
_null = _Null

class Scanner:

    def __init__(self, function, argument=_null):
        """
        Construct a new scanner object given a scanner function.

        'function' - a scanner function taking two or three arguments and
        returning a list of strings.

        'argument' - an optional argument that will be passed to the
        scanner function if it is given.

        The scanner function's first argument will be the name of a file
        that should be scanned for dependencies, the second argument will
        be an Environment object, the third argument will be the value
        passed into 'argument', and the returned list should contain the
        file names of all the direct dependencies of the file.

        Examples:

        s = Scanner(my_scanner_function)
        
        s = Scanner(function = my_scanner_function)

        s = Scanner(function = my_scanner_function, argument = 'foo')

        """

        # Note: this class could easily work with scanner functions that take
        # something other than a filename as an argument (e.g. a database
        # node) and a dependencies list that aren't file names. All that
        # would need to be changed is the documentation.

        self.function = function
        self.argument = argument

    def scan(self, filename, env):
        """
        This method does the actually scanning. 'filename' is the filename
        that will be passed to the scanner function, and 'env' is the
        environment that will be passed to the scanner function. A list of
        dependencies will be returned.
        """

        if not self.argument is _null:
            return self.function(filename, env, self.argument)
        else:
            return self.function(filename, env)
        



