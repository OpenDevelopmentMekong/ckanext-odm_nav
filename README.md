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

# Configuration

## Wordpress domain

Please set wordpress main domain
```
ckan.odm_nav_concept.wp_domain = opendevelopmentmekong.net
```

## Wordpress Menu Endpoints

In order to have the WP menu loaded into CKAN you need to provide the json api menu endpoints in the ckan config file.

```
ckan.odm_nav_concept.mekong_menu_endpoint = https://pp.opendevelopmentmekong.net/wp-json/menus/847
ckan.odm_nav_concept.cambodia_menu_endpoint = https://pp-cambodia.opendevelopmentmekong.net/wp-json/menus/43025
ckan.odm_nav_concept.thailand_menu_endpoint = https://pp-thailand.opendevelopmentmekong.net/wp-json/menus/10
ckan.odm_nav_concept.laos_menu_endpoint = https://pp-laos.opendevelopmentmekong.net/wp-json/menus/9
ckan.odm_nav_concept.vietnam_menu_endpoint = https://pp-vietnam.opendevelopmentmekong.net/wp-json/menus/572
ckan.odm_nav_concept.myanmar_menu_endpoint = https://pp-myanmar.opendevelopmentmekong.net/wp-json/menus/9
```

## Disable Top Topics Menu Links

If a certain WP country-sub-site does not have top topic content enabled, you should disable the links to the topic pages. By setting

```
ckan.odm_nav_concept.disable_top_topic_links_for_countries = laos myanmar vietnam thailand
```

The top topic links on ckan site for laos, myanmar, vietnam & thailand are set to the corresponding landing pages (COUNTRY at a glance).

When ```ckan.odm_nav_concept.disable_top_topic_links_for_countries```is not set, all top topic links are enabled by default!

# Testing

  Run ```nosetest```

# Copyright and License

This material is copyright (c) 2014-2015 East-West Management Institute, Inc. (EWMI).

It is open and licensed under the GNU Affero General Public License (AGPL) v3.0 whose full text may be found at:

http://www.fsf.org/licensing/licenses/agpl-3.0.html
