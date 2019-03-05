#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import ckan
import urlparse

import os
import requests

from ckan.common import config
import ckan.lib.helpers as h
import ckan.logic as logic
from ckan.plugins.toolkit import request
import ckan.plugins.toolkit as toolkit

from . import menus

import logging
log = logging.getLogger(__name__)

taxonomy_dictionary = 'taxonomy'

# memoization decorator from http://code.activestate.com/recipes/578231-probably-the-fastest-memoization-decorator-in-the-/
# mit license
def memoize(f):
    class memoize(dict):
        def __missing__(self, key):
            ret = self[key] = f(key)
            return ret
    return memoize().__getitem__

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

@memoize
def get_localized_tag(tag):
  '''Looks for a term translation for the specified tag. Returns the tag untranslated if no term found'''

  log.debug('odm_nav_get_localized_tag: %s', tag)
  desired_lang_code = request.environ['CKAN_LANG']

  translations = ckan.logic.action.get.term_translation_show(
          {'model': ckan.model},
          {'terms': (tag)})

  for translation in translations:
    if translation['lang_code'] == desired_lang_code:
      return translation['term_translation']

  return tag

@memoize
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

  log.debug('tag_for_topic')

  tag_name = ''.join(ch for ch in topic if (ch.isalnum() or ch == '_' or ch == '-' or ch == ' ' ))
  return tag_name if len(tag_name)<=100 else tag_name[0:99]

def recent_datasets():
  '''Return a sorted list of the datasets updated recently.'''

  dataset = toolkit.get_action('current_package_list_with_resources')(
      data_dict={'limit': 10})

  return dataset


def sanitize_html(s):
  s = ''.join(ch for ch in s if (ch.isalnum() or ch == '_' or ch == '-' or ch == ' '))
  s = s.replace(' ','-').lower()
  return s


#Helpers for data preview_resource


def predict_if_resource_will_preview(resource_dict):
    format = resource_dict.get('format')

    if not format:
        return False

    normalised_format = format.lower().split('/')[-1]
    accepted_formats = (('csv', 'xls', 'rdf+xml', 'owl+xml', 'xlsx',
                                  'xml', 'n-triples', 'turtle', 'plain',
                                  'txt', 'atom', 'tsv', 'rss',
                                  'geojson', 'kml', 'json-stat',
                                  'doc', 'docx', 'pdf',
                                  'jpeg', 'jpg', 'png', 'gif','wms', 'json'))
    # Check format is TSV or CSV but url doesn't end in that extension
    if normalised_format in ('csv', 'tsv'):
        # Get url file extension
        url = resource_dict.get('url')
        tmp = url.split('/')
        tmp = tmp[len(tmp) - 1]
        tmp = tmp.split('?')
        tmp = tmp[0]
        ext = tmp.split('.')

        file_extension = None
        if len(ext) > 1: #Because a filename with /only/ an extension doesn't make much sense
            file_extension = ext[-1]
        if file_extension:
            return file_extension in ('csv', 'tsv')
        else:
            #Get the downloaded file extension from the server (workaround for CKAN /dump URLs)
            #Inspired by CKAN resourceproxy code but much simpler here
            try:
                r = requests.head(url)
                cd = r.headers.get('Content-Disposition', '')
                filename = cd.split('filename')[1].split('"')[1]
            except:
                return False

            ext = filename.split('.')
            file_extension = None
            if len(ext) > 0:
                file_extension = ext[-1]

            if file_extension:
                return file_extension in ('csv', 'tsv')
            else:
                return False

    else:
        return normalised_format in accepted_formats

def resource_to_preview_on_dataset_page(resources):
    possible_resources = {}
    for resource in resources:
        if not resource.get('format', None):
            continue
        normalised_format = resource.get('format').lower().split('/')[-1]
        if (predict_if_resource_will_preview(resource)):
            if (not possible_resources.get(normalised_format)):
                possible_resources[normalised_format] = []
            possible_resources[normalised_format].append(resource)

    preview_priority = [
        # if there are image resource, we want to show them first as they are fast to load
        'jpeg', 'jpg', 'png', 'gif',
        # if we have a kml resource we want to show that next
        'kml',
        # if we don't have kml, try geojson
        'geojson', 'wms',
        # no geojson, maybe json-stat?
        'json-stat',
        # welp, now it's tables I guess
        'csv', 'tsv', 'xls', 'xlsx',
        # and json
        'json',
        # no table? probably a pdf :(
        'pdf',
        # maybe a doc or ppt?
        'doc',
        'docx',
        'ppt',
        'pptx'
        # not that? no need to preview
    ]
    view_types_priority = [
        'geo_view',
        'jsonstat_view',
        'text_view'
    ]
    for possible_format in preview_priority:
        if (possible_resources.get(possible_format) and len(possible_resources.get(possible_format))):
            context ={}
            resource_views = toolkit.get_action('resource_view_list')(
                context, {'id': possible_resources.get(possible_format)[0]['id']})
            for vtype in view_types_priority:
                for rv in resource_views:
                    if vtype == rv['view_type']:
                        rv['resource_name'] = possible_resources.get(possible_format)[0]['name']
                        rv['resource_url'] = possible_resources.get(possible_format)[0]['url']
                        return rv
                    rv['resource_name'] = possible_resources.get(possible_format)[0]['name']
                    rv['resource_url'] = possible_resources.get(possible_format)[0]['url']
                    return rv
            # return possible_resources.get(possible_format)[0]
    return None

def active_search_link():

    # List of path to identify as current active path
    path_list = ['/agreement', '/library_record', '/dataset', '/laws_record']
    active_path = {}

    for path in path_list:

        if path == h.current_url():

            active_path[path.replace("/", '')] = True
        else:

            active_path[path.replace("/", '')] = False

    return active_path

def gen_odm_menu(list_element, first_pass=True):
    items = []

    if len(list_element) == 0:
        return ""
    else:
        if first_pass:
            items.append('<ul class="nav navbar-nav">')
            first_pass=False
        else:
            items.append('<ul class="dropdown-menu">')

        for element in list_element:
            items.append('<li>')

            if len(element['child_menus']) != 0:
                items.append('<a href="' + element['url'].replace('/', '') + '" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">' + element['title'] + '<span class="caret"></span></a>')
            else:
                items.append('<a href="' + element['url'].replace('/', '') + '" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">' + element['title'] + '</a>')

            items.append(nav_html_parsing(element['child_menus'], first_pass))
            items.append('</li>')
        items.append('</ul>')

        return "".join(items)

def ckan_url_for_site(sitecode):
    return config.get("ckanext.odm.%s_url" % sitecode, "")

def wp_url_for_site(sitecode):
    return config.get("ckanext.odm.%s_wp_url" % sitecode, "")

def country_name_for_site(site=None):
    if not site:
        site = config.get('ckanext.odm.site_code')
    names = {'odm': 'Mekong',
             'odmy': 'Myanmar',
             'odt': 'Thailand',
             'odl': 'Laos',
             'odc': 'Cambodia',
             'odv': 'Vietnam'}
    return names.get(site,'')

def odm_nav_menu(site=None):
    if not site:
        site = config.get('ckanext.odm.site_code')
    if not site in menus.rendered:
        base_path = os.path.join(os.path.dirname(__file__), 'public')
        filename = '%s_nav_items.json' % site
        with open(os.path.join(base_path, filename), 'r') as f:
            menu_items = json.load(f)
            
        menus.rendered[site] = gen_odm_menu(menu_items)
        
    return menus.rendered[site]
