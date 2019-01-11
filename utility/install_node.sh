#!/usr/bin/env bash

set -ex
# Used by travis-CI to install node.
# XXX Remove this when Travis fixes their issues.
# See https://travis-ci.community/t/then-sudo-apt-get-update-failed-public-key-is-not-available-no-pubkey-6b05f25d762e3157-in-ubuntu-xenial/1728?u=alexkiro
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 6B05F25D762E3157
# Install nvm
sudo apt update --allow-unauthenticated
sudo apt install -y wget tar
wget -qO- https://raw.githubusercontent.com/creationix/nvm/v0.33.0/install.sh | bash
source ~/.bashrc
# Install node
nvm install node
node --version
npm --version
# Install yarn
npm install --global yarn