import os
import sys
import time
import http.client

sys.path.append(os.getcwd())
from teststate import Response

WAIT = 10
count = 0

conn = http.client.HTTPConnection("127.0.0.1", port=int(sys.argv[3]))

def check_test_state():
    conn.request("GET", "/?get_mycopy_started=1")
    response = conn.getresponse()
    response.read()
    status = response.status
    return status == Response.OK.value
    
while not check_test_state() and count < WAIT:
    time.sleep(0.1)
    count += 0.1

if count >= WAIT:
    sys.exit(99)

conn.request("GET", "/?set_myfail_done=1&pid=" + str(os.getpid()))
conn.close()

sys.exit(1)