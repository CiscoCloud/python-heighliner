.nimbus.yml - Getting Started
=============================

All repos in CCS fall into one of two categories:

 * Source Repo - Any arbitrary source code that should be tested, built into a package, and deployed.  Examples include: java, python, ruby or other software applications; puppet modules, ansible roles, or other libraries for shared use; plugins, scripts, or other arbitrary code.  Basically, any application or code that provides a desired functionality.

 * Service Repo - The wrapper code that defines all of the informaiton required to deploy the above application into a CCS environment.  A service repo contains all of the: deployment code, documentation, monitoring, integration tests, and other "defintion-of-done" requirements for qa, ops, and release teams to test and support your application.

For both repo types, the pipeline will take actions based on the contents of an included `.nimbus.yml` file.

# Source Project Examples

## Python Package

```
project: python-package
version: 1.0.0
check:
  script: nosetests
build:
  script: ./build.sh
#deploy: _  # No deploy action available for source projects
```

# Service Examples

## Ansible deployment

```
service: ansible-service
version: 1.0.0
check:
  script: ansible-lint
#build: _ # build step is set by the pipeline, will be ignored if specified
deploy:
  type: ansible
  playbook: deploy.yml
verify:
  type: serverspec
```

## Puppet deployment
```
service: puppet-service
version: 1.0.0
check:
  script: rake spec
#build: _ # build step is set by the pipeline, will be ignored if specified
deploy:
  type: puppet
  manifest: manifests/site.pp
verify:
  type: serverspec
```
