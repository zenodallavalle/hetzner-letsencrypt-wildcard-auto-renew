import sys
from dotenv import load_dotenv

# load_dotenv must be called before importing hetzner module as importing hetzner module will check the presence of HETZNER_TOKEN in os.environ
load_dotenv()


import hetzner
import certbot


def main():
    print("Let's Encrypt Wildcard Auto-Renewal with Hetzner\n")

    if len(sys.argv) != 2:
        print("Domain name is missing\n")
        print("Usage: python renew.py example.com")
        exit()

    domain = sys.argv[1]
    zone = hetzner.get_zone(domain)
    record = hetzner.get_acme_record(zone)
    certbot.renew(zone, record, domain)


if __name__ == "__main__":
    main()
