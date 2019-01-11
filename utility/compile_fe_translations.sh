#!/usr/bin/env bash

set -evx

if ! [ -d $APP_HOME/translations ]
then
    exit 0
fi

cd $APP_HOME/frontend
make translations
