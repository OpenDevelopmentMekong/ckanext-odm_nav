#!/usr/bin/env python
# -*- coding: utf-8 -*-

DEBUG = False

import pylons
import json
import ckan
import logging
import urlparse
import urllib
from ckan.common import request
import ckan.plugins.toolkit as toolkit
import os
import socket
from pprint import pprint
import string
import requests
import simplejson as json
import traceback

log = logging.getLogger(__name__)

taxonomy_dictionary = 'taxonomy'

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

  groups = toolkit.get_action('group_list')(
      data_dict={'sort': 'packages desc', 'all_fields': True})

  groups = groups[:10]

  return groups

def popular_datasets(limit):
  '''Return a sorted list of the most popular datasets.'''

  result_dict = toolkit.get_action('package_search')(
      data_dict={'sort': 'views_recent desc', 'rows': limit})

  return result_dict['results']

def get_all_laws_records():
	result = toolkit.get_action('package_search')(data_dict={'fq': '+type:laws_record','rows':1000})
	return map(lambda x:x["name"], result['results'])

def get_all_laws_records_and_agreements():
	result = toolkit.get_action('package_search')(data_dict={'fq': '+type:(laws_record OR agreement)','rows':1000})
	return map(lambda x:x["name"], result['results'])

def get_all_library_records():
	result = toolkit.get_action('package_search')(data_dict={'fq': '+type:library_record','rows':1000})
	return map(lambda x:x["name"], result['results'])

def get_all_agreements():
	result = toolkit.get_action('package_search')(data_dict={'fq': '+type:agreement','rows':1000})
	return map(lambda x:x["name"], result['results'])

def get_all_datasets():
	result = toolkit.get_action('package_search')(data_dict={'fq': '+type:dataset','rows':1000})
	return map(lambda x:x["name"], result['results'])

def get_all_laws_records_complete():
  result = toolkit.get_action('package_search')(data_dict={'fq': '+type:laws_record','rows':1000})
  return result['results']

def get_all_laws_records_and_agreements_complete():
  result = toolkit.get_action('package_search')(data_dict={'fq': '+type:(laws_record OR agreement)','rows':1000})
  return result['results']

def get_all_library_records_complete():
  result = toolkit.get_action('package_search')(data_dict={'fq': '+type:library_record','rows':1000})
  return result['results']

def get_all_agreements_complete():
  result = toolkit.get_action('package_search')(data_dict={'fq': '+type:agreement','rows':1000})
  return result['results']

def get_all_datasets_complete():
  result = toolkit.get_action('package_search')(data_dict={'fq': '+type:dataset','rows':1000})
  return result['results']

def tag_for_topic(topic):
  '''Return the name of the tag corresponding to a top topic'''

  if DEBUG:
    log.debug('tag_for_topic')

  tag_name = ''.join(ch for ch in topic if (ch.isalnum() or ch == '_' or ch == '-' or ch == ' ' ))
  return tag_name if len(tag_name)<=100 else tag_name[0:99]

def recent_datasets():
  '''Return a sorted list of the datasets updated recently.'''

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

def current_url_no_language():
  current_url = request.environ['CKAN_CURRENT_URL']
  current_lang_path = "/" + request.environ['CKAN_LANG']
  return urllib.unquote(current_url.replace(current_lang_path,''))

session = {}
