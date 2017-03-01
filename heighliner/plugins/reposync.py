import os
import sys
import heighliner.utils as utils

from datetime import datetime, timedelta


def register(*args, **kwargs):
    return ['reposync']


def validate(*args, **kwargs):
    return kwargs['config']


def _get_service_name(meta):
    repo_name = "%s-%s" % (meta['type'],
                           meta['name'])

    if meta.get('compose_repo'):
        # TODO: we currently only support one compose_repo per service
        if meta['compose_repo'][0].get('base_name'):
            repo_name = meta['compose_repo'][0].get('base_name')

    return repo_name


def _sync_repos():
    """
    compose repos in nimbus.yml

    connect to pulp, authenticate, begin composing. Need to handle errors

    We also pass in the unstable repo for a service by default. We allow
    this to be disabled via the inherit_service_packages attribute with
    .nimbus.yml
    """

    plugin_dir = os.path.dirname(__file__)
    playbook = "%s/repo/cobbler_sync.yml" % plugin_dir

    extra_vars = {'target': 'localhost',
                  'pulp_repo_action': 'reposync'}

    retcode = utils.run_playbook_shell(playbook,
                                       extra_vars)

    return retcode


def do(*args, **kwargs):
    print 'Running heighliner reposync action'
    retcode = _sync_repos()

    if retcode != 0:
        sys.exit(retcode)

    meta = kwargs['meta']

    if meta.get('compose_repo') or meta.get('use_repo'):
        print "Heighliner found compose_repo or use_repo block in .nimbus.yml"
        plugin_dir = os.path.dirname(__file__)
        playbook = "%s/repo/main.yml" % plugin_dir

        env_val = os.environ.get('HEIGHLINER_DEPLOY_SKIP_REPO_ERRORS')
        skip_repo_errors = False if env_val is None \
            else True if env_val.lower() == 'true' \
            else False

        meta['service_repo_name'] = _get_service_name(meta)

        extra_vars = {'target': 'localhost',
                      'nimbus_yml': meta,
                      'pulp_repo_action': 'deploy'}

        print "Running heighliner repo action (pulp_repo_action: deploy)"
        retcode = utils.run_playbook_shell(playbook,
                                           extra_vars)

        if not skip_repo_errors and retcode != 0:
            sys.exit(retcode)
