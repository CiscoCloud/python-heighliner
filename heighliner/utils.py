import copy
import os
import subprocess
import yaml
import json
import sys


def setup_service(service, version='latest', config=None):
    extra_vars = {
        "service": service,
        "services_base": config['services_base'],
        "dev": config['dev']
    }
    if version:
        extra_vars['version_string'] = 'version=%s' % version
        playbook = "%s/scripts/setup_service.yml" % os.path.dirname(__file__)
    return run_playbook_shell(playbook, extra_vars)


def teardown_service(service, config=None):
    extra_vars = {
        "service": service,
        "dev": config['dev']
    }
    playbook = "%s/scripts/teardown_service.yml" % os.path.dirname(__file__)
    return run_playbook_shell(playbook, extra_vars)


def run_playbook_shell(playbook_path, extra_vars, limit=None, vault_pass=None):
    json_vars = json.dumps(extra_vars)

    if vault_pass is None:
        ansible_cmd = "ansible-playbook"
    else:
        ansible_cmd = "ansible-playbook --vault-password-file=%s" % vault_pass

    if not extra_vars.get('tags'):
        extra_vars['tags'] = 'all'

    ansible_cmd += " --tags='%s'" % extra_vars['tags']

    if limit is None:
        cmd = "%s %s -e '%s'" % (ansible_cmd,
                                 playbook_path,
                                 json_vars)
    else:
        cmd = "%s %s -e '%s' --limit %s" % (ansible_cmd,
                                            playbook_path,
                                            json_vars,
                                            limit)

    print "Running %s" % cmd

    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    while p.poll() is None:
        sys.stdout.write(p.stdout.readline())
    print p.stdout.read()

    return p.returncode


def _run_playbook(playbook_path, extra_vars):
    import ansible.runner
    import ansible.playbook
    from ansible import callbacks
    from ansible import errors
    from ansible import utils

    stats = callbacks.AggregateStats()
    playbook_cb = callbacks.PlaybookCallbacks(verbose=utils.VERBOSITY)
    runner_cb = callbacks.PlaybookRunnerCallbacks(stats,
                                                  verbose=utils.VERBOSITY)
    inventory = ansible.inventory.Inventory(['localhost'])
    pb = ansible.playbook.PlayBook(
        playbook=playbook_path,
        stats=stats,
        callbacks=playbook_cb,
        runner_callbacks=runner_cb,
        inventory=inventory,
        extra_vars=extra_vars,
    )
    try:
        pb.run()
    except errors.AnsibleError, e:
        print "ERROR: %s" % e


def load_manifest(path, config):
    manifest = dict()

    if config['loglevel'] > 0:
        print 'Reading nimbus configuration from %s' % path
    try:
        manifest = yaml.load(file(path, 'r'))
    except yaml.YAMLError as exc:
        print 'Heighliner found YAML syntax error', exc
        sys.exit(1)
    except IOError as exc:
        print exc.strerror, exc.filename, "Proceeding without config."

    return _prepare_manifest(manifest)


def _prepare_manifest(raw_manifest):
    manifest = copy.deepcopy(raw_manifest)

    manifest['meta'] = {}
    if 'service' in manifest and 'project' in manifest:
        raise RuntimeError('Cannot define both service and project keys')

    elif 'service' in manifest and ('compose_repo' in manifest or
                                    'use_repo' in manifest):
        manifest['meta']['name'] = manifest['service']
        manifest['meta']['type'] = 'service'
        if 'owner' in manifest:
            manifest['meta']['owner'] = manifest['owner']
        manifest['meta']['compose_repo'] = manifest.get('compose_repo')
        manifest['meta']['use_repo'] = manifest.get('use_repo')
    elif 'service' in manifest:
        manifest['meta']['name'] = manifest['service']
        manifest['meta']['type'] = 'service'
        if 'owner' in manifest:
            manifest['meta']['owner'] = manifest['owner']
    elif 'project' in manifest:
        manifest['meta']['name'] = manifest['project']
        manifest['meta']['type'] = 'project'
    elif 'repo' in manifest:
        manifest['meta']['name'] = manifest['repo']
        manifest['meta']['type'] = 'repo'
        manifest['meta']['compose_repo'] = manifest.get('compose_repo')
        manifest['meta']['use_repo'] = manifest.get('use_repo')
    else:
        manifest['meta']['type'] = 'project'

    if 'version' in manifest:
        manifest['meta']['version'] = manifest['version']

    return manifest
