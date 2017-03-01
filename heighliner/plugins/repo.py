import os
import sys
import heighliner.utils as utils

from datetime import datetime, timedelta


def register(*args, **kwargs):
    return ['repo']


def validate(*args, **kwargs):
    return kwargs['config']


def _compose_repo(meta):
    """
    compose repos in nimbus.yml

    connect to pulp, authenticate, begin composing. Need to handle errors

    We also pass in the unstable repo for a service by default. We allow
    this to be disabled via the inherit_service_packages attribute with
    .nimbus.yml
    """

    plugin_dir = os.path.dirname(__file__)
    playbook = "%s/repo/compose.yml" % plugin_dir

    repo_name = "%s-%s" % (meta['type'],
                           meta['name'])

    meta['service_repo_name'] = repo_name

    unstable_repo_name = "%s-%s_unstable" % (repo_name, meta['version'])

    inherit_service = {'name': unstable_repo_name,
                       'empty_include_result_fails': True,
                       'empty_exclude_result_fails': False,
                       'include': {}}

    if meta.get('compose_repo'):
        for idx, repo in enumerate(meta['compose_repo']):
            if repo.get('inherit_service_packages'):
                inherit = repo['inherit_service_packages']
                if inherit == 'yes' or inherit is True:
                    meta['compose_repo'][idx]['inherit'].append(
                        inherit_service)

    extra_vars = {'target': 'build-server[0]:sdlc-docker[0]',
                  'nimbus_yml': meta,
                  'pulp_repo_action': 'compose'}

    retcode = utils.run_playbook_shell(playbook,
                                       extra_vars,
                                       'build-server[0]:sdlc-docker[0]')

    return retcode


def do(*args, **kwargs):
    print 'Running heighliner repo action'

    meta = kwargs['meta']
    data = kwargs['data']
    config = kwargs['config']

    if (not config['dev'] and
            (meta.get('compose_repo') or meta.get('use_repo'))):
        retcode = _compose_repo(meta)
        if retcode != 0:
            sys.exit(retcode)

    plugin_dir = os.path.dirname(__file__)
    retcode = 0

    sys.exit(retcode)
