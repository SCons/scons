"""SCons.Job

This module defines the Serial and Parallel classes that execute tasks to
complete a build. The Jobs class provides a higher level interface to start,
stop, and wait on jobs.

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

import SCons.compat
import SCons.Defaults
import SCons.Util

from collections import deque
import datetime

import os
import signal

import SCons.Errors

# The default stack size (in kilobytes) of the threads used to execute
# jobs in parallel.
#
# We use a stack size of 256 kilobytes. The default on some platforms
# is too large and prevents us from creating enough threads to fully
# parallelized the build. For example, the default stack size on linux
# is 8 MBytes.

explicit_stack_size = None
default_stack_size = 256

interrupt_msg = 'Build interrupted.'

display = SCons.Util.display


class InterruptState(object):
    def __init__(self):
        self.interrupted = False

    def set(self):
        self.interrupted = True

    def __call__(self):
        return self.interrupted


class Jobs(object):
    """An instance of this class initializes N jobs, and provides
    methods for starting, stopping, and waiting on all N jobs.
    """

    def __init__(self, num, taskmaster, parallel_v2):
        """
        Create 'num' jobs using the given taskmaster.

        If 'num' is 1 or less, then a serial job will be used,
        otherwise a parallel job with 'num' worker threads will
        be used.

        If 'parallel_v2' is True, use the newer, more aggressive parallel
        job scheduler.

        The 'num_jobs' attribute will be set to the actual number of jobs
        allocated.  If more than one job is requested but the Parallel
        class can't do it, it gets reset to 1.  Wrapping interfaces that
        care should check the value of 'num_jobs' after initialization.
        """

        self.job = None
        tm_owns_caching = False
        if num > 1:
            stack_size = explicit_stack_size
            if stack_size is None:
                stack_size = default_stack_size

            try:
                if parallel_v2:
                    self.job = ParallelV2(taskmaster, num, stack_size)
                    tm_owns_caching = True
                else:
                    self.job = Parallel(taskmaster, num, stack_size)
                self.num_jobs = num
            except NameError:
                pass
        if self.job is None:
            self.job = Serial(taskmaster)
            self.num_jobs = 1

        taskmaster.set_tm_owns_caching(tm_owns_caching)

    def run(self, postfunc=lambda: None):
        """Run the jobs.

        postfunc() will be invoked after the jobs has run. It will be
        invoked even if the jobs are interrupted by a keyboard
        interrupt (well, in fact by a signal such as either SIGINT,
        SIGTERM or SIGHUP). The execution of postfunc() is protected
        against keyboard interrupts and is guaranteed to run to
        completion."""
        self._setup_sig_handler()
        try:
            self.job.start()
        finally:
            postfunc()
            self._reset_sig_handler()

    def were_interrupted(self):
        """Returns whether the jobs were interrupted by a signal."""
        return self.job.interrupted()

    def _setup_sig_handler(self):
        """Setup an interrupt handler so that SCons can shutdown cleanly in
        various conditions:

          a) SIGINT: Keyboard interrupt
          b) SIGTERM: kill or system shutdown
          c) SIGHUP: Controlling shell exiting

        We handle all of these cases by stopping the taskmaster. It
        turns out that it's very difficult to stop the build process
        by throwing asynchronously an exception such as
        KeyboardInterrupt. For example, the python Condition
        variables (threading.Condition) and queues do not seem to be
        asynchronous-exception-safe. It would require adding a whole
        bunch of try/finally block and except KeyboardInterrupt all
        over the place.

        Note also that we have to be careful to handle the case when
        SCons forks before executing another process. In that case, we
        want the child to exit immediately.
        """
        def handler(signum, stack, self=self, parentpid=os.getpid()):
            if os.getpid() == parentpid:
                self.job.taskmaster.stop()
                self.job.interrupted.set()
            else:
                os._exit(2)

        self.old_sigint  = signal.signal(signal.SIGINT, handler)
        self.old_sigterm = signal.signal(signal.SIGTERM, handler)
        try:
            self.old_sighup = signal.signal(signal.SIGHUP, handler)
        except AttributeError:
            pass

    def _reset_sig_handler(self):
        """Restore the signal handlers to their previous state (before the
         call to _setup_sig_handler()."""

        signal.signal(signal.SIGINT, self.old_sigint)
        signal.signal(signal.SIGTERM, self.old_sigterm)
        try:
            signal.signal(signal.SIGHUP, self.old_sighup)
        except AttributeError:
            pass

class Serial(object):
    """This class is used to execute tasks in series, and is more efficient
    than Parallel, but is only appropriate for non-parallel builds. Only
    one instance of this class should be in existence at a time.

    This class is not thread safe.
    """

    def __init__(self, taskmaster):
        """Create a new serial job given a taskmaster.

        The taskmaster's next_task() method should return the next task
        that needs to be executed, or None if there are no more tasks. The
        taskmaster's executed() method will be called for each task when it
        is successfully executed, or failed() will be called if it failed to
        execute (e.g. execute() raised an exception)."""

        self.taskmaster = taskmaster
        self.interrupted = InterruptState()

    def start(self):
        """Start the job. This will begin pulling tasks from the taskmaster
        and executing them, and return when there are no more tasks. If a task
        fails to execute (i.e. execute() raises an exception), then the job will
        stop."""

        while True:
            task = self.taskmaster.next_task()

            if task is None:
                break

            try:
                task.prepare()
                if task.needs_execute():
                    task.execute()
            except Exception:
                if self.interrupted():
                    try:
                        raise SCons.Errors.BuildError(
                            task.targets[0], errstr=interrupt_msg)
                    except:
                        task.exception_set()
                else:
                    task.exception_set()

                # Let the failed() callback function arrange for the
                # build to stop if that's appropriate.
                task.failed()
            else:
                task.executed()

            task.postprocess()
        self.taskmaster.cleanup()


# Trap import failure so that everything in the Job module but the
# Parallel class (and its dependent classes) will work if the interpreter
# doesn't support threads.
try:
    import queue
    import threading
except ImportError:
    pass
else:
    class Worker(threading.Thread):
        """A worker thread waits on a task to be posted to its request queue,
        dequeues the task, executes it, and posts a tuple including the task
        and a boolean indicating whether the task executed successfully. """

        def __init__(self, requestQueue, resultsQueue, interrupted):
            threading.Thread.__init__(self)
            self.setDaemon(1)
            self.requestQueue = requestQueue
            self.resultsQueue = resultsQueue
            self.interrupted = interrupted
            self.start()

        def run(self):
            while True:
                task = self.requestQueue.get()

                if task is None:
                    # The "None" value is used as a sentinel by
                    # ThreadPool.cleanup().  This indicates that there
                    # are no more tasks, so we should quit.
                    break

                try:
                    if self.interrupted():
                        raise SCons.Errors.BuildError(
                            task.targets[0], errstr=interrupt_msg)
                    task.execute()
                except:
                    task.exception_set()
                    ok = False
                else:
                    ok = True

                self.resultsQueue.put((task, ok))

    class ThreadPool(object):
        """This class is responsible for spawning and managing worker threads."""

        def __init__(self, num, stack_size, interrupted):
            """Create the request and reply queues, and 'num' worker threads.

            One must specify the stack size of the worker threads. The
            stack size is specified in kilobytes.
            """
            self.requestQueue = queue.Queue(0)
            self.resultsQueue = queue.Queue(0)

            try:
                prev_size = threading.stack_size(stack_size*1024)
            except AttributeError as e:
                # Only print a warning if the stack size has been
                # explicitly set.
                if explicit_stack_size is not None:
                    msg = "Setting stack size is unsupported by this version of Python:\n    " + \
                        e.args[0]
                    SCons.Warnings.warn(SCons.Warnings.StackSizeWarning, msg)
            except ValueError as e:
                msg = "Setting stack size failed:\n    " + str(e)
                SCons.Warnings.warn(SCons.Warnings.StackSizeWarning, msg)

            # Create worker threads
            self.workers = []
            for _ in range(num):
                worker = Worker(self.requestQueue, self.resultsQueue, interrupted)
                self.workers.append(worker)

            if 'prev_size' in locals():
                threading.stack_size(prev_size)

        def put(self, task):
            """Put task into request queue."""
            self.requestQueue.put(task)

        def get(self):
            """Remove and return a result tuple from the results queue."""
            return self.resultsQueue.get()

        def preparation_failed(self, task):
            self.resultsQueue.put((task, False))

        def cleanup(self):
            """
            Shuts down the thread pool, giving each worker thread a
            chance to shut down gracefully.
            """
            # For each worker thread, put a sentinel "None" value
            # on the requestQueue (indicating that there's no work
            # to be done) so that each worker thread will get one and
            # terminate gracefully.
            for _ in self.workers:
                self.requestQueue.put(None)

            # Wait for all of the workers to terminate.
            #
            # If we don't do this, later Python versions (2.4, 2.5) often
            # seem to raise exceptions during shutdown.  This happens
            # in requestQueue.get(), as an assertion failure that
            # requestQueue.not_full is notified while not acquired,
            # seemingly because the main thread has shut down (or is
            # in the process of doing so) while the workers are still
            # trying to pull sentinels off the requestQueue.
            #
            # Normally these terminations should happen fairly quickly,
            # but we'll stick a one-second timeout on here just in case
            # someone gets hung.
            for worker in self.workers:
                worker.join(1.0)
            self.workers = []

    class Parallel(object):
        """This class is used to execute tasks in parallel, and is somewhat
        less efficient than Serial, but is appropriate for parallel builds.

        This class is thread safe.
        """

        def __init__(self, taskmaster, num, stack_size):
            """Create a new parallel job given a taskmaster.

            The taskmaster's next_task() method should return the next
            task that needs to be executed, or None if there are no more
            tasks. The taskmaster's executed() method will be called
            for each task when it is successfully executed, or failed()
            will be called if the task failed to execute (i.e. execute()
            raised an exception).

            Note: calls to taskmaster are serialized, but calls to
            execute() on distinct tasks are not serialized, because
            that is the whole point of parallel jobs: they can execute
            multiple tasks simultaneously. """

            self.taskmaster = taskmaster
            self.interrupted = InterruptState()
            self.tp = ThreadPool(num, stack_size, self.interrupted)

            self.maxjobs = num

        def start(self):
            """Start the job. This will begin pulling tasks from the
            taskmaster and executing them, and return when there are no
            more tasks. If a task fails to execute (i.e. execute() raises
            an exception), then the job will stop."""

            jobs = 0

            while True:
                # Start up as many available tasks as we're
                # allowed to.
                while jobs < self.maxjobs:
                    task = self.taskmaster.next_task()
                    if task is None:
                        break

                    try:
                        # prepare task for execution
                        task.prepare()
                    except:
                        task.exception_set()
                        task.failed()
                        task.postprocess()
                    else:
                        if task.needs_execute():
                            # dispatch task
                            self.tp.put(task)
                            jobs = jobs + 1
                        else:
                            task.executed()
                            task.postprocess()

                if not task and not jobs: break

                jobs = jobs - self._processResults(jobs)

            self.tp.cleanup()
            self.taskmaster.cleanup()

        def _processResults(self, jobs):
            """Process all available results. This function will block while
            waiting for the first result from the thread pool. If any
            additional results are available, it will retrieve them and then
            return.

            The jobs parameter is the number of active jobs.

            Returns the number of results that were retrieved.
            """
            results = 0

            # Let any/all completed tasks finish up before we go
            # back and put the next batch of tasks on the queue.
            while True:
                task, ok = self.tp.get()
                results = results + 1

                if ok:
                    task.executed()
                else:
                    if self.interrupted():
                        try:
                            raise SCons.Errors.BuildError(
                                task.targets[0], errstr=interrupt_msg)
                        except:
                            task.exception_set()

                    # Let the failed() callback function arrange
                    # for the build to stop if that's appropriate.
                    task.failed()

                task.postprocess()

                # Checking jobs == results here avoids unnecessarily calling
                # into empty() in that case. It is an expensive call because
                # it grabs a mutex.
                if jobs == results or self.tp.resultsQueue.empty():
                    return results

    class ParallelV2(Parallel):
        def _gatherTasks(self, tasks, max_batch_size, exitOnJobComplete):
            """
            Compiles a list of tasks that need to be executed.
            Exits if we run out of tasks or a job is complete.

            Params:
                self: Current object.
                tasks (deque): List of tasks.
                max_batch_size (Int): Length limit of tasks list. -1 if no limit.
                exitOnJobComplete (Bool): True to exit if the results queue is
                                          non-empty, False to not check it.
            Returns:
                Bool specifying whether any jobs are done with results in the
                resultsQueue. If exitOnJobComplete was False, this is always
                False.
                Bool specifying whether any tasks are left.
            """
            limitResults = False if max_batch_size == -1 else True
            taskNumber = 1
            while not limitResults or len(tasks) < max_batch_size:
                # Try to get the next available task.
                task = self.taskmaster.next_task()
                if task is None:
                    return False, False

                # Prepare the task for execution and see if it needs to be
                # executed. If not, we can postprocess and forget about it.
                try:
                    task.prepare()
                except:
                    task.exception_set()
                    task.failed()
                    task.postprocess()
                else:
                    if task.needs_execute():
                        tasks.append(task)
                    else:
                        task.executed()
                        task.postprocess()

                if exitOnJobComplete:
                    # Check whether any jobs are complete. This is expensive
                    # because resultsQueue.empty() acquires a mutex, so we do
                    # so only every once in a while.
                    taskNumber = taskNumber + 1
                    if taskNumber % 10 == 0 and not self.tp.resultsQueue.empty():
                        return True, True
            return False, True

        def _fetchFromCache(self, tasks, cacheDir):
            """
            Fetches the specified tasks from the cache.

            Params:
                tasks (deque): Tasks to fetch from the cache.
                cacheDir (CacheDir): Cache owner.
            Returns:
                deque of tasks that still need to be executed.
                True if at least one task was fetched from cache.
            """
            targets_to_retrieve = deque()
            for task in tasks:
                cache_candidates = [t for t in task.targets
                                    if t.should_retrieve_from_cache()]
                if len(cache_candidates) == len(task.targets):
                    targets_to_retrieve.extend(cache_candidates)

            retrieved_nodes = cacheDir.retrieve_nodes(targets_to_retrieve) \
                if targets_to_retrieve else []

            # Figure out which tasks were entirely fetched from cache.
            tasks_to_execute = deque()
            task_fetched = False
            for task in tasks:
                cached_targets = [t for t in task.targets
                                  if t in retrieved_nodes]
                if task.process_cached_targets(cached_targets):
                    task.executed()
                    task.postprocess()
                    task_fetched = True
            return tasks_to_execute, task_fetched

        def start(self):
            """Runs the full list of tasks."""
            cache = SCons.Defaults.DefaultEnvironment().get_CacheDir()
            cache_enabled = cache.is_enabled()
            tasks_to_fetch = deque()
            tasks_to_execute = deque()
            jobs = 0
            tasks_left = True
            batch_size = 250

            while True:
                if tasks_left:
                    if jobs > 0:
                        # Keep gathering tasks while waiting but be interrupted
                        # often to optimize for keeping jobs equal to
                        # self.maxjobs as often as possible.
                        jobs_done, tasks_left = self._gatherTasks(
                            tasks_to_fetch, -1, True)
                    else:
                        # No active jobs. Grab some now to iterate over.
                        display('Gathering some tasks for SCons.')
                        jobs_done, tasks_left = self._gatherTasks(
                            tasks_to_fetch, batch_size, False)
                        display('Found %d tasks to evaluate.' %
                                len(tasks_to_fetch))

                    # This should be larger for subsequent runs of this loop
                    # because we only expect it to be used again if most
                    # deliverables came from cache. Otherwise, the initial batch
                    # should serve as enough tasks to keep the thread pool busy
                    # while we keep looking for more tasks.
                    batch_size = 1000
                else:
                    # No tasks left, so trigger the code below to wait for the
                    # the next job.
                    jobs_done = True

                    # Reset the batch size because the next time tasks_left is
                    # True, we expect it to be a run over the next higher level
                    # the tree that has been unblocked by the previous set of
                    # leaf nodes.
                    batch_size = 250

                # If there are no tasks left and there are no active jobs,
                # we are done.
                if not tasks_to_fetch and not tasks_to_execute and jobs == 0:
                    break

                # If any jobs are done, we should process them now.
                if jobs_done:
                    jobs = jobs - self._processResults(jobs)

                    # Tasks could have been unblocked, so we should check
                    # again.
                    tasks_left = True

                # Check to see if we need to go to the cache for the tasks we
                # have accumulated in tasks_to_fetch.
                if tasks_to_fetch:
                    if not cache_enabled:
                        # No cache to fetch from, so execute all tasks.
                        tasks_to_execute.extend(tasks_to_fetch)
                        tasks_to_fetch.clear()
                    elif jobs + len(tasks_to_execute) < self.maxjobs:
                        # We don't have enough jobs to fill our queue, so it's
                        # a good time to go to the cache.
                        to_execute, any_fetched = self._fetchFromCache(
                            tasks_to_fetch, cache)
                        tasks_to_execute.extend(to_execute)

                        if any_fetched:
                            tasks_left = True

                        tasks_to_fetch.clear()

                # Now dispatch any more jobs if there is room.
                while tasks_to_execute and jobs < self.maxjobs:
                    self.tp.put(tasks_to_execute.popleft())
                    jobs = jobs + 1

            self.tp.cleanup()
            self.taskmaster.cleanup()


# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
