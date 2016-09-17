import threading

work_status = 1

def datafetcher():
    t = threading.Timer(interval=1.0, function=fetch_work_status)
    t.daemon = True
    t.start()

def fetch_work_status():
    global work_status
    import random
    work_status = random.choice([1, 2, 3])
    
    t = threading.Timer(interval=1.0, function=fetch_work_status)
    t.daemon = True
    t.start()

def get_work_status():
    return work_status

datafetcher()