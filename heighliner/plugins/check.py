import subprocess
import sys


def register(*args, **kwargs):
    return ['check']


def validate(*args, **kwargs):
    return kwargs['config']


def do(*args, **kwargs):
    print 'Running heighliner check action'

    data = kwargs['data']
    meta = kwargs['meta']

    if 'owner' not in meta and meta['type'] == 'service':
        print "ERROR: owner key is missing in .nimbus.yml. " \
              "This is a required key for service repo."
        print "Visit https://confluence.sco.cisco.com/display/CCS/" \
              "GoCD+RBAC+Scrum+Team+Configuration for more details."
        sys.exit(1)

    if 'script' in data:
        retcode = subprocess.call(data['script'], shell=True)
        sys.exit(retcode)
