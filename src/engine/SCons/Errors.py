"""SCons.Errors

This file contains the exception classes used to handle internal
and user errors in SCons.

"""

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"



class BuildError(Exception):
    def __init__(self, node=None, stat=0, *args):
        self.node = node
        self.stat = stat
        self.args = args

class InternalError(Exception):
    def __init__(self, args=None):
        self.args = args

class UserError(Exception):
    def __init__(self, args=None):
        self.args = args
