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
from pprint import pprint
log = logging.getLogger(__name__)



class OdmNavPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
  '''OD Mekong Nav plugin.'''

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

    return {
            'license_id': toolkit._('License'),
            'organization': toolkit._('Organizations'),
            'res_format': toolkit._('Formats'),
            'extras_odm_language': toolkit._('Language'),
            'extras_odm_spatial_range': toolkit._('Country')
            }

    # NOTE: Add support for tags -> 'tags': toolkit._('Topics'),

  def group_facets(self, facets_dict, group_type, package_type):

    return {
            'license_id': toolkit._('License'),
            'organization': toolkit._('Organizations'),
            'res_format': toolkit._('Formats'),
            'extras_odm_language': toolkit._('Language'),
            'extras_odm_spatial_range': toolkit._('Country')
            }

  def organization_facets(self, facets_dict, organization_type, package_type):

    return {
            'license_id': toolkit._('License'),
            'res_format': toolkit._('Formats'),
            'extras_odm_language': toolkit._('Language'),
            'extras_odm_spatial_range': toolkit._('Country')
            }

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
      'odm_nav_tag_for_topic': odm_nav_helper.tag_for_topic,
      'odm_nav_sanitize_html':odm_nav_helper.sanitize_html,
      'odm_nav_last_dataset': odm_nav_helper.last_dataset,
      'odm_nav_taxonomy_dictionary': odm_nav_helper.get_taxonomy_dictionary,
      'odm_nav_localize_resource_url': odm_nav_helper.localize_resource_url,
      'odm_nav_get_localized_tag': odm_nav_helper.get_localized_tag,
      'odm_nav_get_localized_tag_string': odm_nav_helper.get_localized_tag_string,
      'odm_nav_popular_datasets': odm_nav_helper.popular_datasets,
      'odm_nav_recent_datasets': odm_nav_helper.recent_datasets,
      'odm_nav_sanitize_html':odm_nav_helper.sanitize_html,
      'odm_nav_get_all_laws_records':odm_nav_helper.get_all_laws_records,
      'odm_nav_get_all_library_records':odm_nav_helper.get_all_library_records,
      'odm_nav_get_all_datasets':odm_nav_helper.get_all_datasets
	}

  # IPackageController
  def before_create(self, context, resource):
    log.info('before_create')

    odm_nav_helper.session['last_dataset'] = None
    odm_nav_helper.session.save()

  def after_create(self, context, pkg_dict):
    log.debug('after_create: %s', pkg_dict['name'])

    odm_nav_helper.session['last_dataset'] = pkg_dict
    odm_nav_helper.session.save()

  def after_update(self, context, pkg_dict):
    log.debug('after_update: %s', pkg_dict['name'])

    odm_nav_helper.session['last_dataset'] = pkg_dict
    odm_nav_helper.session.save()
