import subprocess
import sys
import os
import pathlib
import tempfile
import hashlib
import logging
import time
import http.client
import traceback

ninja_builddir = pathlib.Path(sys.argv[2])
daemon_dir = pathlib.Path(tempfile.gettempdir()) / ('scons_daemon_' + str(hashlib.md5(str(ninja_builddir).encode()).hexdigest()))
os.makedirs(daemon_dir, exist_ok=True)

logging.basicConfig(
    filename=daemon_dir / "scons_daemon.log",
    filemode="a",
    format="%(asctime)s %(message)s",
    level=logging.DEBUG,
)

if not os.path.exists(ninja_builddir / "scons_daemon_dirty"):
    cmd = [sys.executable, str(pathlib.Path(__file__).parent / "ninja_scons_daemon.py")] + sys.argv[1:]
    logging.debug(f"Starting daemon with {' '.join(cmd)}")

    p = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=False)

    with open(daemon_dir / "pidfile", "w") as f:
        f.write(str(p.pid))
    with open(ninja_builddir / "scons_daemon_dirty", "w") as f:
        f.write(str(p.pid))

    error_msg = f"ERROR: Failed to connect to scons daemon.\n Check {daemon_dir / 'scons_daemon.log'} for more info.\n"

    while True:
        try: 
            logging.debug(f"Attempting to connect scons daemon")
            conn = http.client.HTTPConnection("127.0.0.1", port=int(sys.argv[1]), timeout=60)
            conn.request("GET", "/?ready=true")
            response = None

            try:
                response = conn.getresponse()
            except (http.client.RemoteDisconnected, http.client.ResponseNotReady):
                time.sleep(0.01)
            except http.client.HTTPException as e:
                logging.debug(f"Error: {traceback.format_exc()}")
                sys.stderr.write(error_msg)
                exit(1)
            else:
                msg = response.read()
                status = response.status
                if status != 200:
                    print(msg.decode('utf-8'))
                    exit(1)
                logging.debug(f"Request Done: {sys.argv[3]}")
                break
            
        except ConnectionRefusedError:
            logging.debug(f"Server not ready: {sys.argv[3]}")
            time.sleep(1)
        except ConnectionResetError:
            logging.debug(f"Server ConnectionResetError")
            sys.stderr.write(error_msg)
            exit(1)
        except:
            logging.debug(f"Error: {traceback.format_exc()}")
            sys.stderr.write(error_msg)
            exit(1)

