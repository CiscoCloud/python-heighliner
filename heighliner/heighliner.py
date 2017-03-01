#!/usr/bin/env python

import click
import glob
import imp
import os
import sys

import utils

CONFIG = {
    'loglevel': 3,
    'lib': '/usr/lib/heighliner/plugins',
    'nimbusfile': '.nimbus.yml',
    'services_base': '/opt/ccs/services',
    'repo_base': '/opt/ccs/repos',
    'dev': False,
    'vaultpass': '/etc/ansible/.ccs.vaultpass.txt',
}


def _load_plugins_from_path(plugin_path, listeners={}):
    if CONFIG['loglevel'] > 0:
        click.echo('Reading plugins from %s' % plugin_path)
    for plugin in glob.glob('%s/*.py' % plugin_path):
        path, fname = os.path.split(plugin)
        name, ext = os.path.splitext(fname)

        if _is_plugin_registered(name, listeners):
            if CONFIG['loglevel'] > 3:
                click.echo('Module already loaded, skipping %s' % name)
            continue

        fp, pathname, desc = imp.find_module(name, [plugin_path])
        try:
            mod = imp.load_module(name, fp, pathname, desc)
            if CONFIG['loglevel'] > 3:
                click.echo('Loaded module: %s' % pathname)
        except ImportError as e:
            print e
        finally:
            if fp:
                fp.close()

        if not hasattr(mod, 'register'):
            if CONFIG['loglevel'] > 3:
                click.echo('Skipping module: %s' % mod)
            continue

        keys = mod.register()
        for key in keys:
            if key not in listeners:
                listeners[key] = []
            listeners[key].append(name)
    return listeners


def _load_plugins(lib_path):
    listeners = _load_plugins_from_path(lib_path)

    mod_path = os.path.dirname(os.path.abspath(__file__))
    plugin_path = '%s/plugins' % mod_path
    listeners_with_builtins = _load_plugins_from_path(plugin_path,
                                                      listeners=listeners)

    return listeners_with_builtins


def _is_plugin_registered(name, listener_map):
    for key in listener_map:
        if name in listener_map[key]:
            return True
    return False


def _validate_nimbus(old_config, listeners):
    config = old_config

    for plugin in listeners:
        if plugin not in config:
            config[plugin] = {}
        if hasattr(sys.modules[plugin], 'validate'):
            valid_config = sys.modules[plugin].validate(config=config[plugin])
            config[plugin] = valid_config

    return config


def _do(key, config, listeners):
    if key not in listeners:
        click.echo('No plugins registered for %s' % key, err=True)
        if CONFIG['loglevel'] > 3:
            click.echo('Registered listeners: %s' % listeners)
    elif key not in config:
        click.echo('Plugin failed to load: %s' % key, err=True)
    else:
        for plugin in listeners[key]:
            sys.modules[plugin].do(key=key, meta=config['meta'],
                                   data=config[key], config=CONFIG)


@click.command()
@click.argument('action')
@click.option('--debug', is_flag=True)
@click.option('--dev', is_flag=True)
@click.option('--verbose', '-v', count=True)
@click.option('--lib', '-l', help='Path to heighliner plugins')
@click.option('--nimbusfile', '-n',
              help='Path to nimbus configuration yaml file')
@click.option('--service-dir', '-s', help='Path to service directory')
def cli(action, debug, dev, verbose, lib, nimbusfile, service_dir):
    global CONFIG

    if lib and os.path.isdir(lib):
        CONFIG['lib'] = lib
    if service_dir and os.path.isdir(service_dir):
        os.chdir(service_dir)
    if nimbusfile and os.path.isfile(nimbusfile):
        CONFIG['nimbusfile'] = nimbusfile
    if debug:
        CONFIG['loglevel'] = 4
        click.echo('DEBUG enabled')
        click.echo(CONFIG)
    if dev:
        CONFIG['dev'] = True
        CONFIG['services_base'] = '/tmp/services'
    if verbose and not debug:
        if verbose > 3:
            verbose = 3
        CONFIG['loglevel'] = verbose
        click.echo('VERBOSITY set to %s' % verbose)

    listeners = _load_plugins(CONFIG['lib'])
    nimbus_yml = utils.load_manifest(CONFIG['nimbusfile'], CONFIG)
    valid_nimbus = _validate_nimbus(nimbus_yml, listeners)
    _do(action, valid_nimbus, listeners)

if __name__ == '__main__':
    cli()
