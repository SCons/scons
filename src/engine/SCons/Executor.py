"""SCons.Executor

A module for executing actions with specific lists of target and source
Nodes.

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


from SCons.Debug import logInstanceCreation
import SCons.Util


class Executor:
    """A class for controlling instances of executing an action.

    This largely exists to hold a single association of an action,
    environment, list of environment override dictionaries, targets
    and sources for later processing as needed.
    """

    __metaclass__ = SCons.Memoize.Memoized_Metaclass

    def __init__(self, action, env=None, overridelist=[{}],
                 targets=[], sources=[], builder_kw={}):
        if __debug__: logInstanceCreation(self)
        if not action:
            raise SCons.Errors.UserError, "Executor must have an action."
        self.action = action
        self.env = env
        self.overridelist = overridelist
        self.targets = targets
        self.sources = sources[:]
        self.builder_kw = builder_kw

    def get_build_env(self):
        """Fetch or create the appropriate build Environment
        for this Executor.
        __cacheable__
        """
        # Create the build environment instance with appropriate
        # overrides.  These get evaluated against the current
        # environment's construction variables so that users can
        # add to existing values by referencing the variable in
        # the expansion.
        overrides = {}
        for odict in self.overridelist:
            overrides.update(odict)

        import SCons.Defaults
        env = self.env or SCons.Defaults.DefaultEnvironment()
        build_env = env.Override(overrides)

        return build_env

    def get_build_scanner_path(self, scanner):
        """
        __cacheable__
        """
        env = self.get_build_env()
        try:
            cwd = self.targets[0].cwd
        except (IndexError, AttributeError):
            cwd = None
        return scanner.path(env, cwd, self.targets, self.sources)

    def do_nothing(self, target, errfunc, kw):
        pass

    def do_execute(self, target, errfunc, kw):
        """Actually execute the action list."""
        kw = kw.copy()
        kw.update(self.builder_kw)
        apply(self.action, (self.targets, self.sources,
                            self.get_build_env(), errfunc), kw)

    # use extra indirection because with new-style objects (Python 2.2
    # and above) we can't override special methods, and nullify() needs
    # to be able to do this.
    
    def __call__(self, target, errfunc, **kw):
        self.do_execute(target, errfunc, kw)

    def cleanup(self):
        "__reset_cache__"
        pass

    def add_sources(self, sources):
        """Add source files to this Executor's list.  This is necessary
        for "multi" Builders that can be called repeatedly to build up
        a source file list for a given target."""
        slist = filter(lambda x, s=self.sources: x not in s, sources)
        self.sources.extend(slist)

    # another extra indirection for new-style objects and nullify...
    
    def my_str(self):
        return self.action.genstring(self.targets,
                                     self.sources,
                                     self.get_build_env())

    def __str__(self):
        "__cacheable__"
        return self.my_str()

    def nullify(self):
        "__reset_cache__"
        self.do_execute = self.do_nothing
        self.my_str     = lambda S=self: ''

    def get_contents(self):
        """Fetch the signature contents.  This, along with
        get_raw_contents(), is the real reason this class exists, so we
        can compute this once and cache it regardless of how many target
        or source Nodes there are.
        __cacheable__
        """
        return self.action.get_contents(self.targets,
                                        self.sources,
                                        self.get_build_env())

    def get_timestamp(self):
        """Fetch a time stamp for this Executor.  We don't have one, of
        course (only files do), but this is the interface used by the
        timestamp module.
        """
        return 0

    def scan(self, scanner):
        """Scan this Executor's source files for implicit dependencies
        and update all of the targets with them.  This essentially
        short-circuits an N^2 scan of the sources for each individual
        targets, which is a hell of a lot more efficient.
        """
        env = self.get_build_env()
        select_specific_scanner = lambda t: (t[0], t[1].select(t[0]))
        remove_null_scanners = lambda t: not t[1] is None
        add_scanner_path = lambda t, s=self: (t[0], t[1], s.get_build_scanner_path(t[1]))
        if scanner:
            initial_scanners = lambda src, s=scanner: (src, s)
        else:
            initial_scanners = lambda src, e=env: (src, e.get_scanner(src.scanner_key()))
        scanner_list = map(initial_scanners, self.sources)
        scanner_list = filter(remove_null_scanners, scanner_list)
        scanner_list = map(select_specific_scanner, scanner_list)
        scanner_list = filter(remove_null_scanners, scanner_list)
        scanner_path_list = map(add_scanner_path, scanner_list)
        deps = []
        for src, scanner, path in scanner_path_list:
            deps.extend(src.get_implicit_deps(env, scanner, path))

        for tgt in self.targets:
            tgt.add_to_implicit(deps)

if not SCons.Memoize.has_metaclass:
    _Base = Executor
    class Executor(SCons.Memoize.Memoizer, _Base):
        def __init__(self, *args, **kw):
            SCons.Memoize.Memoizer.__init__(self)
            apply(_Base.__init__, (self,)+args, kw)

