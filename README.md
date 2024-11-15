# Let's Encrypt Wildcard Auto-Renewal with Hetzner Zone-File DNS Challenge

The provided scripts will auto-renew your Let's Encrypt Wildcard Certificates. For the renewal a DNS Challenge is needed and the certbot-auto asks for a TXT Record named _\_acme-challenge_ to be set to a random generated string.

The scripts will update the Zone File within the Hetzner DNS to that new string and await the DNS change to take effect before proceeding with the re-issuing of the certificates.

## Prerequisites

- Python 3.7+
- certbot-auto / certbot

## Installation

In order for the scripts to work some 3rd party modules are required. They can be installed as follows:

```
$ pip[or pip3] install -r requirements.txt
```

## Configuration

The script is using Hetzner DNS API, so only thing you should provide is token (assign it to `HETZNER_TOKEN` environment variable). You can generate new token at https://dns.hetzner.com/settings/api-token
To function correctly set `HETZNER_TOKEN` environment variable. Alternatively you can create a `.env` file in main directory that contains HETZNER_TOKEN=xxxx. Python-dotenv module will make sure entries in `.env` file are loaded when the script is executed, before importing hetzner.py, that would cause an AssertionError to be raised.

## Usage

The Usage is quite simple. Just call the renew.py script with the TLD for which the Zone-File needs to be updated, i.e. the TLD the certificate is due for renewal. In my setup for example I have the following cronjob active

```
@monthly HETZNER_TOKEN=x python renew.py example.com && apache2ctl graceful
```

You can run the script monthly. If the certbot-auto returns a `Certificate is not yet due for renewal` the script will stop immediately, otherwise the renewal process is started.

# Disclaimer

Even though the scripts are used in production on my system and are tested on a Ubuntu 18.04.02 system I do neither claim correctness nor completeness on these scripts. Use at your own risk!
