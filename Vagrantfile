# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant::Config.run do |config|
  config.vm.box = "DebianSqueeze64"
  config.vm.box_url = "http://dl.dropbox.com/u/937870/VMs/squeeze64.box"
  config.vm.provision :shell, :path => "append_authorized_keys_to_root.sh"

  config.vm.host_name = "beta.montigny-tt.info"
  config.hosts.name = "beta.montigny-tt.info"

  config.vm.network :hostonly, "192.168.33.10", :mac => "080027e5f699"

  config.vm.share_folder "src", "/home/vagrant/projects/", "."
end
