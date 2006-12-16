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

__doc__ = """
Generic Taskmaster module for the SCons build engine.

This module contains the primary interface(s) between a wrapping user
interface and the SCons build engine.  There are two key classes here:

    Taskmaster
        This is the main engine for walking the dependency graph and
        calling things to decide what does or doesn't need to be built.

    Task
        This is the base class for allowing a wrapping interface to
        decide what does or doesn't actually need to be done.  The
        intention is for a wrapping interface to subclass this as
        appropriate for different types of behavior it may need.

        The canonical example is the SCons native Python interface,
        which has Task subclasses that handle its specific behavior,
        like printing "`foo' is up to date" when a top-level target
        doesn't need to be built, and handling the -c option by removing
        targets as its "build" action.

        The Taskmaster instantiates a Task object for each (set of)
        target(s) that it decides need to be evaluated and/or built.
"""

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import string
import sys
import traceback

import SCons.Node
import SCons.Errors

StateString = SCons.Node.StateString

# A subsystem for recording stats about how different Nodes are handled by
# the main Taskmaster loop.  There's no external control here (no need for
# a --debug= option); enable it by changing the value of CollectStats.

CollectStats = None

class Stats:
    """
    A simple class for holding statistics about the disposition of a
    Node by the Taskmaster.  If we're collecting statistics, each Node
    processed by the Taskmaster gets one of these attached, in which
    the Taskmaster records its decision each time it processes the Node.
    (Ideally, that's just once per Node.)
    """
    def __init__(self):
        """
        Instantiates a Taskmaster.Stats object, initializing all
        appropriate counters to zero.
        """
        self.considered  = 0
        self.already_handled  = 0
        self.problem  = 0
        self.child_failed  = 0
        self.not_built  = 0
        self.side_effects  = 0
        self.build  = 0

StatsNodes = []

fmt = "%(considered)3d "\
      "%(already_handled)3d " \
      "%(problem)3d " \
      "%(child_failed)3d " \
      "%(not_built)3d " \
      "%(side_effects)3d " \
      "%(build)3d "

def dump_stats():
    StatsNodes.sort(lambda a, b: cmp(str(a), str(b)))
    for n in StatsNodes:
        print (fmt % n.stats.__dict__) + str(n)

class Task:
    """Default SCons build engine task.

    This controls the interaction of the actual building of node
    and the rest of the engine.

    This is expected to handle all of the normally-customizable
    aspects of controlling a build, so any given application
    *should* be able to do what it wants by sub-classing this
    class and overriding methods as appropriate.  If an application
    needs to customze something by sub-classing Taskmaster (or
    some other build engine class), we should first try to migrate
    that functionality into this class.

    Note that it's generally a good idea for sub-classes to call
    these methods explicitly to update state, etc., rather than
    roll their own interaction with Taskmaster from scratch."""
    def __init__(self, tm, targets, top, node):
        self.tm = tm
        self.targets = targets
        self.top = top
        self.node = node
        self.exc_clear()

    def display(self, message):
        """Allow the calling interface to display a message
        """
        pass

    def prepare(self):
        """Called just before the task is executed.

        This unlinks all targets and makes all directories before
        building anything."""

        # Now that it's the appropriate time, give the TaskMaster a
        # chance to raise any exceptions it encountered while preparing
        # this task.
        self.exception_raise()

        if self.tm.message:
            self.display(self.tm.message)
            self.tm.message = None

        for t in self.targets:
            t.prepare()
            for s in t.side_effects:
                s.prepare()

    def get_target(self):
        """Fetch the target being built or updated by this task.
        """
        return self.node

    def execute(self):
        """Called to execute the task.

        This method is called from multiple threads in a parallel build,
        so only do thread safe stuff here.  Do thread unsafe stuff in
        prepare(), executed() or failed()."""

        try:
            everything_was_cached = 1
            for t in self.targets:
                if not t.retrieve_from_cache():
                    everything_was_cached = 0
                    break
            if not everything_was_cached:
                self.targets[0].build()
        except KeyboardInterrupt:
            raise
        except SystemExit:
            exc_value = sys.exc_info()[1]
            raise SCons.Errors.ExplicitExit(self.targets[0], exc_value.code)
        except SCons.Errors.UserError:
            raise
        except SCons.Errors.BuildError:
            raise
        except:
            raise SCons.Errors.TaskmasterException(self.targets[0],
                                                   sys.exc_info())

    def executed(self):
        """Called when the task has been successfully executed.

        This may have been a do-nothing operation (to preserve
        build order), so check the node's state before updating
        things.  Most importantly, this calls back to the
        Taskmaster to put any node tasks waiting on this one
        back on the pending list."""
        for t in self.targets:
            if t.get_state() == SCons.Node.executing:
                t.set_state(SCons.Node.executed)
                t.built()
            else:
                t.visited()

        self.tm.executed(self.node)

    def failed(self):
        """Default action when a task fails:  stop the build."""
        self.fail_stop()

    def fail_stop(self):
        """Explicit stop-the-build failure."""
        for t in self.targets:
            t.set_state(SCons.Node.failed)
        self.tm.failed(self.node)
        self.tm.stop()

        # We're stopping because of a build failure, but give the
        # calling Task class a chance to postprocess() the top-level
        # target under which the build failure occurred.
        self.targets = [self.tm.current_top]
        self.top = 1

    def fail_continue(self):
        """Explicit continue-the-build failure.

        This sets failure status on the target nodes and all of
        their dependent parent nodes.
        """
        for t in self.targets:
            # Set failure state on all of the parents that were dependent
            # on this failed build.
            def set_state(node): node.set_state(SCons.Node.failed)
            t.call_for_all_waiting_parents(set_state)

        self.tm.executed(self.node)

    def make_ready_all(self):
        """Mark all targets in a task ready for execution.

        This is used when the interface needs every target Node to be
        visited--the canonical example being the "scons -c" option.
        """
        self.out_of_date = self.targets[:]
        for t in self.targets:
            t.disambiguate().set_state(SCons.Node.executing)
            for s in t.side_effects:
                s.set_state(SCons.Node.executing)

    def make_ready_current(self):
        """Mark all targets in a task ready for execution if any target
        is not current.

        This is the default behavior for building only what's necessary.
        """
        self.out_of_date = []
        for t in self.targets:
            if t.disambiguate().current():
                t.set_state(SCons.Node.up_to_date)
            else:
                self.out_of_date.append(t)
                t.set_state(SCons.Node.executing)
                for s in t.side_effects:
                    s.set_state(SCons.Node.executing)

    make_ready = make_ready_current

    def postprocess(self):
        """Post process a task after it's been executed."""
        parents = {}
        for t in self.targets:
            for p in t.waiting_parents.keys():
                parents[p] = parents.get(p, 0) + 1
        for t in self.targets:
            for s in t.side_effects:
                if s.get_state() == SCons.Node.executing:
                    s.set_state(SCons.Node.no_state)
                    for p in s.waiting_parents.keys():
                        if not parents.has_key(p):
                            parents[p] = 1
                for p in s.waiting_s_e.keys():
                    if p.ref_count == 0:
                        self.tm.candidates.append(p)
        for p, subtract in parents.items():
            p.ref_count = p.ref_count - subtract
            if p.ref_count == 0:
                self.tm.candidates.append(p)
        for t in self.targets:
            t.postprocess()

    def exc_info(self):
        return self.exception

    def exc_clear(self):
        self.exception = (None, None, None)
        self.exception_raise = self._no_exception_to_raise

    def exception_set(self, exception=None):
        if not exception:
            exception = sys.exc_info()
        self.exception = exception
        self.exception_raise = self._exception_raise

    def _no_exception_to_raise(self):
        pass

    def _exception_raise(self):
        """Raise a pending exception that was recorded while
        getting a Task ready for execution."""
        self.tm.exception_raise(self.exc_info())


def order(dependencies):
    """Re-order a list of dependencies (if we need to)."""
    return dependencies


def find_cycle(stack):
    if stack[0] == stack[-1]:
        return stack
    for n in stack[-1].waiting_parents.keys():
        stack.append(n)
        if find_cycle(stack):
            return stack
        stack.pop()
    return None


class Taskmaster:
    """A generic Taskmaster for handling a bunch of targets.

    Classes that override methods of this class should call
    the base class method, so this class can do its thing.
    """

    def __init__(self, targets=[], tasker=Task, order=order, trace=None):
        self.top_targets = targets[:]
        self.top_targets.reverse()
        self.candidates = []
        self.tasker = tasker
        self.ready = None # the next task that is ready to be executed
        self.order = order
        self.message = None
        self.trace = trace
        self.next_candidate = self.find_next_candidate

    def find_next_candidate(self):
        try:
            return self.candidates.pop()
        except IndexError:
            pass
        try:
            node = self.top_targets.pop()
        except IndexError:
            return None
        self.current_top = node
        alt, message = node.alter_targets()
        if alt:
            self.message = message
            self.candidates.append(node)
            self.candidates.extend(self.order(alt))
            node = self.candidates.pop()
        return node

    def no_next_candidate(self):
        return None

    def _find_next_ready_node(self):
        """Find the next node that is ready to be built"""

        if self.ready:
            return

        self.ready_exc = None

        T = self.trace

        while 1:
            node = self.next_candidate()
            if node is None:
                self.ready = None
                break

            node = node.disambiguate()
            state = node.get_state()

            if CollectStats:
                if not hasattr(node, 'stats'):
                    node.stats = Stats()
                    StatsNodes.append(node)
                S = node.stats
                S.considered = S.considered + 1
            else:
                S = None

            if T: T.write('Taskmaster: %s:' % repr(str(node)))

            # Skip this node if it has already been evaluated:
            if state > SCons.Node.pending:
                if S: S.already_handled = S.already_handled + 1
                if T: T.write(' already handled (%s)\n' % StateString[state])
                continue

            # Mark this node as being on the execution stack:
            node.set_state(SCons.Node.pending)

            try:
                children = node.children()
            except SystemExit:
                exc_value = sys.exc_info()[1]
                e = SCons.Errors.ExplicitExit(node, exc_value.code)
                self.ready_exc = (SCons.Errors.ExplicitExit, e)
                self.ready = node
                if T: T.write(' SystemExit\n')
                break
            except KeyboardInterrupt:
                if T: T.write(' KeyboardInterrupt\n')
                raise
            except:
                # We had a problem just trying to figure out the
                # children (like a child couldn't be linked in to a
                # BuildDir, or a Scanner threw something).  Arrange to
                # raise the exception when the Task is "executed."
                self.ready_exc = sys.exc_info()
                self.ready = node
                if S: S.problem = S.problem + 1
                if T: T.write(' exception\n')
                break

            if T and children:
                c = map(str, children)
                c.sort()
                T.write(' children:\n    %s\n   ' % c)

            childinfo = map(lambda N: (N.get_state(),
                                       N.is_derived() or N.is_pseudo_derived(),
                                       N), children)

            # Skip this node if any of its children have failed.  This
            # catches the case where we're descending a top-level target
            # and one of our children failed while trying to be built
            # by a *previous* descent of an earlier top-level target.
            failed_children = filter(lambda I: I[0] == SCons.Node.failed,
                                     childinfo)
            if failed_children:
                node.set_state(SCons.Node.failed)
                if S: S.child_failed = S.child_failed + 1
                if T:
                    c = map(str, failed_children)
                    c.sort()
                    T.write(' children failed:\n    %s\n' % c)
                continue

            # Detect dependency cycles:
            pending_nodes = filter(lambda I: I[0] == SCons.Node.pending, childinfo)
            if pending_nodes:
                for p in pending_nodes:
                    cycle = find_cycle([p[2], node])
                    if cycle:
                        desc = "Dependency cycle: " + string.join(map(str, cycle), " -> ")
                        if T: T.write(' dependency cycle\n')
                        raise SCons.Errors.UserError, desc

            # Select all of the dependencies that are derived targets
            # (that is, children who have builders or are side effects).
            derived_children = filter(lambda I: I[1], childinfo)

            not_started = filter(lambda I: not I[0], derived_children)
            if not_started:
                not_started = map(lambda I: I[2], not_started)

                # We're waiting on one more derived targets that have
                # not yet started building.  Add this node to the
                # waiting_parents lists of those derived files so that
                # when they've finished building, our implicit dependency
                # list will get cleared and we'll re-scan the newly-built
                # file(s) for updated implicit dependencies.
                map(lambda n, P=node: n.add_to_waiting_parents(P), not_started)
                node.ref_count = len(not_started)

                # Now we add these derived targets to the candidates
                # list so they can be examined and built.  We have to
                # add ourselves back to the list first, though, so we get
                # a chance to re-scan and build after the dependencies.
                #
                # We reverse the order in which the children are added
                # to the candidates stack so the order in which they're
                # popped matches the order in which they show up in our
                # children's list.  This is more logical / efficient for
                # builders with multiple targets, since the "primary"
                # target will be examined first.
                self.candidates.append(node)
                not_started.reverse()
                self.candidates.extend(self.order(not_started))

                if S: S.not_started = S.not_started + 1
                if T:
                    c = map(str, not_started)
                    c.sort()
                    T.write(' waiting on unstarted children:\n    %s\n' % c)
                continue

            not_built = filter(lambda I: I[0] <= SCons.Node.executing, derived_children)
            if not_built:
                not_built = map(lambda I: I[2], not_built)

                # We're waiting on one or more derived targets that have
                # started building but not yet finished.  Add this node
                # to the waiting parents lists of those derived files
                # so that when they've finished building, our implicit
                # dependency list will get cleared and we'll re-scan the
                # newly-built file(s) for updated implicit dependencies.
                map(lambda n, P=node: n.add_to_waiting_parents(P), not_built)
                node.ref_count = len(not_built)

                if S: S.not_built = S.not_built + 1
                if T:
                    c = map(str, not_built)
                    c.sort()
                    T.write(' waiting on unfinished children:\n    %s\n' % c)
                continue

            # Skip this node if it has side-effects that are currently being
            # built  themselves or waiting for something else being built.
            side_effects = filter(lambda N:
                                  N.get_state() == SCons.Node.executing,
                                  node.side_effects)
            if side_effects:
                map(lambda n, P=node: n.add_to_waiting_s_e(P), side_effects)
                if S: S.side_effects = S.side_effects + 1
                if T:
                    c = map(str, side_effects)
                    c.sort()
                    T.write(' waiting on side effects:\n    %s\n' % c)
                continue

            # The default when we've gotten through all of the checks above:
            # this node is ready to be built.
            self.ready = node
            if S: S.build = S.build + 1
            if T: T.write(' evaluating %s\n' % node)
            break

    def next_task(self):
        """Return the next task to be executed."""

        self._find_next_ready_node()

        node = self.ready

        if node is None:
            return None

        try:
            tlist = node.builder.targets(node)
        except AttributeError:
            tlist = [node]

        task = self.tasker(self, tlist, node is self.current_top, node)
        try:
            task.make_ready()
        except KeyboardInterrupt:
            raise
        except:
            # We had a problem just trying to get this task ready (like
            # a child couldn't be linked in to a BuildDir when deciding
            # whether this node is current).  Arrange to raise the
            # exception when the Task is "executed."
            self.ready_exc = sys.exc_info()

        if self.ready_exc:
            task.exception_set(self.ready_exc)

        self.ready = None
        self.ready_exc = None

        return task

    def stop(self):
        """Stop the current build completely."""
        self.next_candidate = self.no_next_candidate
        self.ready = None

    def failed(self, node):
        pass

    def executed(self, node):
        try:
            tlist = node.builder.targets(node)
        except AttributeError:
            tlist = [node]

    def exception_raise(self, exception):
        exc = exception[:]
        try:
            exc_type, exc_value, exc_traceback = exc
        except ValueError:
            exc_type, exc_value = exc
            exc_traceback = None
        raise exc_type, exc_value, exc_traceback
