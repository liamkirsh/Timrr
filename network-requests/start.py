#!/usr/local/bin/python
import os
import subprocess
import time
import sys


def linux_start():
    try:
        ret = subprocess.Popen(["mitmdump"])
        time.sleep(3)  # FIXME: reliably check that certs are ready

        # Create cert dir
        retval = os.system("sudo mkdir -p /usr/share/ca-certificates/extra")
        assert not retval
        
        # Copy mitmproxy CA to cert dir
        retval = os.system("sudo cp ~/.mitmproxy/mitmproxy-ca-cert.pem /usr/share/ca-certificates/extra/mitmproxy-ca-cert.pem")
        assert not retval
    finally:
        ret.kill()

if not (sys.platform == "linux" or sys.platform == "linux2"):
    sys.stderr.write("error: only linux is supported at this time")
    sys.exit(1)
    # FIXME: handle mac & windows
linux_start()

