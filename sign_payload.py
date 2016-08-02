#!/usr/bin/env python2
import hmac
import hashlib
import json
from lib.settings_loader import settings
import sys
import os

def sign(payload):
    return hmac.new(settings.GITHUB_TOKEN, payload, hashlib.sha1).hexdigest()

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print("missing file")
        exit()

    if not os.path.isfile(sys.argv[1]):
        print("this file does not exist")
        exit()

    with open(sys.argv[1], 'r') as payload_file:
        payload = payload_file.read().strip()

    print(sign(payload))
