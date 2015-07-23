# -*- coding: utf-8 -*-

# Host for the server
HOST = '127.0.0.1'

# Port for the server
PORT = 4567

# Number of child threads
THREAD_POOL = 2

# Directory where repos are located
BASE_PATH = '/'

# The namespace (group repos)
NAMESPACE = ''

# GitHub Key (64 random chars)
GITHUB_TOKEN = ''

NOTIFY_ADAPTER = 'slack' # Where to notify deploys (one of 'slack', 'mailgun')

SLACK_HOOK = 'https://hooks.slack.com/services/YOUR/HOOK/KEY'

# Mailgun Key
MAILGUN_KEY = ''

# Mailgun URL
MAILGUN_URL = 'https://api.mailgun.net/v2/<user>/messages'

# Admins, where to send the deploy mails
ADMINS = [
    'support@example.com',
    # ...
]

# Email address that sends deploy messages
FROM_MAIL = 'deploy@example.com'

# Header for sent emails
FROM_NAME = 'Deploy service'
