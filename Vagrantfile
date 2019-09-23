# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  if Vagrant.has_plugin?("vagrant-env")
    config.env.enable
  end

  config.vm.box = "base"

  config.nfs.functional = false
  config.smb.functional = false

  config.vm.provider :vmck do |vmck|
    vmck.image_path = "imgbuild-master.qcow2.tar.gz"
    vmck.vmck_url = ENV["VMCK_URL"]
    vmck.memory = 8000
    vmck.cpus = 2
    vmck.name = ENV["VMCK_NAME"] || "ozone"
  end

  config.vm.provision :shell, privileged: false, path: "utility/vagrant_provision.sh"

end
