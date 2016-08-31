ckanext-odm_nav
=================

[![Build Status](https://travis-ci.org/OpenDevelopmentMekong/ckanext-odm_nav.svg?branch=master)](https://travis-ci.org/OpenDevelopmentMekong/ckanext-odm_nav)

A CKAN extension which provides with template files replacing CKAN's default UI and adding some javascript logic.

# Installation

In order to install this CKAN Extension:

  * clone the ckanext-odm_nav folder to the src/ folder in the target CKAN instance. NOTE: This repository contains some submodules, hence do not forget to include the --recursive flag for the git clone.

 ```
 git clone --recursive https://github.com/OpenDevelopmentMekong/ckanext-odm_nav.git
 cd ckanext-odm_nav
 ```

 * Install dependencies
 <code>pip install -r requirements.txt</code>

 * Setup plugin
 <code>python setup.py develop</code>

# Testing

Tests are found on ckanext/odm_dataset/tests and can be run with ```nosetest```

# Continuous deployment

Everytime code is pushed to the repository, travis will run the tests available on **/tests**. In case the code has been pushed to **master** branch and tests pass, the **_ci/deploy.sh** script will be called for deploying code in CKAN's DEV instance. Analog to this, and when code from **master** branch has been **tagged as release**, travis will deploy to CKAN's PROD instance automatically.

# Copyright and License

This material is copyright (c) 2014-2015 East-West Management Institute, Inc. (EWMI).

It is open and licensed under the GNU Affero General Public License (AGPL) v3.0 whose full text may be found at:

http://www.fsf.org/licensing/licenses/agpl-3.0.html
