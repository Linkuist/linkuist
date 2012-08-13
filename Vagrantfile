Vagrant::Config.run do |config|
  # vm
  config.vm.box = 'collectr-precise64'
  config.vm.box_url = 'http://files.vagrantup.com/precise64.box'
  config.vm.forward_port 80, 8000
  config.vm.share_folder('v-root', '/home/vagrant/project', '.')
  config.vm.network :hostonly, '33.33.33.10'
  # ssh
  config.ssh.max_tries = 50
  config.ssh.timeout = 300
end
