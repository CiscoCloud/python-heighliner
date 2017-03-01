# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANTFILE_API_VERSION = "2"
PRIV_KEY = File.read(File.expand_path('~/.ssh/id_rsa'))

project_name = 'heighliner'

$init = <<SCRIPT
export PATH=$PATH:/usr/local/bin

mkdir -p ~/.ssh
chmod 0700 ~/.ssh
cat << EOF > ~/.ssh/config
Host cis-gerrit.cisco.com
User #{ENV['USER']}
Hostname cis-gerrit.cisco.com
EOF

echo "#{PRIV_KEY}" > ~/.ssh/id_rsa
chmod 0600 ~/.ssh/id_rsa

sudo sed -i '/secure_path/d' /etc/sudoers
sudo echo 'Defaults    secure_path = /sbin:/bin:/usr/sbin:/usr/bin:/usr/local/bin' >> /etc/sudoers

yum makecache fast
yum -y install rpm-build gcc ruby-devel git
gem install fpm

cd /usr/src/heighliner
python setup.py develop

cat << EOF > /etc/ansible/hosts
[build-server]
localhost ansible_connection=local environment_name=dev site_repo=vagrant-dev
[heighliner]
localhost ansible_connection=local environment_name=dev site_repo=vagrant-dev
EOF

mkdir -p /opt/ccs/services
cp -a /usr/src/heighliner /opt/ccs/services/heighliner
mkdir -p /opt/ccs/services/heighliner/{ansible,tests,foo,bar}
cat << NIMBUS >> /opt/ccs/services/heighliner/.nimbus.yml
verify:
  type: testinfra
  additional_test_dirs: ['foo', 'bar']
NIMBUS
cat << TESTINFRA >> /opt/ccs/services/heighliner/tests/test_passwd.py
def test_passwd_file(File):
    passwd = File("/etc/passwd")
    assert passwd.contains("root")
    assert passwd.user == "root"
    assert passwd.group == "root"
    assert passwd.mode == 0o644
TESTINFRA

for d in foo bar ansible;do
  cp /opt/ccs/services/heighliner/tests/test_passwd.py /opt/ccs/services/heighliner/${d}/test_${d}.py
done
SCRIPT

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

  config.ssh.insert_key = false
  config.ssh.private_key_path = [
    "~/.ssh/id_rsa",
    "~/.vagrant.d/insecure_private_key"
  ]

  config.vm.box = "http://cis-kickstart.cisco.com/ccs-rhel-7.box"
  config.vm.hostname = 'heighliner'
  config.vm.synced_folder ".", "/usr/src/#{project_name}"
  config.vm.network "forwarded_port", guest: 80, host: 8080

  config.vm.provision "shell", inline: $init
end
