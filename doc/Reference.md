.nimbus.yml - Full Reference
============================

## meta

### name
The name of the project or service.  `REQUIRED` unless using the `service` or `project` shortcut.
```
name: foostack
```

Default: `None`

### type

The type of the repo described by the Nimbusfile. `REQUIRED` unless using the `service` or `project` shortcut.

Default: `None`

Options:

`service` - a repo containing all requirements to deploy a service into Nimbus.
```
type: service
```

`project` - any other kind of project.
```
type: project
```


A shortcut is available to combine the name and type into one entry. The 'project' and 'service' keys are mutually exclusive; validation of the Nimbusfile will fail if both are defined.
```
project: foostack
# is equivalent to
name: foostack
type: project
```

### version

The current version of the project or service.  The version is applied to packages generated from the repository.
```
version: 1.0.0
```

Default: `None`

### description

A short description of the service or project.
```
description: A most valuable service
```

Default: `<blank>`

## check

Heighliner `check` action will be executed by `Jenkins` when the gerrit change set is submitted for review.

### script

A script to be executed.
```
check:
  script: /path/to/script.sh
```
## build

Heighliner `build` action will be executed by `Jenkins` when the gerrit change set is merged. For `service repo`, the build section is ignored.  The service package will be built using a standard build process.  For arbitrary source projects, a `script` should be supplied.

### script

A script to be executed.
```
build:
  script: /path/to/script.sh
```

## package

Heighliner `package` action will be executed by `Jenkins` followed by `build` action. when the gerrit change set is merged. It will build packages using `fpm`.

```
package:
  name: helloworld
  specfile: ./hello.spec
  source: ./src
  buildenv: mock
```

### name

Name of the package.
```
package:
  name: some-package-name
```

### specfile

Location of the .spec file.
```
package:
  specfile: /path/to/specfile
```

### source

Location of the source directory.
```
package:
  source: /path/to/src/directory
```

### buildenv

Build packages via `mock`.
```
package:
  buildenv: mock
```

## deploy

Heighliner `deploy` action will be executed by `Go`. Supported deployment tools: `ansible` and `puppet`.

### type: ansible

An `ansible-playbook` can be specified to perform the deployment.  Any roles required by the playbook should be vendored into the `ansible/` directory in the service repo.
```
ansible
├── deploy.yml # playbooks can be placed anywhere within the ansible directory
└── roles/     # roles can be vendored in under the ansible directory
```

#### playbook

The path to the playbook to perform the deployment, relative to the `ansible/` directory in the repo.
```
deploy:
  type: ansible
  playbook: deploy.yml
```

### type: puppet

A puppet manifest can be specified to perform the deployment.  All modules and manifests will be copied to the relevant hosts and run via `puppet apply`.  Any modules required by the manifest should be vendored into the `puppet/modules/` directory in the service repo.
```
puppet
├── manifests/ # manifests for deployment
└── modules/   # modules can be vendored in here
```

#### manifest

The path to the puppet manifest to perform the deployment, relative to the `puppet/` directory in the repo.
```
deploy:
  type: puppet
  manifest: manifests/site.pp
```

### type: docker (planned)

A Docker container will be built and deployed from the included Dockerfile.  Support for existing images (from registry) is on the Roadmap.
```
docker
└── Dockerfile
```

#### ports

The ports string will be passed to the `docker run` command.  The string should be formatted according to the docker cli specification.
```
deploy:
  type: docker
  ports: "8080:80"
```

### services (planned)

Provide a list of services to deploy as a part of this service, effectively turning this service into a meta-service.  Services must be supplied in a list, without the 'service-' prefix.  The services will be deployed in the order listed.  If any service deployment fails, the entire deployment will halt.
```
deploy:
  services:
    - base
    - proxy
```

To peg a service to a particular version, use the `==` separator between the service name and version.  The version will be used to resolve the version and release from the yum/apt repository.
```
deploy:
  services:
    - base==0.1.0   # Installs service-base-0.1.0 from yum/apt
    - proxy         # Installs service-base (latest) from yum/apt
```

## compose_repo

Heighliner will use `compose_repo` block to construct a per-service pulp repo based on what is specified within it. It utilizes the Pulp API and the syntax is mongodb compatible. The per-service pulp repo creation will be executed by `Jenkins` at the end of successful service repo build.

```
compose_repo:
  - inherit_service_packages: no
    basic_auth: no
    build_proposed: yes
    inherit:
      - name:  ccs-static-artefacts_unstable
        empty_include_result_fails: yes
        empty_exclude_result_fails: no
        include:
          'name':
            '$regex': '.*'
      - name: ccs-api_unstable
        empty_include_result_fails: yes
        empty_exclude_result_fails: no
        include:
          'name':
            '$regex': '.*'
      - name: ccs-idmapi_unstable
        empty_include_result_fails: yes
        empty_exclude_result_fails: no
        include:
          'name':
            '$regex': '.*'
```

### base_auth

This tells heighliner that you do not want your repository to be located in the /rpm/secure path, which is locked down via HTTP Basic Auth and via IP Address ACL. Valid values are `yes` and `no`.

```
base_auth: no
```

### build_proposed

If you would like to skip the promotion step and not create a proposed repo, set this to `no`. Valid values are `yes` and `no`.

```
build_proposed: yes
```

### priority

This will correspond to the yum repo priority within the .repo file.

```
priority: 99
```

### inherit

The inherit block tells heighliner that you want to compose your repo by inheriting from another repo. In this case we are saying we want to inherit from the repo named rhel-7-server-openstack-5.0-rpms_unstable. The include block states that we want to include rpm content types based on their name parameter. Everything within the include: key is essentially a mongodb query.

```
inherit:
  - name: rhel-7-server-openstack-5.0-rpms_unstable
    empty_include_result_fails: yes
    empty_exclude_result_fails: no
    include:
      'name':
        '$regex': '.*'`
```

## verify

Heighliner currently supports the 'serverspec' resource types testing.

### type: serverspec

The 'verify' action can be specified to perform the serverspec resource testing.  Any test required should be vendored into the `serverspec/` directory in the service repo.
```
serverspec/
├── properties.yml # specifies the various tests
├── Rakefile
└── spec           # test specs can be vendored in under this spec directory
    ├── base
    │   └── base_spec.rb
    ├── spec_helper.rb
    └── web
        └── web_spec.rb
```

## doc (planned)

### path

Path to docs folder
```
doc:
  path: doc
```

Default: `doc`
