# -*- coding: utf-8 -*-
import cherrypy
import hashlib
import hmac
import json
import os
import re
import subprocess
import platform
from multiprocessing import Process
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from lib.settings_loader import settings
from cherrypy.process.plugins import PIDFile
from cherrypy.process.plugins import Daemonizer
from time import sleep
from functools import wraps
from actions import deploy_repo, rollback_repo

is_windows        = platform.system() == 'Windows'
deployment_dir    = os.getcwd()
json_deployfile   = os.path.join(deployment_dir, 'deploy.json')

notify_adapter = __import__('lib.notify.'+settings.NOTIFY_ADAPTER).notify.__getattribute__(settings.NOTIFY_ADAPTER)

cherrypy.config.update({
    'server.socket_port' : settings.PORT,
    'server.socket_host' : settings.HOST,
    'server.thread_pool' : settings.THREAD_POOL,
})

def check_signature(endpoint):
    """A wrapper middleware that checks the payload signature
    """
    @wraps(endpoint)
    def wrapper(*args, **kwargs):
        if cherrypy.request.method != 'POST':
            return {'msg': 'Nothing to do here, change request method'}

        headers = cherrypy.request.headers

        if 'X-Hub-Signature' not in headers:
            cherrypy.response.status = 400
            return {'msg': 'header X-Hub-Signature required'}

        payload         = cherrypy.request.body.read()
        signature       = hmac.new(settings.GITHUB_TOKEN, payload, hashlib.sha1).hexdigest()
        given_signature = headers['X-Hub-Signature']

        if not re.match('sha1=[a-f0-9]{40}$', given_signature):
            cherrypy.response.status = 400
            return {'msg': 'Bad signature format: sha1=<40 digit hex string>'}

        if not hmac.compare_digest(signature, given_signature.split('=')[1]):
            cherrypy.response.status = 401
            return {'msg': 'invalid signature'}

        args += (payload,)
        return endpoint(*args, **kwargs)
    return wrapper

class App(object):
    @cherrypy.expose
    @cherrypy.tools.json_out()
    @check_signature
    def index(self, payload, **kwargs):
        payload_object  = json.loads(payload)

        # Message for new repos added
        if not 'ref' in payload_object:
            notify_adapter.repo_added(payload_object)

            return {'msg': 'hello, github'}

        match = re.match('^refs/(heads|tags)/(.*)$', payload_object['ref'])
        if not match:
            return {'msg': 'malformed ref'}

        ref = match.group(2)

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

        if not os.path.exists(repo_dir):
            return {'msg': 'repo with name %s and target %s doesn\'t exists' % (repo_name, ref)}

        deployfile = os.path.join(repo_dir, '.deployfile')

        if not os.path.isfile(deployfile):
            cherrypy.log('"%s" not found'%deployfile, context='ERROR')

            # Raise error
            cherrypy.response.status = 501
            return {'msg': 'missing .deployfile'}

        with open(deployfile, 'r') as deploy_script:
            try:
                script = json.load(deploy_script)['update']
            except ValueError:
                cherrypy.response.status = 501
                return {'msg': 'malformed .deployfile'}
            except KeyError:
                cherrypy.response.status = 501
                return {'msg': "Missing 'update' task in .deployfile"}

        deploy_data = {
            'head'    : head,
            'repo'    : repo_name,
            'started' : datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'commits' : commits,
            'type'    : 'git',
            'target'  : ref,
        }

        process = Process(target=deploy_repo, args=(repo_dir, deploy_data, script))
        process.start()
        process.join(120)

        return {'msg': 'deploy process started, wait for confirmation'}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @check_signature
    def rollback(self, payload):
        payload_object = json.loads(payload)

        if not 'ref' in payload_object:
            return {'msg': 'Missing required ref field'}
        ref = payload_object['ref']

        # Distinguish main branches and targets
        if ref == 'develop':
            repos_dir = os.path.join(settings.BASE_PATH, settings.NAMESPACE+'_develop')
        elif ref == 'master':
            repos_dir = os.path.join(settings.BASE_PATH, settings.NAMESPACE)
        else:
            return {'msg': 'Push to undefined target "%s"'%ref}

        repo_name = payload_object['repo']
        repo_dir  = os.path.join(repos_dir, repo_name)

        if not os.path.exists(repo_dir):
            return {'msg': 'repo with name %s and target %s doesn\'t exists' % (repo_name, ref)}

        deployfile = os.path.join(repo_dir, '.deployfile')

        try:
            script = json.load(open(deployfile, 'r'))['update']
        except ValueError:
            cherrypy.response.status = 501
            return {'msg': 'malformed .deployfile'}
        except KeyError, IOError:
            script = []

        rollback_data = {
            'repo'    : repo_name,
            'started' : datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }

        if 'tag' in payload_object:
            rollback_data['tag'] = payload_object['tag']

        process = Process(target=rollback_repo, args=(repo_dir, rollback_data, script))
        process.start()
        process.join(120)

        return {'msg': 'rollback process started, wait for confirmation'}


if __name__ == '__main__':
    conf = {
        '/': {
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'text/plain')],
        },
    }
    app = App()

    if not is_windows:
        PIDFile(cherrypy.engine, os.path.join(deployment_dir, 'deployment.pid')).subscribe()
        Daemonizer(cherrypy.engine,
            stdout=os.path.join(deployment_dir, 'logs/access.log'),
            stderr=os.path.join(deployment_dir, 'logs/error.log')
        ).subscribe()
    else:
        print("Windows does not support fork(), running server in current cmd")

    cherrypy.quickstart(app, '/', conf)
