import cherrypy
import os
import subprocess
from lib.settings_loader import settings
import platform
from datetime import datetime

notify_adapter = __import__('lib.notify.'+settings.NOTIFY_ADAPTER).notify.__getattribute__(settings.NOTIFY_ADAPTER)
is_windows     = platform.system() == 'Windows'

def deploy_repo(repo_dir, deploy_data, script):
    cherrypy.log('deploying repo ' + repo_dir, context='GIT')

    os.chdir(repo_dir)

    for command in script:
        process = subprocess.call(command.split(' '), shell=is_windows)

    deploy_data.update({
        'finished': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    })

    notify_adapter.deploy_finished(deploy_data)

    cherrypy.log('finished deploy ' + repo_dir, context='GIT')

def rollback_repo(repo_dir, rollback_data, script):
    os.chdir(repo_dir)

    if 'tag' in rollback_data:
        tag = rollback_data['tag']
    else:
        tag = subprocess.check_output(["git", "tag"]).strip().split('\n')[-2]

    cherrypy.log('rolling back repo {} to tag {}'.format(repo_dir, tag), context='GIT')

    script.insert(0, 'git reset --hard {}'.format(tag))

    for command in script:
        if command.startswith('git pull'):
            continue # ignore git pull, this rolls back the rollback
        process = subprocess.call(command.split(' '), shell=is_windows)

    rollback_data.update({
        'tag'     : tag,
        'finished': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    })

    notify_adapter.rollback_finished(rollback_data)

    cherrypy.log('finished rollback ' + repo_dir, context='GIT')
