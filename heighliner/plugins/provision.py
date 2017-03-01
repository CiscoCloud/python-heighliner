import os
import sys

from heighliner import utils


def register(*args, **kwargs):
    return ['provision']


def validate(*args, **kwargs):
    return kwargs['config']


def do(*args, **kwargs):
    print 'Running heighliner provision action'
    meta = kwargs['meta']
    data = kwargs['data']
    config = kwargs['config']

    _provision_host(meta, data, config)


def _provision_host(meta, data, config):
    plugin_dir = os.path.dirname(__file__)
    env_var = meta['name'].replace('-', '_').upper()

    # TODO Add argument passing for heighliner plugins
    # like this. We want to move foward with that instead
    # of using environment variables this way.

    target_hosts = os.environ.get('HEIGHLINER_PROVISION_TARGET_HOSTS')
    virtual_state = os.getenv('HEIGHLINER_PROVISION_VIRTUAL_STATE', 'present')

    if not virtual_state:
        virtual_state = 'present'

    if not target_hosts:
        target_hosts = meta['name']

    extra_vars = {'target': target_hosts,
                  'virtual_state': virtual_state}

    if virtual_state == 'absent':
        play = "provision/host.yml"
    else:
        play = "provision/present.yml"

    playbook = "%s/%s" % (plugin_dir, play)

    print "Running playbook {0}".format(playbook)
    print "limited to hosts in the {0} group".format(meta['name'])
    print "with extra vars {0}".format(extra_vars)
    retcode = utils.run_playbook_shell(playbook, extra_vars, meta['name'])
    sys.exit(retcode)
