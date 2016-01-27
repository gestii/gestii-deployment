#!/usr/bin/env python2
import sys
import json
import os
from server import deploy_repo

if __name__ == '__main__':
	if len(sys.argv) == 1:
		print('missing repo dir')
		exit(1)

	update_script = json.load(open(os.path.join(sys.argv[1], '.deployfile')))

	deploy_repo(sys.argv[1], {}, update_script)
