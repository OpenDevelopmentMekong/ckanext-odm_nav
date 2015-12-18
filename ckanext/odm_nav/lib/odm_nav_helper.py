
#!/usr/bin/env python
# -*- coding: utf-8 -*-

DEBUG = False

import pylons
import json
import ckan
import logging
import urlparse
import ckan.plugins.toolkit as toolkit
import os
import socket
import Cookie
from pprint import pprint
import string
import requests
import simplejson as json



## DEV

# cookie = Cookie.SimpleCookie()
# cookie_string = os.environ.get('HTTP_COOKIE')
# cookie.load(cookie_string)
# # Use the value attribute of the cookie to get it
# data = cookie['odm_transition_data'].value
# pprint(data)




##
log = logging.getLogger(__name__)

taxonomy_dictionary = 'taxonomy'
jsonPath = os.path.abspath(os.path.join(__file__, '../../','odm-taxonomy/top_topics/top_topics_multilingual.json'))

def load_country_specific_menu(country, wpUrl):
  log.info('getting menu for %s',country)

  # list of menu endpoints
  if country=='':
    menu_endpoint= 'pp.' + wpUrl + '/wp-json/menus/824'
  elif country=='cambodia':
    menu_endpoint= 'pp-cambodia.'+ wpUrl + '/wp-json/menus/2'
  else:
    log.debug("Cannot get WP menu")
    return ''
  # get json representation of menu
  try:
    r = requests.get(menu_endpoint)
    jsonData = r.json()
    return jsonData['items']
  except(requests.exceptions.ConnectionError):
    print("cannot connect to Wordpress Instance on " +wpUrl)
    return []


def get_cookie():
  request=toolkit.request
  try:
    cookie=request.cookies['odm_transition_country']
    # cookie=json.loads(request.cookies['odm_transition_data'])
    return cookie
  except (Cookie.CookieError, KeyError):
    return ''

def localize_resource_url(url):
  '''Converts a absolute URL in a relative, chopping out the domain'''

  try:
    parsed = urlparse(url)
    str_index = url.index(parsed.netloc)
    str_length = len(parsed.netloc)
    localized = url[str_index+str_length:]
    return localized

  except:
    return url


def get_tag_dictionaries(vocab_id):
  '''Returns the tag dictionary for the specified vocab_id'''

  try:

    tag_dictionaries = toolkit.get_action('tag_list')(data_dict={'vocabulary_id': vocab_id})
    return tag_dictionaries

  except toolkit.ObjectNotFound:

    return []

def get_taxonomy_dictionary():
  '''Returns the tag dictionary for the taxonomy'''

  return get_tag_dictionaries(taxonomy_dictionary)

def get_localized_tag(tag):
  '''Looks for a term translation for the specified tag. Returns the tag untranslated if no term found'''

  log.debug('odm_nav_get_localized_tag: %s', tag)

  desired_lang_code = pylons.request.environ['CKAN_LANG']

  translations = ckan.logic.action.get.term_translation_show(
          {'model': ckan.model},
          {'terms': (tag)})

  # Transform the translations into a more convenient structure.
  for translation in translations:
    if translation['lang_code'] == desired_lang_code:
      return translation['term_translation']

  return tag

def get_localized_tag_string(tags_string):
  '''Returns a comma separated string with the translation of the tags specified. Calls get_localized_tag'''

  log.debug('get_localized_tag_string: %s', tags_string)

  translated_array = []
  for tag in tags_string.split(', '):
    translated_array.append(get_localized_tag(tag))

  if len(translated_array)==0:
    return ''

  return ','.join(translated_array)

def tag_for_topic(topic):
  '''Return the name of the tag corresponding to a top topic'''

  log.debug('tag_for_topic')

  tag_name = ''.join(ch for ch in topic if (ch.isalnum() or ch == '_' or ch == '-' or ch == ' ' ))
  return tag_name if len(tag_name)<=100 else tag_name[0:99]

def popular_groups():
  '''Return a sorted list of the groups with the most datasets.'''

  # Get a list of all the site's groups from CKAN, sorted by number of
  # datasets.
  groups = toolkit.get_action('group_list')(
      data_dict={'sort': 'packages desc', 'all_fields': True})

  # Truncate the list to the 10 most popular groups only.
  groups = groups[:10]

  return groups

def popular_datasets(limit):
  '''Return a sorted list of the most popular datasets.'''

  # Get a list of all the site's groups from CKAN, sorted by number of
  # datasets.
  result_dict = toolkit.get_action('package_search')(
      data_dict={'sort': 'views_recent desc', 'rows': limit})

  return result_dict['results']

def json_load_top_topics():
    with open(jsonPath) as data_file:
       return json.load(data_file)

def tag_for_topic(topic):
  '''Return the name of the tag corresponding to a top topic'''

  if DEBUG:
    log.debug('tag_for_topic')

  tag_name = ''.join(ch for ch in topic if (ch.isalnum() or ch == '_' or ch == '-' or ch == ' ' ))
  return tag_name if len(tag_name)<=100 else tag_name[0:99]

def recent_datasets():
  '''Return a sorted list of the datasets updated recently.'''

  # Get a list of all the site's groups from CKAN, sorted by number of
  # datasets.
  dataset = toolkit.get_action('current_package_list_with_resources')(
      data_dict={'limit': 10})

  return dataset

def last_dataset():
  ''' Returns the last dataset info stored in session'''
  if 'last_dataset' in session:
    return session['last_dataset']

  return None

def sanitize_html(string):
  string = ''.join(ch for ch in string if (ch.isalnum() or ch == '_' or ch == '-' or ch == ' '))
  string = string.replace(' ','-').lower()
  return string

session = {}
