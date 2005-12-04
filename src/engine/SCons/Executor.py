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

import string

from SCons.Debug import logInstanceCreation
import SCons.Util


class Executor:
    """A class for controlling instances of executing an action.

    This largely exists to hold a single association of an action,
    environment, list of environment override dictionaries, targets
    and sources for later processing as needed.
    """

    if SCons.Memoize.use_memoizer:
        __metaclass__ = SCons.Memoize.Memoized_Metaclass

    def __init__(self, action, env=None, overridelist=[{}],
                 targets=[], sources=[], builder_kw={}):
        if __debug__: logInstanceCreation(self, 'Executor.Executor')
        self.set_action_list(action)
        self.pre_actions = []
        self.post_actions = []
        self.env = env
        self.overridelist = overridelist
        self.targets = targets
        self.sources = sources[:]
        self.builder_kw = builder_kw

    def set_action_list(self, action):
        if not SCons.Util.is_List(action):
            if not action:
                raise SCons.Errors.UserError, "Executor must have an action."
            action = [action]
        self.action_list = action

    def get_action_list(self):
        return self.pre_actions + self.action_list + self.post_actions

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
        """Fetch the scanner path for this executor's targets
        and sources.
        """
        env = self.get_build_env()
        try:
            cwd = self.targets[0].cwd
        except (IndexError, AttributeError):
            cwd = None
        return scanner.path(env, cwd, self.targets, self.sources)

    def get_kw(self, kw={}):
        result = self.builder_kw.copy()
        result.update(kw)
        return result

    def do_nothing(self, target, exitstatfunc, kw):
        pass

    def do_execute(self, target, exitstatfunc, kw):
        """Actually execute the action list."""
        env = self.get_build_env()
        kw = self.get_kw(kw)
        for act in self.get_action_list():
            apply(act,
                  (self.targets, self.sources, env, exitstatfunc),
                  kw)

    # use extra indirection because with new-style objects (Python 2.2
    # and above) we can't override special methods, and nullify() needs
    # to be able to do this.

    def __call__(self, target, exitstatfunc, **kw):
        self.do_execute(target, exitstatfunc, kw)

    def cleanup(self):
        "__reset_cache__"
        pass

    def add_sources(self, sources):
        """Add source files to this Executor's list.  This is necessary
        for "multi" Builders that can be called repeatedly to build up
        a source file list for a given target."""
        slist = filter(lambda x, s=self.sources: x not in s, sources)
        self.sources.extend(slist)

    def add_pre_action(self, action):
        self.pre_actions.append(action)

    def add_post_action(self, action):
        self.post_actions.append(action)

    # another extra indirection for new-style objects and nullify...

    def my_str(self):
        env = self.get_build_env()
        get = lambda action, t=self.targets, s=self.sources, e=env: \
                     action.genstring(t, s, e)
        return string.join(map(get, self.get_action_list()), "\n")


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
        env = self.get_build_env()
        get = lambda action, t=self.targets, s=self.sources, e=env: \
                     action.get_contents(t, s, e)
        return string.join(map(get, self.get_action_list()), "")

    def get_timestamp(self):
        """Fetch a time stamp for this Executor.  We don't have one, of
        course (only files do), but this is the interface used by the
        timestamp module.
        """
        return 0

    def scan_targets(self, scanner):
        self.scan(scanner, self.targets)

    def scan_sources(self, scanner):
        self.scan(scanner, self.sources)

    def scan(self, scanner, node_list):
        """Scan a list of this Executor's files (targets or sources) for
        implicit dependencies and update all of the targets with them.
        This essentially short-circuits an N*M scan of the sources for
        each individual target, which is a hell of a lot more efficient.
        """
        env = self.get_build_env()
        select_specific_scanner = lambda t: (t[0], t[0].select_scanner(t[1]))
        remove_null_scanners = lambda t: not t[1] is None
        add_scanner_path = lambda t, s=self: \
                                  (t[0], t[1], s.get_build_scanner_path(t[1]))
        if scanner:
            scanner_list = map(lambda src, s=scanner: (src, s), node_list)
        else:
            kw = self.get_kw()
            get_initial_scanners = lambda src, e=env, kw=kw: \
                                          (src, src.get_scanner(e, kw))
            scanner_list = map(get_initial_scanners, node_list)
            scanner_list = filter(remove_null_scanners, scanner_list)

        scanner_list = map(select_specific_scanner, scanner_list)
        scanner_list = filter(remove_null_scanners, scanner_list)
        scanner_path_list = map(add_scanner_path, scanner_list)
        deps = []
        for node, scanner, path in scanner_path_list:
            deps.extend(node.get_implicit_deps(env, scanner, path))

        for tgt in self.targets:
            tgt.add_to_implicit(deps)

    def get_missing_sources(self):
        """
        __cacheable__
        """
        return filter(lambda s: s.missing(), self.sources)

    def get_unignored_sources(self, ignore):
        """__cacheable__"""
        sourcelist = self.sources
        if ignore:
            sourcelist = filter(lambda s, i=ignore: not s in i, sourcelist)
        return sourcelist

    def process_sources(self, func, ignore=[]):
        """__cacheable__"""
        return map(func, self.get_unignored_sources(ignore))


_Executor = Executor

class Null(_Executor):
    """A null Executor, with a null build Environment, that does
    nothing when the rest of the methods call it.

    This might be able to disapper when we refactor things to
    disassociate Builders from Nodes entirely, so we're not
    going to worry about unit tests for this--at least for now.
    """
    def __init__(self, *args, **kw):
        if __debug__: logInstanceCreation(self, 'Executor.Null')
        kw['action'] = []
        apply(_Executor.__init__, (self,), kw)
    def get_build_env(self):
        class NullEnvironment:
            def get_scanner(self, key):
                return None
        return NullEnvironment()
    def get_build_scanner_path(self):
        return None
    def cleanup(self):
        pass



if SCons.Memoize.use_old_memoization():
    _Base = Executor
    class Executor(SCons.Memoize.Memoizer, _Base):
        def __init__(self, *args, **kw):
            SCons.Memoize.Memoizer.__init__(self)
            apply(_Base.__init__, (self,)+args, kw)

