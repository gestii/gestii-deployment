#!/usr/bin/env python2
import os
import sys
import json
import argparse
from server import deploy_repo

def deploy_dir(string):
    if not os.path.isdir(string):
        raise argparse.ArgumentTypeError("%r is not a directory" % string)
    if not os.path.isfile(os.path.join(string, '.deployfile')):
        raise argparse.ArgumentTypeError("%r is not deployment enabled" % string)
    return string

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Deploys a local repo')

    parser.add_argument('path',
        type = deploy_dir,
        help = 'absolute path to the repo',
    )
    parser.add_argument('-t' '--task',
        default  = 'update',
        help     = 'The task to execute (by default update)',
        dest     = 'task',
    )

    args = parser.parse_args()

    update_script = json.load(open(os.path.join(args.path, '.deployfile')))

    deploy_repo(args.path, {}, update_script, args.task)
