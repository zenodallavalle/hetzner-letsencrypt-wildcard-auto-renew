import sys
import pexpect
from dns import resolver
from time import sleep

import hetzner


def get_acme_challenge(domain):
    try:
        records = resolver.resolve(f'_acme-challenge.{domain}', 'TXT')
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
        'Simulating a certificate request for\d*',
        "Certificate not yet due for renewal"
    ])

    if ex == 2:
        print("\nCertificate not yet due for renewal. Exiting.")
        sys.stdout.flush()
        sys.exit(0)
    else:
        i = 0
        child.expect('with the following value:')
        while i < 10:
            new = child.readline().strip()
            print('NEW IS new:', new)
            if new:
                break
        else:
            print('\nError while trying to read value, abort...')
            sys.stdout.flush()
            sys.exit(0)

        print(f'\nUpdating/creating record with value: {new}')
        sys.stdout.flush()

        record = hetzner.save_acme_record(zone, record, new)['record']

        print('\nHetzner DNS record updated!\n')
        sys.stdout.flush()

        i = 0
        while i < 100:
            got_value = get_acme_challenge(domain)
            print('.', end='')
            if got_value == new:
                print('')
                sys.stdout.flush()
                break
            sleep(1)
            i += 1

        child.sendline()

        ex = child.expect(
            'The dry run was successful.' if test_mode else 'Congratulations!')

        print('\nFinished, cleaning up...')
        sys.stdout.flush()

        hetzner.delete_acme_record(zone, record)
