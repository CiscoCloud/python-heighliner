Heighliner
==========

Heighliner is a tool for parsing and executing actions specified in .nimbus.yml file.

# Changelog

Current version: 0.6.0

## 0.6.0

 * Add promote action
 * Add provision action
 * Add repo action
 * Add reposync action
 * Update deploy action

## 0.5.1

 * US12487 - Serverspec for service validation
 * TA16696 - Implement 'verify' action

## 0.5.0

 * US8762 - Multi-service deployments (linear)
 * Support ansible-playbook runs with vaultpass in non-dev environments

## 0.4.3

 * DE1979 Setting default repo type to 'project' when not specified

## 0.4.1

 * Fixed issue with heighliner not passing failed exit codes from check scripts

## 0.4.0

 * US10750 - RPMs get published to yum repo after creation
 * Plugins now reside in heighliner repo to simplify bootstrap and deployment

## 0.3.1

 * Added separate packaging step with dynamic versioning
 * Added git submodule support in service/project repos

## 0.2.4 - US10526

 * TA10645 - Heighliner accepts a path to a nimbusfile, defaulting to '.nimbus.yml' in the local directory
 * TA10686 - Heighliner can be run without a nimbusfile to read config from.  Plugins will use their default logic.

## 0.1.0 - US8746

 * TA10044 - Plugin architecture for processing actions
 * TA10039 - Implement 'check' action
 * TA10041 - Implement 'build' action

# Roadmap

# Requirements

 * As a developer, I want to specify a script that will be executed after I post a commit for review in gerrit
