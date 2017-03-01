import os
import sys
import subprocess
import re

from heighliner import utils


def register(*args, **kwargs):
    return ['deploy']


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


def do(*args, **kwargs):

    meta = kwargs['meta']
    data = kwargs['data']

    if meta.get('compose_repo') or meta.get('use_repo'):
        print "Heighliner found compose_repo or use_repo block in .nimbus.yml"
        plugin_dir = os.path.dirname(__file__)
        playbook = "%s/repo/main.yml" % plugin_dir

        env_val = os.environ.get('HEIGHLINER_DEPLOY_SKIP_REPO_ERRORS')
        skip_repo_errors = False if env_val is None \
            else True if env_val.lower() == 'true' \
            else False

        env_var = 'HEIGHLINER_DEPLOY_TARGET_HOSTS'
        target_hosts = os.environ.get(env_var)

        if not target_hosts:
            target_hosts = meta['name']

        meta['service_repo_name'] = _get_service_name(meta)

        extra_vars = {'target': target_hosts,
                      'nimbus_yml': meta,
                      'pulp_repo_action': 'deploy'}

        print "Running heighliner repo action (pulp_repo_action: deploy)"
        retcode = utils.run_playbook_shell(playbook,
                                           extra_vars,
                                           meta['name'])
        if not skip_repo_errors and retcode != 0:
            sys.exit(retcode)

    if meta.get('type') == 'service':
        _run_service(meta, data, kwargs['config'],
                     recurse=True)


def _pulp_play(meta, plugin_dir, extra_vars, play):
    if meta.get('compose_repo') or meta.get('use_repo'):
        provision_vars = {'target': extra_vars['target'],
                          'nimbus_yml': meta,
                          'pulp_repo_action': play}

        playbook = "%s/repo/main.yml" % plugin_dir
        print "Running heighliner repo action (pulp_repo_action: %s)" % play
        retcode = utils.run_playbook_shell(playbook,
                                           provision_vars,
                                           meta['name'])


def _pulp_provision(meta, plugin_dir, extra_vars):
    _pulp_play(meta, plugin_dir, extra_vars, 'provision')


def _pulp_deprovision(meta, plugin_dir, extra_vars):
    _pulp_play(meta, plugin_dir, extra_vars, 'deprovision')


def _run_service(meta, data, config, recurse=False):
    plugin_dir = os.path.dirname(__file__)
    service_dir = "/opt/ccs/services/%s" % meta['name']
    retcode = 0

    if not data:
        raise Exception("deploy block not specified in %s" %
                        config['nimbusfile'])

    if 'services' in data and recurse:
        print "Heighliner found deploy:services block in .nimbus.yml"
        _run_bundle(data['services'], config)
    elif 'script' in data:
        retcode = subprocess.call(data['script'], shell=True)
    elif data.get('type') == 'ansible':
        service_data_dir = "%s/data/" % service_dir
        service_data_regex = r'^service\.(yml|yaml)$'
        service_data_file = ''

        if os.path.isdir(service_data_dir):
            for data_file in os.listdir(service_data_dir):
                if re.match(service_data_regex, data_file):
                    if data_file == 'service.yml':
                        print "Your services data file, service.yml must"
                        print "be named service.yaml. All YAML files in the"
                        print "data directory must have a .yaml extension."
                        sys.exit(1)
                    service_data_file = "%s%s" % (service_data_dir, data_file)
                    break

        service_group_vars = "/etc/ansible/group_vars/%s.yaml" % meta['name']
        ansible_lib_path = "/usr/share/ansible:/opt/cis/tools/ansible/library"
        vaultpass = None
        if not config['dev']:
            vaultpass = config['vaultpass']
        if (os.path.isfile(service_data_file) and
                not os.path.isfile(service_group_vars)):
            os.symlink(service_data_file, service_group_vars)
        if os.path.isdir("%s/ansible/library" % service_dir):
            os.environ['ANSIBLE_CONFIG_LIBRARY'] = "%s:%s/ansible/library" % (
                ansible_lib_path, service_dir)
        if 'role' in data:
            print "Not Implemented"
        elif 'playbook' in data:
            # TODO: Implement argument passing for plugins. The click framework
            # supports this
            env_var = 'HEIGHLINER_DEPLOY_TARGET_HOSTS'
            target_hosts = os.environ.get(env_var)
            heighliner_tags = os.environ.get('HEIGHLINER_DEPLOY_TAGS')

            if not target_hosts:
                target_hosts = meta['name']

            if not heighliner_tags or heighliner_tags.strip() == '':
                heighliner_tags = 'all'

            extra_vars = {'target': target_hosts,
                          'tags': heighliner_tags,
                          'version': meta['version']}

            meta['service_repo_name'] = _get_service_name(meta)

            print "Running playbook {0}".format(data['playbook'])
            print "limited to hosts in the {0} group".format(meta['name'])
            print "with extra vars {0}".format(extra_vars)

            # setup the pulp repo for this services
            _pulp_provision(meta, plugin_dir, extra_vars)

            playbook = 'ansible/%s' % data['playbook']
            print "Running heighliner deploy action for %s (version: %s)" \
                  % (meta['name'], meta['version'])
            retcode = utils.run_playbook_shell(playbook,
                                               extra_vars,
                                               meta['name'],
                                               vaultpass)

            _pulp_deprovision(meta, plugin_dir, extra_vars)

        if os.path.islink(service_group_vars):
            os.remove(service_group_vars)
    elif data.get('type') == 'puppet':
        if 'manifest' in data:
            playbook = "%s/build/puppet/puppet_apply.yml" % plugin_dir
            env_var = 'HEIGHLINER_DEPLOY_TARGET_HOSTS'
            target_hosts = os.environ.get(env_var)

            extra_vars = {'service': meta['name'],
                          'version': meta['version'],
                          'manifest': data['manifest']}

            # F2188 - for multiple puppet run support.
            # Two options are available to puppet users in the nimbus.yml and
            # injected into deploy via the data dictionary.  The options get
            # processed by the below code and are added to the extra_vars
            # dictionary.  Below is a description of the new options.  If
            # both options are unspecified then the default values will
            # preserve legacy behavior.  The defaults for these options arei
            # mirrored in the puppet_apply.yml in the event they are unset.
            # num_of_runs (Default = 1) - This spcifies how many times puppet
            #  apply should be run.  The num_of_runs is capped at 8.  Values
            #  greater than 8 will be automatically set to 8.
            # ignore_puppet_errors (Default = true) - if set to false then
            #  failed puppet runs will result in failed ansible runs.
            extra_vars['num_of_runs'] = 1
            if 'num_of_runs' in data:
                if data['num_of_runs'] > 8:
                    extra_vars['num_of_runs'] = 8
                else:
                    extra_vars['num_of_runs'] = data['num_of_runs']

            extra_vars['ignore_puppet_errors'] = str(True)
            if 'ignore_puppet_errors' in data:
                extra_vars['ignore_puppet_errors'] = \
                  str(data['ignore_puppet_errors'])

            if not target_hosts:
                extra_vars['target'] = meta['name']
            else:
                extra_vars['target'] = target_hosts

            _pulp_provision(meta, plugin_dir, extra_vars)

            print "Running heighliner deploy action for %s (version: %s)" \
                  % (meta['name'], meta['version'])
            retcode = utils.run_playbook_shell(playbook,
                                               extra_vars,
                                               meta['name'])
            _pulp_deprovision(meta, plugin_dir, extra_vars)

    elif data.get('type') == 'docker':
        ports = ""
        if 'ports' in data:
            ports = data['ports']
        dockerfile = os.path.join(service_dir, 'docker', 'Dockerfile')
        if os.path.isfile(dockerfile):
            extra_args = {
                'service': meta['name'],
                'docker_dir': "%s/docker" % service_dir,
                'docker_ports': ports,
            }
            playbook = "%s/deploy/docker_dockerfile.yml" % plugin_dir
            utils.run_playbook_shell(playbook, extra_args, meta['name'])
    else:
        msg = "deploy: script or deploy type not specified in %s" % \
              config['nimbusfile']
        raise Exception(msg)

    if retcode != 0:
        sys.exit(retcode)


def _run_bundle(services, config):
    managed_services = []
    cwd = os.getcwd()

    for service in services:
        print "Installing service %s" % service
        retcode = utils.setup_service(service, config=config)
        if retcode != 0:
            sys.exit(retcode)
        managed_services.append(service)
        service_path = "%s/%s" % (config['services_base'], service)
        service_manifest_path = "%s/.nimbus.yml" % service_path
        if os.path.isfile(service_manifest_path):
            manifest = utils.load_manifest(service_manifest_path, config)
            # TODO: Refactor playbook execution to not require chdir
            # Ideally, we can execute a heighliner action from any working
            # directory and any source directory.
            os.chdir(service_path)
            _run_service(manifest['meta'], manifest['deploy'], config)
            os.chdir(cwd)

    for service in managed_services:
        print "Uninstalling service %s" % service
        utils.teardown_service(service, config=config)
