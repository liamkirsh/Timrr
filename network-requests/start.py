#!/usr/local/bin/python
import os
import subprocess
import time
import sys

FILTER = "net.py"


def start():
    try:
        ret = subprocess.Popen(["mitmdump"])
        time.sleep(3)  # FIXME: reliably check that certs are ready

        if platform == "linux":
            # Create cert dir
            retval = os.system("sudo mkdir -p /usr/share/ca-certificates/extra")
            assert not retval

            # Copy mitmproxy CA to cert dir
            retval = os.system(
                "sudo cp ~/.mitmproxy/mitmproxy-ca-cert.pem "
                "/usr/share/ca-certificates/extra/mitmproxy-ca-cert.pem"
            )
            assert not retval

        elif platform == "mac":
            retval = os.system(
                'sudo security add-trusted-cert -d -r trustRoot -k '
                '"/Library/Keychains/System.keychain" ~/.mitmproxy/mitmproxy-ca-cert.pem'
            )
            assert not retval

    finally:
        ret.kill()

    # Set up transparent network proxy
    try:
        _setup_proxy()

        # FIXME: Create a user to run mitmproxy that can be excluded by the iptables rule
        #ret = os.system(
        #    "sudo python /usr/local/bin/mitmdump -T --host -s {} --verify-upstream-cert".format(FILTER)
        #)
        #ret = subprocess.call(["mitmproxy", "-T", "--host", "--verify-upstream-cert"])
        ret = os.system(
            "sudo /usr/local/bin/mitmproxy -T --host --verify-upstream-cert"
        )
        assert not ret
    finally:
        _teardown_proxy()


def _teardown_proxy():
    # If something fails, ensure that the firewall rules are removed
    if platform == "linux":
        retval = os.system(
            "sudo sysctl -w net.ipv4.ip_forward=0"
        )

    elif platform == "mac":
        retval = os.system(
            "sudo sysctl -w net.inet.ip.forwarding=0"
        )
        assert not retval

    if platform == "linux":
        retval = os.system(
            "sudo iptables -t nat -D OUTPUT -p tcp -m owner ! --uid-owner root -m multiport --dports 80,443 -j REDIRECT --to-port 8080"
        )  # FIXME: use the python-iptables bindings?

    elif platform == "mac":
        retval = os.system(
            "sudo pfctl -f /etc/pf.conf"
        )
        assert not retval

'''retval = os.system(
    "sudo route del default gw localhost"
)'''


def _setup_proxy():
    """I'd just like to interject for a moment. What you're referring to as
Linux, is in fact, GNU/Linux, or as I've recently taken to calling it, GNU
plus Linux. Linux is not an operating system unto itself, but rather another
free component of a fully functioning GNU system made useful by the GNU
corelibs, shell utilities and vital system components comprising a full OS as
defined by POSIX. Many computer users run a modified version of the GNU system
every day, without realizing it. Through a peculiar turn of events, the version
of GNU which is widely used today is often called 'Linux', and many of its
users are not aware that it is basically the GNU system, developed by the GNU
Project. There really is a Linux, and these people are using it, but it is
just a part of the system they use. Linux is the kernel: the program in the
system that allocates the machine's resources to the other programs that you
run. The kernel is an essential part of an operating system, but useless by
itself; it can only function in the context of a complete operating system.
Linux is normally used in combination with the GNU operating system: the whole
system is basically GNU with Linux added, or GNU/Linux. All the so-called
'Linux' distributions are really distributions of GNU/Linux."""
    if platform == "linux":
        retval = os.system(
            "sudo sysctl -w net.ipv4.ip_forward=1"
        )
        assert not retval

        retval = os.system(
            "echo 0 | sudo tee /proc/sys/net/ipv4/conf/*/send_redirects"
        )
        assert not retval

    elif platform == "mac":
        retval = os.system(
            "sudo sysctl -w net.inet.ip.forwarding=1"
        )
        assert not retval

    if platform == "linux":
        retval = os.system(
            "sudo iptables -t nat -A OUTPUT -p tcp -m owner ! --uid-owner root -m multiport --dports 80,443 -j REDIRECT --to-port 8080"
        )  # FIXME: use the python-iptables bindings?

    elif platform == "mac":
        pfconf = open("pf.conf", "w")
        pfconf.write(
            "rdr on en2 inet proto tcp to any port 80 -> 127.0.0.1 port 8080\n"
            "rdr on en2 inet proto tcp to any port 443 -> 127.0.0.1 port 8080"
        )

        # configure pf
        retval = os.system("sudo pfctl -f pf.conf")
        assert not retval

        # enable pf
        retval = os.system("sudo pfctl -e")
        assert retval == 0 or retval == 1

        # configure sudoers to allow mitmproxy to access pfctl
        retval = os.system(
            'echo "ALL ALL=NOPASSWD: /sbin/pfctl -s state" | sudo tee -a /etc/sudoers'
        )
        assert not retval

if sys.platform == "linux" or sys.platform == "linux2":
    platform = "linux"
elif sys.platform == "darwin":  # MAC OS X
    platform = "mac"
else:
    sys.stderr.write("error: only linux and mac are supported at this time")
    sys.exit(1)
    # FIXME: handle windows
start()
