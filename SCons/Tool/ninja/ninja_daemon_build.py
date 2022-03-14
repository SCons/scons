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

import http.client
import sys
import time
import os
import logging
import pathlib
import tempfile
import hashlib
import traceback

ninja_builddir = pathlib.Path(sys.argv[2])
daemon_dir = pathlib.Path(tempfile.gettempdir()) / (
    "scons_daemon_" + str(hashlib.md5(str(ninja_builddir).encode()).hexdigest())
)
os.makedirs(daemon_dir, exist_ok=True)

logging.basicConfig(
    filename=daemon_dir / "scons_daemon_request.log",
    filemode="a",
    format="%(asctime)s %(message)s",
    level=logging.DEBUG,
)

while True:
    try:
        logging.debug(f"Sending request: {sys.argv[3]}")
        conn = http.client.HTTPConnection(
            "127.0.0.1", port=int(sys.argv[1]), timeout=60
        )
        conn.request("GET", "/?build=" + sys.argv[3])
        response = None

        while not response:
            try:
                response = conn.getresponse()
            except (http.client.RemoteDisconnected, http.client.ResponseNotReady):
                time.sleep(0.01)
            except http.client.HTTPException:
                logging.debug(f"Error: {traceback.format_exc()}")
                exit(1)
            else:
                msg = response.read()
                status = response.status
                if status != 200:
                    print(msg.decode("utf-8"))
                    exit(1)
                logging.debug(f"Request Done: {sys.argv[3]}")
                exit(0)

    except ConnectionRefusedError:
        logging.debug(f"Server not ready: {traceback.format_exc()}")
        time.sleep(1)
    except ConnectionResetError:
        logging.debug("Server ConnectionResetError")
        exit(1)


# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4: