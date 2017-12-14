#!/usr/bin/env bash

set -e;
cd /tmp/odm-automation-master

echo "$(tput setaf 136)"
echo "             Starting Deployment "
echo "============================================="
echo "$(tput sgr0)" # reset

if [ $TRAVIS_TAG ]; then

    echo "$(tput setaf 136)"
    echo "             deploying to prod "
    echo "---------------------------------------------"
    echo "$(tput sgr0)" # reset

    export ANSIBLE_HOST_KEY_CHECKING=False
    time ./deploy.sh ckan prod ckanext-odm_nav

else

    echo "$(tput setaf 136)"
    echo "             deploying to dev "
    echo "---------------------------------------------"
    echo "$(tput sgr0)" # reset

    export ANSIBLE_HOST_KEY_CHECKING=False
    time ./deploy.sh ckan dev ckanext-odm_nav

fi

echo "$(tput setaf 64)" # green
echo "---------------------------------------------"
echo "             ✓ done deployment"
echo "$(tput sgr0)" # reset
