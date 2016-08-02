import json
from datetime import datetime
from lib.settings_loader import settings
import os

"""
Send deploy messages to json files
"""

def deploy_finished(deploy_data):
    file_name = "{server_name}_{date}.json".format(
        server_name = settings.NAME,
        date = datetime.now().strftime('%Y-%m-%dT%H-%M-%S.%f')
    )
    with open(file_name, 'w') as message_file:
        json.dump(deploy_data, message_file)

def repo_added(deploy_data):
    file_name = "{server_name}_{date}.json".format(
        server_name = settings.NAME,
        date = datetime.now().strftime('%Y-%m-%dT%H-%M-%S.%f')
    )
    with open(os.path.join(os.path.dirname(__file__), '../../', file_name), 'w') as message_file:
        json.dump(deploy_data, message_file)

if __name__ == '__main__':
    print()
