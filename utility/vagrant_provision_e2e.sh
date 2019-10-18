#!/bin/bash -e

cd /vagrant
source .envrc.vagrant
export DEBIAN_FRONTEND=noninteractive

(
  echo "Installing webdriver and vnc for e2e tests"
  set -x

  sudo apt-get install -qqy default-jdk chromium-browser vnc4server xfce4
  sudo npm install --quiet --global webdriver-manager
  sudo webdriver-manager update

  sudo mkdir -p /etc/vnc
  sudo bash -c "echo 'x-window-manager &; x-session-manager &' > /etc/vnc/xstartup"
  sudo chmod +x /etc/vnc/xstartup
)

echo "✔ E2E provisioning successful!"
