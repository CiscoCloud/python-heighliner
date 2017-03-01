import os
import subprocess
import sys


def register(*args, **kwargs):
    return ['package']


def validate(*args, **kwargs):
    return kwargs['config']


def do(*args, **kwargs):
    print 'Running heighliner package action'
    meta = kwargs['meta']
    data = kwargs['data']

    plugin_dir = os.path.dirname(__file__)

    if meta.get('type') == 'repo':
        print "Package repo artifact"
        package_script = '%s/package/package-repo.sh %s %s %s' % (
            plugin_dir, meta['name'], meta['version'],
            kwargs['config']['repo_base'])
        subprocess.call(package_script, shell=True)
    elif meta['type'] == 'service':
        package_script = '%s/package/package-service.sh %s %s' % (
            plugin_dir, meta['name'], meta['version'])
        subprocess.call(package_script, shell=True)
    elif 'script' in data:
        subprocess.check_call(data['script'], shell=True)
    elif 'specfile' in data:
        command = ['%s/package/build-rpm.sh' % plugin_dir]
        if 'source' in data:
            command.append("-s")
            command.append("%s" % data['source'])
        if 'specfile' in data:
            command.append("-sfile")
            command.append("%s" % data['specfile'])
        if 'name' in data:
            command.append("-n")
            command.append("%s" % data['name'])
        if 'buildenv' in data and data['buildenv'] == 'mock':
            command.append("-mock")
        print(command)
        try:
            subprocess.call(command)
        except Exception as e:
            print(e)
            sys.exit(1)
