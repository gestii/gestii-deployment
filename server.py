# -*- coding: utf-8 -*-
import cherrypy
import hashlib
import hmac
import json
import os
import re
import subprocess
import platform
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from lib.settings_loader import settings
from cherrypy.process.plugins import PIDFile
from cherrypy.process.plugins import Daemonizer

system            = platform.system()
deployment_dir    = os.getcwd()
update_run_script = './update' if system != 'Windows' else 'update.bat'
json_deployfile   = os.path.join(deployment_dir, 'deploy.json')

notify_adapter = __import__('lib.notify.'+settings.NOTIFY_ADAPTER).notify.__getattribute__(settings.NOTIFY_ADAPTER)

cherrypy.config.update({
    'server.socket_port' : settings.PORT,
    'server.socket_host' : settings.HOST,
    'server.thread_pool' : settings.THREAD_POOL,
})

class App(object):
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self, **kwargs):
        if cherrypy.request.method == 'GET':
            return {'msg': 'nothing to do here'}
        elif cherrypy.request.method == 'POST':
            payload = cherrypy.request.body.read()
            headers = cherrypy.request.headers

            if 'X-Hub-Signature' in headers:
                signature       = hmac.new(settings.GITHUB_TOKEN, payload, hashlib.sha1).hexdigest()
                given_signature = headers['X-Hub-Signature']

                if not re.match('sha1=[a-f0-9]{40}$', given_signature):
                    return {'msg': 'Bad signature format'}

                if hmac.compare_digest(signature, given_signature.split('=')[1]):

                    payload_object = json.loads(payload)

                    # Message for new repos added
                    if not 'ref' in payload_object:
                        notify_adapter.repo_added()

                        return {'msg': 'hello, github'}

                    ref = re.match('^refs/(heads|tags)/(.*)$', payload_object['ref']).group(2)

                    # Distinguish main branches and targets
                    if ref == 'develop':
                        repos_dir = os.path.join(settings.BASE_PATH, settings.NAMESPACE+'_develop')
                    elif ref == 'master':
                        repos_dir = os.path.join(settings.BASE_PATH, settings.NAMESPACE)
                    else:
                        return {'msg': 'Push to undefined target "%s"'%ref}

                    commits    = payload_object['commits']
                    head       = payload_object['after']
                    repo_name  = payload_object['repository']['name']
                    repo_dir   = os.path.join(repos_dir, repo_name)

                    if os.path.exists(repo_dir):
                        # dump to file some data
                        json.dump({
                            'head'    : head,
                            'repo'    : repo_name,
                            'started' : datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'commits' : commits,
                            'type'    : 'git',
                            'target'  : ref,
                        }, open(json_deployfile, 'w'))
                        # now we change the working dir in order to find the
                        # update scripts
                        update_script = os.path.join(repo_dir, update_run_script)

                        if not os.path.isfile(update_script):
                            cherrypy.log('"%s" script not found'%update_script, context='ERROR')

                            # Raise error
                            cherrypy.response.status = 501
                            return {'msg': 'Update script for this repo does not exist'}

                        os.chdir(repo_dir)

                        cherrypy.log('deploying repo ' + repo_dir, context='GIT')

                        process = subprocess.Popen([update_run_script])

                        os.chdir(deployment_dir)

                        return {'msg': 'deploy process started, wait for confirm email'}
                    else:
                        cherrypy.response.status = 400
                        return {'msg': 'repo with name %s and target %s doesn\'t exists' % (repo_name, ref)}
                else:
                    cherrypy.response.status = 401
                    return {'msg': 'invalid signature'}
            else:
                cherrypy.response.status = 400
                return {'msg': 'header X-Hub-Signature required'}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def message(self, **kwargs):
        if cherrypy.request.method == 'GET':
            return {'msg': 'nothing to do here, use another verb'}
        elif cherrypy.request.method == 'POST':
            if os.path.isfile(json_deployfile):
                deploy_data = json.load(open(json_deployfile, 'r'))
                deploy_data.update({
                    'finished': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                })

                notify_adapter.deploy_finished(deploy_data)

                try:
                    os.remove(json_deployfile)
                except OSError:
                    cherrypy.log('Attempting to remove unexistent deployfile', context='WARN')

                return {'msg': 'deploy message sent!'}
            else:
                return {'msg': 'missing file'}

if __name__ == '__main__':
    conf = {
        '/': {
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'text/plain')],
        },
    }
    app = App()

    if system != 'Windows':
        PIDFile(cherrypy.engine, os.path.join(deployment_dir, 'deployment.pid')).subscribe()
        Daemonizer(cherrypy.engine,
            stdout=os.path.join(deployment_dir, 'access.log'),
            stderr=os.path.join(deployment_dir, 'error.log')
        ).subscribe()
    else:
        print "Windows does not support fork(), running server in current cmd"

    cherrypy.quickstart(app, '/', conf)
