import subprocess
#from multiprocessing import Process

def run_agent(path):
    """
    Alternative way
    p = Process(target=f, args=('bob',))
    p.start()
    p.join()
    """

    subprocess.Popen(["python", path])

def run_all():
    mydaemons = [
        "selfspy -n"
    ]

    for daemon in mydaemons:
        run_agent(daemon)
