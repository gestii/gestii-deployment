import requests
import json
from datetime import datetime
from lib.settings_loader import settings

def time_delta(td):
    seconds = td.total_seconds()

    if  seconds > 60:
        return "%d m %d s"%(seconds/60, seconds%60)
    else:
        return "%d s"%seconds

def parse_commits(commit):
    return {
        "title": commit['message'],
        "value": "%s (<%s|ver commit>)"%(commit['author']['name'], commit['url']),
        "short": False,
    }

def deploy_finished(deploy_data):
    text = '[%s] Se ha publicado %s, rama %s (%s)'%(
        settings.NAME,
        deploy_data['repo'],
        deploy_data['target'],
        time_delta(
            datetime.strptime(deploy_data['finished'], '%Y-%m-%d %H:%M:%S') - \
            datetime.strptime(deploy_data['started'], '%Y-%m-%d %H:%M:%S')
        )
    )
    payload = {
        'attachments' : [
            {
                "fallback" : text,
                "pretext"  : text,
                "color"    : "good",
                "fields"   : map(parse_commits, deploy_data['commits'])
            }
        ],
    }
    r = requests.post(settings.SLACK_HOOK, data=json.dumps(payload))

def repo_added():
    pass
