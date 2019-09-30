#!/bin/bash -e

## environment
cd /vagrant
source .envrc.vagrant
export DEBIAN_FRONTEND=noninteractive


(
  echo "Installing apt packages"
  set -x

  sudo apt-get update -qq
  sudo apt-get install -qqy \
    wget curl ca-certificates gnupg lsb-core snapd \
    python3-pip build-essential git

  sudo update-locale LANG=en_US.UTF-8
)

export PATH=$PATH:/snap/bin


dpkg --list | grep -q postgresql-9.4 && echo "PostgreSQL 9.4 already installed" || (
  echo "Installing PostgreSQL 9.4"
  set -x

  curl -s https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
  sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'

  sudo apt-get update -qq
  sudo apt-get install -qqy postgresql-9.4

  sudo sed -Ei 's/^(host\s.*)md5/\1trust/' /etc/postgresql/9.4/main/pg_hba.conf
  sudo systemctl restart postgresql
  sudo -u postgres createuser -s vagrant
  createdb ozone
)


node --version | grep -q 'v8\.' && echo "Nodejs 8 already installed" || (
  echo "Installing Nodejs v8.x"
  set -x

  sudo snap install node --classic --channel=8
)


pidof tusd && echo "tusd already running" || (
  echo "Downloading and running tusd"
  set -x

  mkdir /tmp/tusd-dist
  cd /tmp/tusd-dist
  curl -sLO https://github.com/tus/tusd/releases/download/0.11.0/tusd_linux_amd64.tar.gz
  tar -xzvf tusd_linux_amd64.tar.gz

  # Start tusd server
  nohup tusd_linux_amd64/tusd -dir $TUSD_UPLOADS_DIR -hooks-http http://$BACKEND_HOST:$BACKEND_PORT/api/uploads/ &
)


(
  echo "Installing Python dependencies and preparing database"
  set -x

  sudo pip3 install -q -r requirements/tests.txt

  python3 manage.py migrate
  python3 manage.py load_initial_fixtures

  cd utility
  ./setup_backend.sh
)


(
  echo "Building the frontend"
  set -x

  cd frontend
  /snap/bin/npm install --quiet
  /snap/bin/npm run build
)

echo "✔ Provisioning successful!"
