import json
from datetime import datetime
from lib.settings_loader import settings
import os

"""
Send deploy messages to json files
"""

def get_file_name(action):
    return os.path.join(
        os.path.dirname(__file__),
        '../../logs',
        "{action}_{server_name}_{date}.json".format(
            action = action,
            server_name = settings.NAME,
            date = datetime.now().strftime('%Y-%m-%dT%H-%M-%S.%f')
        )
    )

def deploy_finished(deploy_data):
    with open(get_file_name('deploy'), 'w') as message_file:
        json.dump(deploy_data, message_file)

def rollback_finished(deploy_data):
    with open(get_file_name('rollback'), 'w') as message_file:
        json.dump(deploy_data, message_file)

def repo_added(deploy_data):
    with open(get_file_name('add'), 'w') as message_file:
        json.dump(deploy_data, message_file)
