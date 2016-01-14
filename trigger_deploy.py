#!/usr/bin/env python2
import sys
import json
import argparse
import requests
from functools import partial
from sign_payload import sign
from lib.settings_loader import settings

def err(msg):
    sys.stderr.write(msg + '\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Triggers the deploy process')

    parser.add_argument('host', help='The host')
    parser.add_argument('repo', help='The repository to deploy')

    args = parser.parse_args()

    payload = json.dumps({
        "ref": "refs/heads/develop",
        "after": "DUMMY",
        "commits": [],
        "repository": {
            "name": args.repo
        }
    })

    print(payload)
    print(settings.GITHUB_TOKEN)

    r = requests.post('http://'+args.host+':4567', headers={
        'X-Hub-Signature': 'sha1='+sign(payload)
    }, data=payload)

    if r.status_code == 400:
        err(r.json()['msg'])
        exit(1)

    print(r.status_code)
    print(r.text)
