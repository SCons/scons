"""SCons.Job

This module defines the Serial and Parallel classes that execute tasks to
complete a build. The Jobs class provides a higher level interface to start,
stop, and wait on jobs.

"""

#
# Copyright (c) 2001, 2002 Steven Knight
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

class Jobs:
    """An instance of this class initializes N jobs, and provides
    methods for starting, stopping, and waiting on all N jobs.
    """
    
    def __init__(self, num, taskmaster):
        """
        create 'num' jobs using the given taskmaster.

        If 'num' is equal to 0, then a serial job will be used,
        otherwise 'num' parallel jobs will be used.
        """

        if num > 1:
            self.jobs = []
            for i in range(num):
                self.jobs.append(Parallel(taskmaster, self))
        else:
            self.jobs = [Serial(taskmaster)]

    def start(self):
        """start the jobs"""

        for job in self.jobs:
            job.start()

    def wait(self):
        """ wait for the jobs started with start() to finish"""

        for job in self.jobs:
            job.wait()

    def stop(self):
        """
        stop the jobs started with start()

        This function does not wait for the jobs to finish.
        """

        for job in self.jobs:
            job.stop()
    
class Serial:
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
        is successfully executed or failed() will be called if it failed to
        execute (e.g. execute() raised an exception). The taskmaster's
        is_blocked() method will not be called.  """
        
        self.taskmaster = taskmaster

    def start(self):
        
        """Start the job. This will begin pulling tasks from the taskmaster
        and executing them, and return when there are no more tasks. If a task
        fails to execute (i.e. execute() raises an exception), then the job will
        stop."""
        
        while 1:
            task = self.taskmaster.next_task()

            if task is None:
                break

            try:
                task.execute()
            except:
                # Let the failed() callback function arrange for the
                # build to stop if that's appropriate.
                task.failed()
            else:
                task.executed()

    def stop(self):
        """Serial jobs are always finished when start() returns, so there
        is nothing to do here"""
        
        pass

    def wait(self):
        """Serial jobs are always finished when start() returns, so there
        is nothing to do here"""
        pass


# The will hold a condition variable once the first parallel task
# is created.
cv = None

class Parallel:
    """This class is used to execute tasks in parallel, and is less
    efficient than Serial, but is appropriate for parallel builds. Create
    an instance of this class for each job or thread you want.

    This class is thread safe.
    """


    def __init__(self, taskmaster, jobs):
        """Create a new parallel job given a taskmaster, and a Jobs instance.
        Multiple jobs will be using the taskmaster in parallel, but all
        method calls to taskmaster methods are serialized by the jobs
        themselves.

        The taskmaster's next_task() method should return the next task
        that needs to be executed, or None if there are no more tasks. The
        taskmaster's executed() method will be called for each task when it
        is successfully executed or failed() will be called if the task
        failed to execute (i.e. execute() raised an exception).  The
        taskmaster's is_blocked() method should return true iff there are
        more tasks, but they can't be executed until one or more other
        tasks have been executed. next_task() will be called iff
        is_blocked() returned false.

        Note: calls to taskmaster are serialized, but calls to execute() on
        distinct tasks are not serialized, because that is the whole point
        of parallel jobs: they can execute multiple tasks
        simultaneously. """

        global cv
        
        # import threading here so that everything in the Job module
        # but the Parallel class will work if the interpreter doesn't
        # support threads
        import threading
        
        self.taskmaster = taskmaster
        self.jobs = jobs
        self.thread = threading.Thread(None, self.__run)
        self.stop_running = 0

        if cv is None:
            cv = threading.Condition()

    def start(self):
        """Start the job. This will spawn a thread that will begin pulling
        tasks from the task master and executing them. This method returns
        immediately and doesn't wait for the jobs to be executed.

        If a task fails to execute (i.e. execute() raises an exception),
        all jobs will be stopped.

        To stop the job, call stop().
        To wait for the job to finish, call wait().
        """
        self.thread.start()

    def stop(self):
        """Stop the job. This will cause the job to finish after the
        currently executing task is done. A job that has been stopped can
        not be restarted.

        To wait for the job to finish, call wait().
        """

        cv.acquire()
        self.stop_running = 1
        # wake up the sleeping jobs so this job will end as soon as possible:
        cv.notifyAll() 
        cv.release()
        
    def wait(self):
        """Wait for the job to finish. A job is finished when either there
        are no more tasks or the job has been stopped and it is no longer
        executing a task.

        This method should only be called after start() has been called.

        To stop the job, call stop().
        """
        self.thread.join()

    def __run(self):
        """private method that actually executes the tasks"""

        cv.acquire()

        try:

            while 1:
                while self.taskmaster.is_blocked() and not self.stop_running:
                    cv.wait(None)

                # check this before calling next_task(), because
                # this job may have been stopped because of a build
                # failure:
                if self.stop_running:
                    break
                    
                task = self.taskmaster.next_task()

                if task == None:
                    break

                cv.release()
                try:
                    try:
                        task.execute()
                    finally:
                        cv.acquire()
                except:
                    # Let the failed() callback function arrange for
                    # calling self.jobs.stop() to to stop the build
                    # if that's appropriate.
                    task.failed()
                else:
                    task.executed()

                # signal the cv whether the task failed or not,
                # or otherwise the other Jobs might
                # remain blocked:
                if not self.taskmaster.is_blocked():
                    cv.notifyAll()
                    
        finally:
            cv.release()




