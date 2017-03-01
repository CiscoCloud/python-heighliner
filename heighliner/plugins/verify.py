import os
import subprocess
import sys
import re

from heighliner import utils


def register(*args, **kwargs):
    return ['verify']


def validate(*args, **kwargs):
    return kwargs['config']


def do(*args, **kwargs):
    print 'Running heighliner verify action'
    sys.stdout.flush()

    meta = kwargs['meta']
    data = kwargs['data']

    if meta.get('type') == 'repo':
        print "Verify repo"
        return

    _run_service(kwargs['meta'], kwargs['data'], kwargs['config'])


def _run_service(meta, data, config):
    plugin_dir = os.path.dirname(__file__)
    service_dir = "/opt/ccs/services/%s" % meta['name']

    if data['type'] == 'testinfra':
        t = ['ansible', 'tests']
        if 'additional_test_dirs' in data:
            t += data['additional_test_dirs']
            t = list(set(t))
        test_dirs = " ".join([os.path.join(service_dir, x) for x in t])

        if os.path.isfile('/etc/ansible/nimbus.py'):
            inventory_file = "/etc/ansible/nimbus.py"
        else:
            inventory_file = "/etc/ansible/hosts"

        env_var = 'HEIGHLINER_VERIFY_TARGET_HOSTS'
        target_hosts = os.environ.get(env_var)

        if not target_hosts:
            target_hosts = meta['name']

        cmd = ("testinfra -v --connection=ansible "
               "--ansible-inventory=%s "
               "--hosts=%s %s") % (
               inventory_file, target_hosts, test_dirs)
        retcode = subprocess.call(cmd, shell=True)
        sys.exit(retcode)

    elif data['type'] == 'serverspec':
        # Copy serverspec common files from heighliner to service dir
        cmd = ("cp %s/verify/serverspec/.rspec %s/serverspec/.") % (
            plugin_dir, service_dir)
        subprocess.call(cmd, shell=True)

        cmd = ("cp %s/verify/serverspec/Rakefile %s/serverspec/.") % (
            plugin_dir, service_dir)
        subprocess.call(cmd, shell=True)

        cmd = ("cp %s/verify/serverspec/spec_helper.rb "
               "%s/serverspec/spec/.") % (plugin_dir, service_dir)
        subprocess.call(cmd, shell=True)

        # get list of play_hosts from Ansible
        cmd = ('ansible-playbook %s/verify/serverspec/list_hosts.yml '
               '--limit %s --list-hosts -e \"service=%s\"') % (plugin_dir,
                                                               meta['name'],
                                                               meta['name'])
        output = subprocess.check_output([cmd], shell=True)

        # Get count
        for x, line in enumerate(output.splitlines(), 1):
            if 'count=' in line:
                line_content = line
                startline = x

        # Parse line and get the count
        res = re.search(r"(count=)([0-9]+)$", line_content)
        count = int(res.group(2))

        # Get hosts
        hosts = []
        for x, line in enumerate(output.splitlines(), 1):
            if (x > startline) and (x <= startline + count):
                hosts.append(line.strip())
        print 'play_hosts: %s' % hosts
        sys.stdout.flush()

        # Run rake
        retcode = 0
        for hostname in hosts:
            os.environ['TARGET_HOST'] = hostname
            cmd = ("cd %s/serverspec && rake spec"
                   ) % service_dir
            retcode = subprocess.call(cmd, shell=True)
            if retcode != 0:
                sys.exit(retcode)

        sys.exit(retcode)

    else:
        print """\nNOTICE: '%s' is not a supported verification test framework.

The following frameworks are supported:
    1. testinfra (preferred)
    2. serverspec (deprecated)""" % data['name']
        sys.exit(1)
