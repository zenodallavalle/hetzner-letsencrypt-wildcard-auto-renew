import sys
import pexpect
import hetzner
import time
import subprocess


def get_acme_challenge(domain):
    return subprocess.check_output(["dig", "-t", "txt", f"_acme-challenge.{domain}", "+short"]).decode("utf-8").replace('"', "")


def renew(zone, record, domain):
    record = hetzner.get_acme_record(zone)
    old = record["value"]
    old = 'old'
    child = pexpect.spawn(
        f"/bin/bash -c 'certbot certonly -d *.{domain} --server https://acme-v02.api.letsencrypt.org/directory --manual --preferred-challenges dns --manual-public-ip-logging-ok'", encoding="utf-8")
    child.logfile_read = sys.stdout

    ex = child.expect(
        ["Before continuing", "Certificate not yet due for renewal"])
    if ex == 1:
        print("Certificate not yet due for renewal. Exiting.")
        sys.exit(0)
    elif ex == 0:
        i = 0
        child.expect('\d*with the following value:\d*')
        while i < 10:
            new = child.readline().strip()
            if new:
                break
        else:
            print('Error while trying to read value, abort...')
            sys.exit(0)

        if old != new:
            print(f"\n\n\nReplacing {old} with {new}")

            if hetzner.save_acme_record(zone, record, new):
                print("DNS Change Invoked")
                print("Waiting for DNS Change to come through")
                while old == get_acme_challenge(domain):
                    print(".", end="")
                    time.sleep(1)

        child.sendline()
        child.expect("Congratulations!")
