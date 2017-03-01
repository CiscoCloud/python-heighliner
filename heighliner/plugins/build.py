import os
import sys
import shutil
import subprocess
import heighliner.utils as utils

from datetime import datetime, timedelta


def register(*args, **kwargs):
    return ['build']


def validate(*args, **kwargs):
    return kwargs['config']


def do(*args, **kwargs):
    print 'Running heighliner build action'

    meta = kwargs['meta']
    data = kwargs['data']

    if 'owner' not in meta and meta['type'] == 'service':
        print "ERROR: owner key is missing in .nimbus.yml. " \
              "This is a required key for service repo."
        print "Visit https://confluence.sco.cisco.com/display/CCS/" \
              "GoCD+RBAC+Scrum+Team+Configuration for more details."
        sys.exit(1)

    plugin_dir = os.path.dirname(__file__)
    retcode = 0

    if os.path.isfile('.gitmodules'):
        print "Updating git submodules"
        cmd = 'git submodule init && git submodule update'
        subprocess.call(cmd, shell=True)

    install_roles = 'install_roles.yaml' \
        if os.path.isfile('install_roles.yaml') \
        else 'install_roles.yml' if os.path.isfile('install_roles.yml') else ''
    if install_roles:
        # BUG: https://github.com/ansible/ansible/issues/13563
        # [2.0-rc1] ansible-galaxy no longer respects path in requirements file
        # so default the installation to ansible/roles dir
        print "Installing roles in ansible/roles dir"
        cmd = 'ansible-galaxy install --no-deps --ignore-errors \
               --roles-path=ansible/roles --role-file=%s' % install_roles
        retcode = subprocess.call(cmd, shell=True)

    if meta.get('type') == 'service':
        if 'script' in data:
            retcode = subprocess.call(data['script'], shell=True)
        elif os.path.isdir('puppet'):
            if not os.path.isfile('puppet/hiera.yaml'):
                path = '%s/build/puppet/hiera.yaml' % plugin_dir
                shutil.copy(path, 'puppet')
            if not os.path.isfile('puppet/puppet.conf'):
                path = '%s/build/puppet/puppet.conf' % plugin_dir
                shutil.copy(path, 'puppet')
            if os.path.isfile('puppet/Puppetfile'):
                cmd = 'cd puppet && librarian-puppet install'
                retcode = subprocess.call(cmd, shell=True)
    elif 'script' in data:
        retcode = subprocess.call(data['script'], shell=True)

    sys.exit(retcode)
