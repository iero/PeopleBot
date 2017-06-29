#!/bin/bash

PATH="/home/iero/anaconda3/bin:$PATH"
export PATH

pushd /home/iero/scripts/PeopleBot > /dev/null
date
until python peoplebot.py $1 ; do
    echo "Server 'myserver' crashed with exit code $?.  Respawning.." >&2
        sleep 1
        done
popd > /dev/null
