import sys
import pexpect
from dns import resolver
from time import sleep

import hetzner


def get_acme_challenge(domain):
    my_resolver = resolver.Resolver()
    my_resolver.nameservers = [
        '213.133.100.98',
        '88.198.229.192',
        '193.47.99.5',
    ]
    records = my_resolver.resolve(f'_acme-challenge.{domain}', 'TXT')
    try:
        return records[0].to_text().replace('"', '')
    except Exception:
        return ''


def renew(zone, record, domain, test_mode=False):
    test_arg = '--dry-run' if test_mode else ''

    record = hetzner.get_acme_record(zone)

    child = pexpect.spawn(
        f"/bin/bash -c 'certbot certonly {test_arg} -d *.{domain} --server https://acme-v02.api.letsencrypt.org/directory --manual --preferred-challenges dns --manual-public-ip-logging-ok'", encoding="utf-8")
    child.logfile_read = sys.stdout

    ex = child.expect([
        "Before continuing",
        'Simulating a certificate request for\d*' if test_mode else "Certificate not yet due for renewal"
    ])

    if ex == 1:
        print("Certificate not yet due for renewal. Exiting.")
        sys.exit(0)
    else:
        i = 0
        child.expect('\d*with the following value:\d*')
        while i < 10:
            new = child.readline().strip()
            if new:
                break
        else:
            print('Error while trying to read value, abort...')
            sys.exit(0)

        print(f'Updating/creating record with value: {new}')

        record = hetzner.save_acme_record(zone, record, new)['record']

        print('Hetzner DNS record updated!')

        i = 0
        while i < 100:
            got_value = get_acme_challenge(domain)
            print('.', end='')
            if got_value == new:
                print('')
                break
            sleep(1)
            i += 1

        child.sendline()

        ex = child.expect(
            'The dry run was successful.' if test_mode else 'Congratulations!')

        print('Finished, cleaning up...')

        hetzner.delete_acme_record(zone, record)
