# -*- coding: utf-8 -*-

# Host for the server
HOST = '127.0.0.1'

# Name for this server
NAME = 'remote'

# Port for the server
PORT = 4567

# Number of child threads
THREAD_POOL = 2

# GitHub Key (64 random chars)
GITHUB_TOKEN = ''

# Where to notify deploys (one of 'slack', 'mailgun', 'file')
NOTIFY_ADAPTER = 'slack'

# Hook to be used with 'slack' notify adapter
SLACK_HOOK = 'https://hooks.slack.com/services/YOUR/HOOK/KEY'

# Only if notify adapter is mailgun
MAILGUN_KEY = ''

# Only if notify adapter is mailgun
MAILGUN_URL = 'https://api.mailgun.net/v2/<user>/messages'

# Admins, where to send the deploy mails (if mailgun or other email adapter)
ADMINS = [
    'support@example.com',
    # ...
]

# Email address that sends deploy messages (in mailgun or email adapter)
FROM_MAIL = 'deploy@example.com'

# Header for sent emails (if mailgun or email adapter)
FROM_NAME = 'Deploy service'

# Configured repositories to work with
# also allow configuration in a per-branch basis
REPOS = {
    'remote_name': {
        'master': '/path/to/master',
        'develop': '/path/to/develop',
    },
}
