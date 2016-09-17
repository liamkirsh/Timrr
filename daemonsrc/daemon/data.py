import threading
import requests

work_status = 'undecided'
server = "http://localhost:5000"

def datafetcher():
    t = threading.Timer(interval=1.0, function=fetch_work_status)
    t.daemon = True
    t.start()

def fetch_work_status():
    global work_status
    work_status = requests.get("{}/workstatus".format(server)).content
    t = threading.Timer(interval=1.0, function=fetch_work_status)
    t.daemon = True
    t.start()

def get_work_status():
    return work_status

datafetcher()
