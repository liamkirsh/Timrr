import time

from .config import PRODUCTIVE_DOMAINS, NONPRODUCTIVE_DOMAINS

OUTPUT_FILE = "output.txt"
f = None


def start(context, argv):
    global f
    f = open(OUTPUT_FILE, 'a')
    f.write("\n\n" + time.strftime("%d/%m/%Y %H:%M:%S") + "\n\n")


def request(context, flow):
    global f
    f.write("\nRequest " + flow.request.method + "\n")


def done(context):
    global f
    f.close()

# GMail sent mail

# SMTP sent mail


