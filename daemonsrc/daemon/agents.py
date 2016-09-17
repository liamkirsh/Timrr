import subprocess
#from multiprocessing import Process

def run_agent(path):
    """
    Alternative way
    p = Process(target=f, args=('bob',))
    p.start()
    p.join()
    """
    print "Starting executable '{}'".format(path)
    subprocess.Popen(path)

def run_all():
    mydaemons = [
        ["/usr/bin/env", "selfspy", "-n"],
        ["../../spying/spypusher"],
        ["../../spying/netspy"]
    ]

    for daemon in mydaemons:
        run_agent(daemon)
