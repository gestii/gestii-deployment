import requests
import cherrypy
from lib.settings_loader import settings

deployment_dir = os.getcwd()
from_text = '%s <%s>'%(settings.FROM_NAME, settings.FROM_MAIL)
templates_environment = Environment(loader=FileSystemLoader(os.path.join(deployment_dir, 'templates')))

def deploy_finished(deploy_data):
    template = templates_environment.get_template('deploy_finished.html')

    r = requests.post(settings.MAILGUN_URL, auth=('api', settings.MAILGUN_KEY), params={
        'from'    : from_text,
        'to'      : ','.join(settings.ADMINS),
        'subject' : '[%s/%s:%s] Finished deploy'%(
            settings.NAMESPACE,
            deploy_data['repo'],
            deploy_data['target']
        ),
        'html'    : template.render(deploy_data),
    })

    cherrypy.log('Mailgun status code: %d'%r.status_code, context='MSG')


def repo_added():
    template = templates_environment.get_template('repo_added.html')

    context = {
        'repo'       : payload_object['hook']['url'].split('/')[5],
        'zen'        : payload_object['zen'],
        'created_at' : payload_object['hook']['created_at'],
    }

    r = requests.post(settings.MAILGUN_URL, auth=('api', settings.MAILGUN_KEY), params={
        'from'    : from_text,
        'to'      : ','.join(settings.ADMINS),
        'subject' : '[%s] Repo added'%(settings.NAMESPACE),
        'html'    : template.render(context),
    })
