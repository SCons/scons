import os
import sys
import time
import http.client

sys.path.append(os.getcwd())
from teststate import Response

conn = http.client.HTTPConnection("127.0.0.1",  port=int(sys.argv[3]))
conn.request("GET", "/?set_mycopy_started=1")
conn.getresponse().read()

with open(sys.argv[1], 'wb') as ofp, open(sys.argv[2], 'rb') as ifp:
    ofp.write(ifp.read())
    
WAIT = 10
count = 0

def check_test_state():

    conn.request("GET", "/?get_myfail_done=1")
    response = conn.getresponse()
    response.read()
    status = response.status
    return status == Response.OK.value

while not check_test_state() and count < WAIT:
    time.sleep(0.1)
    count += 0.1

if count >= WAIT:
    sys.exit(99)

conn.close()
sys.exit(0)