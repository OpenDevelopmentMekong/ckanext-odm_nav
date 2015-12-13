
#!/usr/bin/env python
# -*- coding: utf-8 -*-

DEBUG = True

import pylons
import json
import ckan
import logging
import urlparse
import ckan.plugins.toolkit as toolkit
import os
import socket
print(socket.gethostname())

log = logging.getLogger(__name__)
jsonPath=os.path.abspath(os.path.join(__file__, '../../','odm-taxonomy/top_topics/top_topics_multilingual.json'))
# jsonPath=os.path.join(os.path.basename(__file__), "odm-taxonomy/"))

def json_load_top_topics():
    with open(jsonPath) as data_file:
       return json.load(data_file)


def recent_datasets():
  '''Return a sorted list of the datasets updated recently.'''

  # Get a list of all the site's groups from CKAN, sorted by number of
  # datasets.
  dataset = toolkit.get_action('current_package_list_with_resources')(
      data_dict={'limit': 10})

  return dataset

def last_dataset():
  ''' Returns the last dataset info stored in session'''
  if 'last_dataset' in odm_nav_helper.session:
    return odm_nav_helper.session['last_dataset']

  return None

def sanitize_html(string):
  string = ''.join(ch for ch in string if (ch.isalnum() or ch == '_' or ch == '-' or ch == ' '))
  string = string.replace(' ','-').lower()
  return string
