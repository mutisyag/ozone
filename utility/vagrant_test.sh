#!/bin/bash -e

## environment
cd /vagrant
source .envrc.vagrant


## run tests
(
  echo "Running backend tests"
  set -x

  export LC_CTYPE=en_US.UTF8
  python3 manage.py test "$@"
)
