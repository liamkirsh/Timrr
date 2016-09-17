#!/usr/bin/env python3

import subprocess
import requests
import time

command="/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -I | grep '^\s*SSID:' | awk '{print $2}'"
server="http://localhost:5000"
lastNet=None

print("Started. Last net is: {}".format(lastNet))
while True:
    currentNet = subprocess.getoutput(command)
    if currentNet != lastNet:
        print("New net '{}' found".format(currentNet));
        network = {
            'fingerprint': currentNet,
            'kind': 'work' if currentNet == 'HackZurich' else 'personal',
            'action': 'connect',
        }
        requests.post("{}/ingest".format(server), json={'network':network})
        lastNet = currentNet
    time.sleep(5)
