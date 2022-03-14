# MIT License
#
# Copyright The SCons Foundation
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

"""

"""

import http.server
import socketserver
from urllib.parse import urlparse, parse_qs
import time
from threading import Condition
from subprocess import PIPE, Popen
import sys
import os
import threading
import queue
import pathlib
import logging
from timeit import default_timer as timer
import traceback
import tempfile
import hashlib

port = int(sys.argv[1])
ninja_builddir = pathlib.Path(sys.argv[2])
daemon_keep_alive = int(sys.argv[3])
args = sys.argv[4:]

daemon_dir = pathlib.Path(tempfile.gettempdir()) / (
    "scons_daemon_" + str(hashlib.md5(str(ninja_builddir).encode()).hexdigest())
)
os.makedirs(daemon_dir, exist_ok=True)
logging.basicConfig(
    filename=daemon_dir / "scons_daemon.log",
    filemode="a",
    format="%(asctime)s %(message)s",
    level=logging.DEBUG,
)


def daemon_log(message):
    logging.debug(message)


def custom_readlines(handle, line_separator="\n", chunk_size=1):
    buf = ""
    while not handle.closed:
        data = handle.read(chunk_size)
        if not data:
            break
        buf += data.decode("utf-8")
        if line_separator in buf:
            chunks = buf.split(line_separator)
            buf = chunks.pop()
            for chunk in chunks:
                yield chunk + line_separator
        if buf.endswith("scons>>>"):
            yield buf
            buf = ""


def custom_readerr(handle, line_separator="\n", chunk_size=1):
    buf = ""
    while not handle.closed:
        data = handle.read(chunk_size)
        if not data:
            break
        buf += data.decode("utf-8")
        if line_separator in buf:
            chunks = buf.split(line_separator)
            buf = chunks.pop()
            for chunk in chunks:
                yield chunk + line_separator


def enqueue_output(out, queue):
    for line in iter(custom_readlines(out)):
        queue.put(line)
    out.close()


def enqueue_error(err, queue):
    for line in iter(custom_readerr(err)):
        queue.put(line)
    err.close()


input_q = queue.Queue()
output_q = queue.Queue()
error_q = queue.Queue()

finished_building = []
error_nodes = []

building_cv = Condition()
error_cv = Condition()

thread_error = False


def daemon_thread_func():
    global thread_error
    global finished_building
    global error_nodes
    try:
        args_list = args + ["--interactive"]
        daemon_log(f"Starting daemon with args: {' '.join(args_list)}")
        daemon_log(f"cwd: {os.getcwd()}")

        p = Popen(args_list, stdout=PIPE, stderr=PIPE, stdin=PIPE)

        t = threading.Thread(target=enqueue_output, args=(p.stdout, output_q))
        t.daemon = True
        t.start()

        te = threading.Thread(target=enqueue_error, args=(p.stderr, error_q))
        te.daemon = True
        te.start()

        daemon_ready = False
        building_node = None

        while p.poll() is None:

            while True:
                try:
                    line = output_q.get(block=False, timeout=0.01)
                except queue.Empty:
                    break
                else:
                    daemon_log("output: " + line.strip())

                    if "scons: building terminated because of errors." in line:
                        error_output = ""
                        while True:
                            try:
                                error_output += error_q.get(block=False, timeout=0.01)
                            except queue.Empty:
                                break
                        error_nodes += [{"node": building_node, "error": error_output}]
                        daemon_ready = True
                        building_node = None
                        with building_cv:
                            building_cv.notify()

                    elif line == "scons>>>":
                        with error_q.mutex:
                            error_q.queue.clear()
                        daemon_ready = True
                        with building_cv:
                            building_cv.notify()
                        building_node = None

            while daemon_ready and not input_q.empty():

                try:
                    building_node = input_q.get(block=False, timeout=0.01)
                except queue.Empty:
                    break
                if "exit" in building_node:
                    p.stdin.write("exit\n".encode("utf-8"))
                    p.stdin.flush()
                    with building_cv:
                        finished_building += [building_node]
                    daemon_ready = False
                    raise

                else:
                    input_command = "build " + building_node + "\n"
                    daemon_log("input: " + input_command.strip())

                    p.stdin.write(input_command.encode("utf-8"))
                    p.stdin.flush()
                    with building_cv:
                        finished_building += [building_node]
                    daemon_ready = False

            time.sleep(0.01)
    except Exception:
        thread_error = True
        daemon_log("SERVER ERROR: " + traceback.format_exc())
        raise


daemon_thread = threading.Thread(target=daemon_thread_func)
daemon_thread.daemon = True
daemon_thread.start()

logging.debug(
    f"Starting request server on port {port}, keep alive: {daemon_keep_alive}"
)

keep_alive_timer = timer()
httpd = None


def server_thread_func():
    class S(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            global thread_error
            global keep_alive_timer
            global error_nodes

            try:
                gets = parse_qs(urlparse(self.path).query)
                build = gets.get("build")
                if build:
                    keep_alive_timer = timer()

                    daemon_log(f"Got request: {build[0]}")
                    input_q.put(build[0])

                    def pred():
                        return build[0] in finished_building

                    with building_cv:
                        building_cv.wait_for(pred)

                    for error_node in error_nodes:
                        if error_node["node"] == build[0]:
                            self.send_response(500)
                            self.send_header("Content-type", "text/html")
                            self.end_headers()
                            self.wfile.write(error_node["error"].encode())
                            return

                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    return

                exitbuild = gets.get("exit")
                if exitbuild:
                    input_q.put("exit")

                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()

            except Exception:
                thread_error = True
                daemon_log("SERVER ERROR: " + traceback.format_exc())
                raise

            def log_message(self, format, *args):
                return

    httpd = socketserver.TCPServer(("127.0.0.1", port), S)
    httpd.serve_forever()


server_thread = threading.Thread(target=server_thread_func)
server_thread.daemon = True
server_thread.start()

while timer() - keep_alive_timer < daemon_keep_alive and not thread_error:
    time.sleep(1)

if thread_error:
    daemon_log(f"Shutting server on port {port} down because thread error.")
else:
    daemon_log(
        f"Shutting server on port {port} down because timed out: {daemon_keep_alive}"
    )

# if there are errors, don't immediately shut down the daemon
# the process which started the server is attempt to connect to
# the daemon before allowing jobs to start being sent. If the daemon
# shuts down too fast, the launch script will think it has not
# started yet and sit and wait. If the launch script is able to connect
# and then the connection is dropped, it will immediately exit with fail.
time.sleep(5)

if os.path.exists(ninja_builddir / "scons_daemon_dirty"):
    os.unlink(ninja_builddir / "scons_daemon_dirty")
if os.path.exists(daemon_dir / "pidfile"):
    os.unlink(daemon_dir / "pidfile")

httpd.shutdown()
server_thread.join()


# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
