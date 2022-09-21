import os
import sys
import requests

BASE_URL = "https://dns.hetzner.com/api/v1"
TOKEN = os.environ.get("HETZNER_TOKEN", None)
RECORD_NAME = "_acme-challenge"

if TOKEN is None:
    raise AssertionError('HETZNER_TOKEN environment variable is missing')


def get_zone(domain):
    try:
        response = requests.get(
            url=f"{BASE_URL}/zones",
            headers={
                "Auth-API-Token": TOKEN,
            },
        )
        if response.status_code != 200:
            sys.exit("Error on fetching zone, please check your token")
        json = response.json()
        if "zones" in json:
            zones = json["zones"]
            return next(item for item in zones if item["name"] == domain)
        else:
            sys.exit("No zones!")
    except requests.exceptions.RequestException:
        sys.exit("Get Zones HTTP Request failed")


def get_acme_record(zone):
    try:
        response = requests.get(
            url=f"{BASE_URL}/records",
            params={
                "zone_id": zone["id"],
            },
            headers={
                "Auth-API-Token": TOKEN,
            },
        )
        if response.status_code != 200:
            sys.exit("Error on fetching acme record, please check your token")
        json = response.json()
        if "records" in json:
            records = json["records"]
            for item in records:
                if item['name'] == RECORD_NAME:
                    return item
            return {'value': ''}
        else:
            sys.exit("No records!")
    except requests.exceptions.RequestException:
        sys.exit("Get Records HTTP Request failed")


def save_acme_record(zone, record, value):
    payload = {
        "value": value,
        "ttl": 86400,
        "type": "TXT",
        "name": RECORD_NAME,
        "zone_id": zone["id"],
    }
    try:
        if not record.get('id', None):
            response = requests.post(
                url=f"{BASE_URL}/records",
                headers={
                    "Content-Type": "application/json",
                    "Auth-API-Token": TOKEN,
                },
                json=payload,
            )
        else:
            response = requests.put(
                url=f"{BASE_URL}/records/{record['id']}",
                headers={
                    "Content-Type": "application/json",
                    "Auth-API-Token": TOKEN,
                },
                json=payload,
            )
        if response.status_code != 200:
            sys.exit("Error on saving acme record")
        return response.json()
    except requests.exceptions.RequestException:
        sys.exit("HTTP Request failed")


def delete_acme_record(record):
    try:
        response = requests.delete(
            url=f"{BASE_URL}/records/{record['id']}",
            headers={
                "Auth-API-Token": TOKEN,
            },
        )
        if response.status_code != 200:
            sys.exit("Error on cleaning acme record, please check your token")
    except requests.exceptions.RequestException:
        sys.exit("Get Records HTTP Request failed")
