"""scons.Scanner

The Scanner package for the scons software construction utility.

"""

__revision__ = "Scanner/__init__.py __REVISION__ __DATE__ __DEVELOPER__"

__version__ = "__VERSION__"

class Scanner:

    def __init__(self, function):
        """
        Construct a new scanner object given a scanner function.

        The only argument to this method is a function taking two arguments
        and returning a list of strings. The functions first argument will
        be the name of a file that should be scanned for dependencies, the
        second argument will be an Environment object and
        the returned list of should contain the file names of all the
        direct dependencies of this file.

        Examples:

        s = Scanner(my_scanner_function)
        
        s = Scanner(function = my_scanner_function)

        """

        # Note: this class could easily work with scanner functions that take
        # something other than a filename as an argument (e.g. a database
        # node) and a dependencies list that aren't file names. All that
        # would need to be changed is the documentation.

        self.function = function

    def scan(self, filename, env):
        """
        This method does the actually scanning. 'filename' is the filename
        that will be passed to the scanner function, and 'env' is the
        environment that will be passed to the scanner function. A list of
        dependencies will be returned.
        """
        
        return self.function(filename, env)
        



