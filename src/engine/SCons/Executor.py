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
        try:
            generate_build_dict = self.targets[0].generate_build_dict
        except (AttributeError, IndexError):
            pass
        else:
            overrides.update(generate_build_dict())

        import SCons.Defaults
        env = self.env or SCons.Defaults.DefaultEnvironment()
        build_env = env.Override(overrides)

        # Update the overrides with the $TARGET/$SOURCE variables for
        # this target+source pair, so that evaluations of arbitrary
        # Python functions have them in the __env__ environment
        # they're passed.  Note that the underlying substitution
        # functions also override these with their own $TARGET/$SOURCE
        # expansions, which is *usually* duplicated effort, but covers
        # a corner case where an Action is called directly from within
        # a function action with different target and source lists.
        build_env._update(SCons.Util.subst_dict(self.targets, self.sources))

        return build_env

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

if not SCons.Memoize.has_metaclass:
    _Base = Executor
    class Executor(SCons.Memoize.Memoizer, _Base):
        def __init__(self, *args, **kw):
            SCons.Memoize.Memoizer.__init__(self)
            apply(_Base.__init__, (self,)+args, kw)

