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

    This largely exists to hold a single association of a builder,
    environment, environment overrides, targets and sources for later
    processing as needed.
    """

    def __init__(self, builder, env, overrides, targets, sources):
        if __debug__: logInstanceCreation(self)
        self.builder = builder
        self.env = env
        self.overrides = overrides
        self.targets = targets
        self.sources = sources[:]

    def get_build_env(self):
        """Fetch or create the appropriate build Environment
        for this Executor.
        """
        try:
            return self.build_env
        except AttributeError:
            if self.env is None:
                # There was no Environment specifically associated with
                # this set of targets (which kind of implies that it
                # is--or they are--source files, but who knows...).
                # So use the environment associated with the Builder
                # itself.
                env = self.builder.env
            else:
                # The normal case:  use the Environment that was
                # used to specify how these targets will be built.
                env = self.env
            overrides = {}
            overrides.update(self.builder.overrides)
            overrides.update(self.overrides)
            try:
                generate_build_dict = self.targets[0].generate_build_dict
            except AttributeError:
                pass
            else:
                overrides.update(generate_build_dict())
            overrides.update(SCons.Util.subst_dict(self.targets, self.sources))
            self.build_env = env.Override(overrides)
            return self.build_env

    def get_action_list(self, target):
        """Fetch or create the appropriate action list (for this target).

        There is an architectural mistake here: we cache the action list
        for the Executor and re-use it regardless of which target is
        being asked for.  In practice, this doesn't seem to be a problem
        because executing the action list will update all of the targets
        involved, so only one target's pre- and post-actions will win,
        anyway.  This is probably a bug we should fix...
        """
        try:
            al = self.action_list
        except AttributeError:
            al = self.builder.action.get_actions()
            self.action_list = al
        # XXX shouldn't reach into node attributes like this
        return target.pre_actions + al + target.post_actions

    def __call__(self, target, func):
        """Actually execute the action list."""
        action_list = self.get_action_list(target)
        if not action_list:
            return
        env = self.get_build_env()
        for action in action_list:
            func(action, self.targets, self.sources, env)

    def cleanup(self):
        try:
            del self.build_env
        except AttributeError:
            pass

    def add_sources(self, sources):
        """Add source files to this Executor's list.  This is necessary
        for "multi" Builders that can be called repeatedly to build up
        a source file list for a given target."""
        slist = filter(lambda x, s=self.sources: x not in s, sources)
        self.sources.extend(slist)

    def get_raw_contents(self):
        """Fetch the raw signature contents.  This, along with
        get_contents(), is the real reason this class exists, so we can
        compute this once and cache it regardless of how many target or
        source Nodes there are.
        """
        try:
            return self.raw_contents
        except AttributeError:
            action = self.builder.action
            self.raw_contents = action.get_raw_contents(self.targets,
                                                        self.sources,
                                                        self.get_build_env())
            return self.raw_contents

    def get_contents(self):
        """Fetch the signature contents.  This, along with
        get_raw_contents(), is the real reason this class exists, so we
        can compute this once and cache it regardless of how many target
        or source Nodes there are.
        """
        try:
            return self.contents
        except AttributeError:
            action = self.builder.action
            self.contents = action.get_contents(self.targets,
                                                self.sources,
                                                self.get_build_env())
            return self.contents

    def get_timestamp(self):
        """Fetch a time stamp for this Executor.  We don't have one, of
        course (only files do), but this is the interface used by the
        timestamp module.
        """
        return 0
