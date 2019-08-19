#!/bin/bash -e

## environment
cd /vagrant
source .envrc.travis


## apt packages
(
  echo "Installing dependencies"
  set -x

  export DEBIAN_FRONTEND=noninteractive
  sudo apt-get update -q
  sudo apt-get install -qy wget curl ca-certificates gnupg lsb-core
)


## postgresql 9.4
dpkg --list | grep -q postgresql-9.4 && echo "PostgreSQL 9.4 already installed" || (
  echo "Installing PostgreSQL 9.4"
  set -x

  export DEBIAN_FRONTEND=noninteractive
  curl -s https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
  sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'

  sudo apt-get update -q
  sudo apt-get install -qy postgresql-9.4

  sudo sed -Ei 's/^(host\s.*)md5/\1trust/' /etc/postgresql/9.4/main/pg_hba.conf
  sudo systemctl restart postgresql
)


## tusd
pidof tusd && echo "tusd already running" || (
  echo "Downloading tusd"
  set -x

  cd /tmp
  wget -q https://github.com/tus/tusd/releases/download/0.11.0/tusd_linux_amd64.tar.gz
  tar -xzvf tusd_linux_amd64.tar.gz

  # Start tusd server
  nohup tusd_linux_amd64/tusd -dir $TUSD_UPLOADS_DIR -hooks-http http://$BACKEND_HOST:$BACKEND_PORT/api/uploads/ &
)


## python packages
(
  echo "Installing dependencies"
  set -x

  sudo pip3 install -r requirements/tests.txt
)
