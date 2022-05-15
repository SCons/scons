import http.server
import socketserver
import time
from urllib.parse import urlparse, parse_qs
from threading import Lock
from enum import Enum
import psutil

class TestState(Enum):
    start_state = 0
    mycopy_started = 1
    myfail_done = 2

class Response(Enum):
    OK = 200
    WAIT = 201
    DONE = 202

def server_thread(PORT):

    class S(http.server.BaseHTTPRequestHandler):

        current_state = TestState.start_state
        mutex = Lock()
        pid_killed_tries = 20

        def do_GET(self):
            gets = parse_qs(urlparse(self.path).query)

            # the two tasks will communicate with the server with basic get
            # requests, either updating or getting the state of the test to
            # know if they continue. The server is regluating the state and making
            # the right criteria is in place from both tasks before moving the
            # test state forward.

            if gets.get('set_mycopy_started'):
                S.mutex.acquire()
                if S.current_state == TestState.start_state:
                    S.current_state = TestState.mycopy_started
                    response = Response.OK
                else:
                    response = Response.WAIT
                S.mutex.release()

            elif gets.get('get_mycopy_started'):
                S.mutex.acquire()
                if S.current_state == TestState.mycopy_started:
                    response = Response.OK
                else:
                    response = Response.WAIT
                S.mutex.release()

            elif gets.get('set_myfail_done'):
                S.mutex.acquire()
                if S.current_state == TestState.mycopy_started:
                    count = 0
                    pid = int(gets.get('pid')[0])
                    while psutil.pid_exists(pid) and count < self.pid_killed_tries:
                        time.sleep(0.5)
                        count += 1
                    if not psutil.pid_exists(pid):
                        S.current_state = TestState.myfail_done
                        response = Response.DONE
                    else:
                        response = Response.WAIT
                else:
                    response = Response.WAIT
                S.mutex.release()

            elif gets.get('get_myfail_done'):
                S.mutex.acquire()
                if S.current_state == TestState.myfail_done:
                    response = Response.OK
                else:
                    response = Response.WAIT
                S.mutex.release()

            else:
                response = Response.WAIT
            self.send_response(response.value)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            if response != Response.DONE:
                self.wfile.write("".encode('utf-8'))

        def log_message(self, format, *args):
            return

    httpd = socketserver.TCPServer(("127.0.0.1", PORT), S)
    httpd.serve_forever()