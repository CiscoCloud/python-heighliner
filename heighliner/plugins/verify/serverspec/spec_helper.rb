# WARNING:  Do not modify this file because it will be replaced by heighliner
require 'serverspec'
require 'net/ssh'

set :backend, :ssh

host = ENV['TARGET_HOST']

options = Net::SSH::Config.for(host)

options[:user] ||= Etc.getpwuid(Process.uid).name
options[:paranoid] = false

set :host,        options[:host_name] || host
set :ssh_options, options
