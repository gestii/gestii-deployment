import hmac
import hashlib
import json
from lib.settings_loader import settings

with open('payload.json', 'r') as payload_file:
    payload = payload_file.read()

print hmac.new(settings.GITHUB_TOKEN, payload, hashlib.sha1).hexdigest()
