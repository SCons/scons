"""SCons.Taskmaster

Generic Taskmaster.

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
import sys
import traceback

import SCons.Node
import SCons.Errors

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
            exc_type, exc_value, exc_traceback = sys.exc_info()
            raise SCons.Errors.BuildError(self.targets[0],
                                          "Exception",
                                          exc_type,
                                          exc_value,
                                          exc_traceback)

    def get_target(self):
        """Fetch the target being built or updated by this task.
        """
        return self.node

    def executed(self):
        """Called when the task has been successfully executed.

        This may have been a do-nothing operation (to preserve
        build order), so check the node's state before updating
        things.  Most importantly, this calls back to the
        Taskmaster to put any node tasks waiting on this one
        back on the pending list."""

        if self.targets[0].get_state() == SCons.Node.executing:
            for t in self.targets:
                for side_effect in t.side_effects:
                    side_effect.set_state(None)
                t.set_state(SCons.Node.executed)
                t.built()
        else:
            for t in self.targets:
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
        next_top = self.tm.next_top_level_candidate()
        self.tm.stop()

        if next_top:
            # We're stopping because of a build failure, but give the
            # calling Task class a chance to postprocess() the top-level
            # target under which the build failure occurred.
            self.targets = [next_top]
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

    def mark_targets(self, state):
        for t in self.targets:
            t.set_state(state)

    def mark_targets_and_side_effects(self, state):
        for t in self.targets:
            for side_effect in t.side_effects:
                side_effect.set_state(state)
            t.set_state(state)

    def make_ready_all(self):
        """Mark all targets in a task ready for execution.

        This is used when the interface needs every target Node to be
        visited--the canonical example being the "scons -c" option.
        """
        self.out_of_date = self.targets[:]
        self.mark_targets_and_side_effects(SCons.Node.executing)

    def make_ready_current(self):
        """Mark all targets in a task ready for execution if any target
        is not current.

        This is the default behavior for building only what's necessary.
        """
        self.out_of_date = []
        for t in self.targets:
            if not t.current():
                self.out_of_date.append(t)
        if self.out_of_date:
            self.mark_targets_and_side_effects(SCons.Node.executing)
        else:
            self.mark_targets(SCons.Node.up_to_date)

    make_ready = make_ready_current

    def postprocess(self):
        """Post process a task after it's been executed."""
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


class Taskmaster:
    """A generic Taskmaster for handling a bunch of targets.

    Classes that override methods of this class should call
    the base class method, so this class can do its thing.
    """

    def __init__(self, targets=[], tasker=Task, order=order):
        self.targets = targets # top level targets
        self.candidates = targets[:] # nodes that might be ready to be executed
        self.candidates.reverse()
        self.executing = [] # nodes that are currently executing
        self.pending = [] # nodes that depend on a currently executing node
        self.tasker = tasker
        self.ready = None # the next task that is ready to be executed
        self.order = order
        self.message = None
        self.altered = []

    def _find_next_ready_node(self):
        """Find the next node that is ready to be built"""

        if self.ready:
            return

        self.ready_exc = None
        
        while self.candidates:
            node = self.candidates[-1]
            state = node.get_state()

            # Skip this node if it has already been executed:
            if state != None and state != SCons.Node.stack:
                self.candidates.pop()
                continue

            # Mark this node as being on the execution stack:
            node.set_state(SCons.Node.stack)

            try:
                children = node.children()
            except SystemExit:
                exc_value = sys.exc_info()[1]
                e = SCons.Errors.ExplicitExit(node, exc_value.code)
                self.ready_exc = (SCons.Errors.ExplicitExit, e)
                self.candidates.pop()
                self.ready = node
                break
            except KeyboardInterrupt:
                raise
            except:
                # We had a problem just trying to figure out the
                # children (like a child couldn't be linked in to a
                # BuildDir, or a Scanner threw something).  Arrange to
                # raise the exception when the Task is "executed."
                self.ready_exc = sys.exc_info()
                self.candidates.pop()
                self.ready = node
                break

            # Skip this node if any of its children have failed.  This
            # catches the case where we're descending a top-level target
            # and one of our children failed while trying to be built
            # by a *previous* descent of an earlier top-level target.
            def failed(node): return node.get_state() == SCons.Node.failed
            if filter(failed, children):
                node.set_state(SCons.Node.failed)
                self.candidates.pop()
                continue

            # Detect dependency cycles:
            def in_stack(node): return node.get_state() == SCons.Node.stack
            cycle = filter(in_stack, children)
            if cycle:
                nodes = filter(in_stack, self.candidates) + cycle
                nodes.reverse()
                desc = "Dependency cycle: " + string.join(map(str, nodes), " -> ")
                raise SCons.Errors.UserError, desc

            # Find all of the derived dependencies (that is,
            # children who have builders or are side effects):
            try:
                def derived_nodes(node): return node.is_derived() or node.is_pseudo_derived()
                derived = filter(derived_nodes, children)
            except KeyboardInterrupt:
                raise
            except:
                # We had a problem just trying to figure out if any of
                # the kids are derived (like a child couldn't be linked
                # from a repository).  Arrange to raise the exception
                # when the Task is "executed."
                self.ready_exc = sys.exc_info()
                self.candidates.pop()
                self.ready = node
                break

            # If this was a top-level argument and we haven't already
            # done so, see if we can alter the target list to find any
            # corresponding targets in linked build directories:
            if node in self.targets and node not in self.altered:
                alt, message = node.alter_targets()
                if alt:
                    self.message = message
                    self.candidates.extend(self.order(alt))
                    self.altered.append(node)
                    continue

            # Add derived files that have not been built
            # to the candidates list:
            def unbuilt_nodes(node): return node.get_state() == None
            not_built = filter(unbuilt_nodes, derived)
            if not_built:
                # We're waiting on one more derived files that have not
                # yet been built.  Add this node to the waiting_parents
                # list of each of those derived files.
                def add_to_waiting_parents(child, parent=node):
                    child.add_to_waiting_parents(parent)
                map(add_to_waiting_parents, not_built)
                not_built.reverse()
                self.candidates.extend(self.order(not_built))
                continue

            # Skip this node if it has side-effects that are
            # currently being built:
            cont = 0
            for side_effect in node.side_effects:
                if side_effect.get_state() == SCons.Node.executing:
                    self.pending.append(node)
                    node.set_state(SCons.Node.pending)
                    self.candidates.pop()
                    cont = 1
                    break
            if cont: continue

            # Skip this node if it is pending on a currently
            # executing node:
            if node.depends_on(self.executing) or node.depends_on(self.pending):
                self.pending.append(node)
                node.set_state(SCons.Node.pending)
                self.candidates.pop()
                continue

            # The default when we've gotten through all of the checks above:
            # this node is ready to be built.
            self.candidates.pop()
            self.ready = node
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
        self.executing.extend(tlist)
        self.executing.extend(node.side_effects)
        
        task = self.tasker(self, tlist, node in self.targets, node)
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

    def is_blocked(self):
        self._find_next_ready_node()

        return not self.ready and (self.pending or self.executing)

    def next_top_level_candidate(self):
        candidates = self.candidates[:]
        candidates.reverse()
        for c in candidates:
            if c in self.targets:
                return c
        return None

    def stop(self):
        """Stop the current build completely."""
        self.candidates = []
        self.ready = None
        self.pending = []

    def failed(self, node):
        try:
            tlist = node.builder.targets(node)
        except AttributeError:
            tlist = [node]
        for t in tlist:
            self.executing.remove(t)
        for side_effect in node.side_effects:
            self.executing.remove(side_effect)

    def executed(self, node):
        try:
            tlist = node.builder.targets(node)
        except AttributeError:
            tlist = [node]
        for t in tlist:
            self.executing.remove(t)
        for side_effect in node.side_effects:
            self.executing.remove(side_effect)

        # move the current pending nodes to the candidates list:
        # (they may not all be ready to build, but _find_next_ready_node()
        #  will figure out which ones are really ready)
        for node in self.pending:
            node.set_state(None)
        self.pending.reverse()
        self.candidates.extend(self.pending)
        self.pending = []

    def exception_raise(self, exception):
        exc = exception[:]
        try:
            exc_type, exc_value, exc_traceback = exc
        except ValueError:
            exc_type, exc_value = exc
            exc_traceback = None
        raise exc_type, exc_value, exc_traceback
