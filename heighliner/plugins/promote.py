import subprocess
import sys
import os
import heighliner.utils as utils


def register(*args, **kwargs):
    return ['promote']


def validate(*args, **kwargs):
    return kwargs['config']


def do(*args, **kwargs):
    print 'Running heighliner promote action'

    data = kwargs['data']
    meta = kwargs['meta']
    retcode = 0

    if meta.get('compose_repo') or meta.get('use_repo'):
        retcode = _promote_repo(meta, data)

    if retcode != 0:
        sys.exit(retcode)


def _promote_repo(meta, data):
    plugin_dir = os.path.dirname(__file__)
    playbook = "%s/repo/main.yml" % plugin_dir

    repo_name = "%s-%s" % (meta['type'],
                           meta['name'])

    meta['service_repo_name'] = repo_name

    extra_vars = {'target': 'build-server',
                  'nimbus_yml': meta,
                  'pulp_repo_action': 'promote'}

    retcode = utils.run_playbook_shell(playbook,
                                       extra_vars,
                                       'build-server')

    return retcode
