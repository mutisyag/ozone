#!/usr/bin/env bash

set -e

setup_git() {
  git config --global user.email "travis@travis-ci.org"
  git config --global user.name "Travis CI"
}

commit_translations() {
  git add . *.po
  git diff-index --quiet HEAD || git commit --message "Travis build: $TRAVIS_BUILD_NUMBER"
}

upload_files() {
  git remote add origin-translations https://${GH_TOKEN}@github.com/eaudeweb/ozone-translations.git > /dev/null 2>&1
  git push --quiet --set-upstream origin-translations
}

setup_git
commit_translations
upload_files