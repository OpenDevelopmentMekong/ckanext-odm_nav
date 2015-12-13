'''plugin.py

'''
import ckan
import pylons
import logging
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckan.lib.helpers as h
from pylons import config
from beaker.middleware import SessionMiddleware
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))
import odm_nav_helper
import datetime
import time
from urlparse import urlparse
import json
import collections
from genshi.template.text import NewTextTemplate
from ckan.lib.base import render

log = logging.getLogger(__name__)

print (sys.version)
from pprint import pprint

jsonPath=os.path.join(os.path.dirname(__file__), "lib/top_topics_multilingual.json")


# tmp build menu

with open(jsonPath) as data_file:
   data = json.load(data_file)

strs ={}
strs['children']={}
# strs['titles']= dict([ (top_topic["titles"]["en"],top_topic["titles"]["th"]) for top_topic in data ])
# titles = dict([ (top_topic["titles"]["en"],top_topic["titles"]["th"]) for top_topic in data ])
i=0
for top_topic in data:
#     # print titles
#     strs.append(top_topic["titles"]["en"])
#     strs[top_topic["titles"]["en"]]=

    strs['titles']={i,top_topic["titles"]["en"]}
    # for child in top_topic['children']:
    i+=1
#         # print names
#         print(child['name'])
#         # strs['children'].update({'d': child['name']})
#

# for top_topic in data:
#     # print titles
#     strs.append(top_topic["titles"]["en"])
print("xyz")

pprint(strs)

#




def last_dataset():
  ''' Returns the last dataset info stored in session'''
  if 'last_dataset' in odm_nav_helper.session:
    return odm_nav_helper.session['last_dataset']

  return None

def localize_resource_url(url):
  '''Converts a absolute URL in a relative, chopping out the domain'''

  parsed = urlparse(url)
  str_index = url.index(parsed.netloc)
  str_length = len(parsed.netloc)

  localized = url[str_index+str_length:]

  return localized

def get_tag_dictionaries(vocab_id):
  '''Returns the tag dictionary for the specified vocab_id'''

  try:

    tag_dictionaries = toolkit.get_action('tag_list')(data_dict={'vocabulary_id': vocab_id})
    return tag_dictionaries

  except toolkit.ObjectNotFound:

    return []

def get_taxonomy_dictionary():
  '''Returns the tag dictionary for the taxonomy'''

  return get_tag_dictionaries(odm_nav_helper.taxonomy_dictionary)



def get_localized_tag(tag):
  '''Looks for a term translation for the specified tag. Returns the tag untranslated if no term found'''

  log.debug('odm_theme_get_localized_tag: %s', tag)

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

def recent_datasets():
  '''Return a sorted list of the datasets updated recently.'''

  # Get a list of all the site's groups from CKAN, sorted by number of
  # datasets.
  dataset = toolkit.get_action('current_package_list_with_resources')(
      data_dict={'limit': 10})

  return dataset

def popular_datasets(limit):
  '''Return a sorted list of the most popular datasets.'''

  # Get a list of all the site's groups from CKAN, sorted by number of
  # datasets.
  result_dict = toolkit.get_action('package_search')(
      data_dict={'sort': 'views_recent desc', 'rows': limit})

  return result_dict['results']

def get_orga_or_group(orga_id,group_id):
  '''Returns orga or group'''

  if orga_id is not None:
    return orga_id
  elif group_id is not None:
    return group_id

  return None

class OdmNavPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
  '''OD Mekong theme plugin.'''

  plugins.implements(plugins.IConfigurer)
  plugins.implements(plugins.ITemplateHelpers)
  plugins.implements(plugins.IRoutes, inherit=True)
  plugins.implements(plugins.IFacets)
  plugins.implements(plugins.IPackageController, inherit=True)

  def __init__(self, *args, **kwargs):

    log.debug('OdmNavPlugin init')
    wsgi_app = SessionMiddleware(None, None)
    odm_nav_helper.session = wsgi_app.session

  # IFacets

  def dataset_facets(self, facets_dict, package_type):

      facets_dict = {
                'license_id': toolkit._('License'),
                'tags': toolkit._('Topics'),
                'organization': toolkit._('Organizations'),
                'groups': toolkit._('Groups'),
                'res_format': toolkit._('Formats'),
                'odm_language': toolkit._('Language'),
                'odm_spatial_range': toolkit._('Country')
                }

      return facets_dict

  def group_facets(self, facets_dict, group_type, package_type):

      group_facets = {
                'license_id': toolkit._('License'),
                'tags': toolkit._('Topics'),
                'organization': toolkit._('Organizations'),
                'res_format': toolkit._('Formats'),
                'odm_language': toolkit._('Language'),
                'odm_spatial_range': toolkit._('Country')
                }

      return group_facets

  def organization_facets(self, facets_dict, organization_type, package_type):

      organization_facets = {
                'license_id': toolkit._('License'),
                'tags': toolkit._('Topics'),
                'groups': toolkit._('Groups'),
                'res_format': toolkit._('Formats'),
                'odm_language': toolkit._('Language'),
                'odm_spatial_range': toolkit._('Country')
                }

      return organization_facets

  # IRoutes

  def before_map(self, m):

    #m.connect('dataset_read', '/dataset/{id}',controller='package', action='read', ckan_icon='table')

    return m

  # IConfigurer

  def update_config(self, config):
    '''Update plugin config'''

    toolkit.add_template_directory(config, 'templates')
    toolkit.add_resource('fanstatic', 'odm_nav')
    toolkit.add_public_directory(config, 'public')

  # IConfigurer

  def get_helpers(self):
    '''Register the plugin's functions above as a template helper function.'''

    return {
      'odm_nav_last_dataset': last_dataset,
      'odm_nav_build_top_topic_nav_menu':build_top_topic_nav_menu
    }

  # IDatasetForm

  def _modify_package_schema_write(self, schema):

    for metadata_field in odm_nav_helper.metadata_fields:
      validators_and_converters = [toolkit.get_validator('ignore_missing'),toolkit.get_converter('convert_to_extras'), ]
      if metadata_field[2]:
        validators_and_converters.insert(1,validate_not_empty)
      schema.update({metadata_field[0]: validators_and_converters})

    for odc_field in odm_nav_helper.odc_fields:
      validators_and_converters = [toolkit.get_validator('ignore_missing'),toolkit.get_converter('convert_to_extras'), ]
      if odc_field[2]:
        validators_and_converters.insert(1,validate_not_empty)
      schema.update({odc_field[0]: validators_and_converters})

    for ckan_field in odm_nav_helper.ckan_fields:
      validators_and_converters = [toolkit.get_validator('ignore_missing'),toolkit.get_converter('convert_to_extras'), ]
      if ckan_field[2]:
        validators_and_converters.insert(1,validate_not_empty)
      schema.update({ckan_field[0]: validators_and_converters})

    for internal_field in odm_nav_helper.internal_fields:
      validators_and_converters = [toolkit.get_validator('ignore_missing'),toolkit.get_converter('convert_to_extras'), ]
      if internal_field[2]:
        validators_and_converters.insert(1,validate_not_empty)
      schema.update({internal_field[0]: validators_and_converters})

    schema.update({odm_nav_helper.taxonomy_dictionary: [toolkit.get_validator('ignore_missing'),toolkit.get_converter('convert_to_tags')(odm_nav_helper.taxonomy_dictionary)]})

    return schema

  def _modify_package_schema_read(self, schema):

    for metadata_field in odm_nav_helper.metadata_fields:
      validators_and_converters = [toolkit.get_converter('convert_from_extras'),toolkit.get_validator('ignore_missing')]
      if metadata_field[2]:
        validators_and_converters.append(validate_not_empty)
      schema.update({metadata_field[0]: validators_and_converters})

    for odc_field in odm_nav_helper.odc_fields:
      validators_and_converters = [toolkit.get_converter('convert_from_extras'),toolkit.get_validator('ignore_missing')]
      if odc_field[2]:
        validators_and_converters.append(validate_not_empty)
      schema.update({odc_field[0]: validators_and_converters})

    for ckan_field in odm_nav_helper.ckan_fields:
      validators_and_converters = [toolkit.get_converter('convert_from_extras'),toolkit.get_validator('ignore_missing')]
      if ckan_field[2]:
        validators_and_converters.append(validate_not_empty)
      schema.update({ckan_field[0]: validators_and_converters})

    for internal_field in odm_nav_helper.internal_fields:
      validators_and_converters = [toolkit.get_converter('convert_from_extras'),toolkit.get_validator('ignore_missing')]
      if internal_field[2]:
        validators_and_converters.append(validate_not_empty)
      schema.update({internal_field[0]: validators_and_converters})

    schema.update({odm_nav_helper.taxonomy_dictionary: [toolkit.get_converter('convert_from_tags')(odm_nav_helper.taxonomy_dictionary),toolkit.get_validator('ignore_missing')]})

    return schema

  def create_package_schema(self):
    schema = super(OdmThemePlugin, self).create_package_schema()
    schema = self._modify_package_schema_write(schema)
    return schema

  def update_package_schema(self):
    schema = super(OdmThemePlugin, self).update_package_schema()
    schema = self._modify_package_schema_write(schema)
    return schema

  def show_package_schema(self):
    schema = super(OdmThemePlugin, self).show_package_schema()
    schema = self._modify_package_schema_read(schema)
    return schema

  def is_fallback(self):
    return True

  def package_types(self):
    return []

  # IPackageController

  def before_create(self, context, resource):
    log.info('before_create')

    odm_nav_helper.session['last_dataset'] = None
    odm_nav_helper.session.save()

  def after_create(self, context, pkg_dict):
    log.debug('after_create: %s', pkg_dict['name'])

    odm_nav_helper.session['last_dataset'] = pkg_dict
    odm_nav_helper.session.save()

    # Create default Issue
    review_system = h.asbool(config.get("ckanext.issues.review_system", False))
    if review_system:
      if pkg_dict['type'] == 'library_record':
        create_default_issue_library_record(pkg_dict)
    # add support for laws datatype
      elif pkg_dict['type'] == 'laws_record':
        log.info('Creating issue for laws record')
        create_default_issue_laws_record(pkg_dict)
      else:
        create_default_issue_dataset(pkg_dict)

  def after_update(self, context, pkg_dict):
    log.debug('after_update: %s', pkg_dict['name'])

    odm_nav_helper.session['last_dataset'] = pkg_dict
    odm_nav_helper.session.save()

def build_top_topic_nav_menu(lang):
    ####################
    # Json menu logic
    ###################
    # read json file
    #

    with open(jsonPath) as data_file:
       data = json.load(data_file)

    strs=[]

    for top_topic in data:
        # print titles
        strs.append(top_topic["titles"][lang])

    return strs
    #
    # for top_topic in data:
    #     # print titles
    #     print(top_topic["titles"]["en"])
    #     for child in top_topic['children']:
    #         # print names
    #         print(child['name'])
    # return literal('<div><h1>test</h1></div>')
    # return literal('<li>')
