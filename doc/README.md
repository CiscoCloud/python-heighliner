Heighliner
==========

## Dev environment

Clone the repo and cd into it.  Load the plugins via submodule.
```
cd heighliner
git submodule init
git submodule update
```

Create a virtualenv.
```
virtualenv .venv
. .venv/bin/activate
```

Install requirements
```
pip install -r requirements.txt
```

To view the pretty version of the documentation, launch a webserver from the doc folder.
```
cd doc
python -m SimpleHTTPServer
```

# Plugins

Heighliner uses plugins to parse, validate, and perform actions on top-level keys in a `.nimbus.yml` file.  Plugins are kept in the `plugins/` directory of the heighliner project.  User-supplied plugins will be added once the config-file mechanism is in place.

## API

Each plugin must implement the following functions:

### register
Heighliner will run the `register()` function on all plugins, passing no arguments.  The plugin should return a list of keys that it is interested in processing.
``` python
# This plugin takes action based on the 'doc' section of the .nimbus.yml
def register(*args, **kwargs):
  return ['doc']
```

### do
When a `.nimbus.yml` file is parsed, each non-meta key will trigger actions for interested plugins.  It will do this by calling the `do()` function, passing the following keyword arguments:
``` python
# The key, meta, and data should be extracted from the kwargs list.
def do(*args, **kwargs):
  key = kwargs['key']
  meta = kwargs['meta']
  data = kwargs['data']
  config = kwargs['config']
  print key, meta, data
```
 * `key` - the key that triggered the action
 * `meta` - a hash of the meta keys, providing details about the source repository
 * `data` - the hash of values for the triggered key
 * `config` - the heighliner configuration settings, set by default or via a heighliner.conf file

## Base Plugins
Plugins that come installed with the heighliner python package.
### meta (non-plugin)

Meta keys are currently hard-wired into the heighliner tool, making meta a non-plugin.  Meta key management is intended to be extracted to a plugin once the plugin architecture is improved to allow modification of the nimbus hash. Meta keys include:

 * name
 * type
 * version
 * description

### build

The base `build` action is triggered in the pipeline once a commit is merged into a branch.  The built-in build plugin only supports `script` execution.

### check

The base `check` action is meant to be triggered in the pipeline once a new patch-set is available for review. The built-in check plugin only supports `script` execution.

### deploy

The base `deploy` action is meant to deploy a service.  The built-in deploy plugin supports `script` and ansible `playbook` deployments. The ansible inventory this action
will execute against can be scoped with environment variables.

```
HEIGHLINER_DEPLOY_TARGET_HOSTS={service-name-group|ccs-a-instance-001}
```

### package

The base `package` action is meant to package project using spec file.  For more details on using spec based packaging refer heighliner-sample-pkg repo in gerrit.

### promote

The `promote` action is meant to promote the per-service pulp repo from proposed to stable state. It entails snapshotting a repository thats in a proposed state. This snapshot creates a new repo that has the `_proposed` suffix removed. The heighliner `promote` action should only ever be run via the Go pipeline for the service you want to promote.

### provision

The `provision` action is meant to instantiate and destroy OpenStack VMs that exist as part of the ansible inventory for a heighliner service. The ansible inventory this action will execute against can be scoped with environment variables. It should be noted that the **definition** of the VMs is something that happens before the provision action can be utilized. This means you must define the VMs via a hosts.d entry first. The heighliner `provision` action should only ever be run via the Go pipeline for the service whose VMs need to be provisioned.

```
SERVICE_NAME_VIRTUAL_STATE={absent|present}
SERVICE_NAME_TARGET_HOSTS={service-name-group|ccs-a-instance-001}
```

The `provision` action applies the following ansible roles from the cis-tools repository

 * common
 * hosts_file
 * package_config
 * provision
 * puppet
 * ntp

### repo

The `repo` action is meant to create a per-service pulp repo based on the compose_repo block in .nimbus.yml. The heighliner `repo` action is executed by Jenkins at the end of successful service repo build.

### reposync

The `reposync` action is meant to set up the per-service pulp repo context for the service that is being deployed. It entails making sure that all site/infra node mirrors are created/updated, and it will also install the per-service pulp repo on to the target VMs. The heighliner `reposync` action gets executed by heighliner `deploy` action.

### verify

The base `verify` action is meant to verify a deployed service.  The built-in verify plugin supports `serverspec` resource types testing.

## CCS Plugins

When heighliner is installed for use in CCS, the base plugins are replaced with more full-featured versions.  Basic functions can be executed using the built-in plugins (including bootstrapping the heighliner service deployment with a basic deployment).
