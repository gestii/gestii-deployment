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
    parser = argparse.ArgumentParser(description='Triggers the rollback process')

    parser.add_argument('host', help='The host')
    parser.add_argument('repo', help='The repository to deploy')
    parser.add_argument('--port', help='The port', default='4567')
    parser.add_argument('--branch', help='The branch', default='master')
    parser.add_argument('--tag', help='The tag to rollback')

    args = parser.parse_args()

    payload = json.dumps({
        "repo": args.repo,
        "ref" : args.branch,
    })

    try:
        r = requests.post('http://{host}:{port}/rollback'.format(
            host = args.host,
            port = args.port,
        ), headers={
            'X-Hub-Signature': 'sha1='+sign(payload)
        }, data=payload)

        print(r.text)
    except requests.exceptions.ConnectionError:
        print('Deploy server {} at port {} is not running'.format(args.host, args.port))
