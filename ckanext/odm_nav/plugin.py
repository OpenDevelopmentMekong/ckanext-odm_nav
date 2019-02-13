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
from . import helpers 
import helpers
import datetime
import time
from urlparse import urlparse
import json
import collections
from genshi.template.text import NewTextTemplate
from ckan.lib.base import render
from pprint import pprint
import collections

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

    # IFacets
    def dataset_facets(self, facets_dict, package_type):

        """ Please enter a facet with a order"""

        ordered_facet = [("dataset_type", toolkit._('Search Result For')),
                         ("extras_odm_spatial_range", toolkit._('Country')),
                         ("extras_odm_language", toolkit._('Language')),
                         ('res_format', toolkit._('Formats')),
                         ('organization', toolkit._('Organizations')),
                         ('license_id', toolkit._('License'))]

        return collections.OrderedDict(ordered_facet)

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
        redirects = {
                '/': '/dataset'
            }

        for k, v in redirects.iteritems():
            m.redirect(k, v)

        return m
        # m.connect('dataset_read', '/dataset/{id}',controller='package', action='read', ckan_icon='table')

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
            'odm_nav_tag_for_topic': helpers.tag_for_topic,
            'odm_nav_sanitize_html': helpers.sanitize_html,
            'odm_nav_taxonomy_dictionary': helpers.get_taxonomy_dictionary,
            'odm_nav_localize_resource_url': helpers.localize_resource_url,
            'odm_nav_get_localized_tag': helpers.get_localized_tag,
            'odm_nav_get_localized_tag_string': helpers.get_localized_tag_string,
            'odm_nav_popular_datasets': helpers.popular_datasets,
            'odm_nav_recent_datasets': helpers.recent_datasets,
            'odm_nav_sanitize_html': helpers.sanitize_html,
            'odm_nav_get_all_laws_records': helpers.get_all_laws_records,
            'odm_nav_get_all_laws_records_and_agreements': helpers.get_all_laws_records_and_agreements,
            'odm_nav_get_all_library_records': helpers.get_all_library_records,
            'odm_nav_get_all_agreements': helpers.get_all_agreements,
            'odm_nav_get_all_datasets': helpers.get_all_datasets,
            'odm_nav_get_all_laws_records_complete': helpers.get_all_laws_records_complete,
            'odm_nav_get_all_laws_records_and_agreements_complete': helpers.get_all_laws_records_and_agreements_complete,
            'odm_nav_get_all_library_records_complete': helpers.get_all_library_records_complete,
            'odm_nav_get_all_agreements_complete': helpers.get_all_agreements_complete,
            'odm_nav_get_all_datasets_complete': helpers.get_all_datasets_complete,
            'resource_to_preview_on_dataset_page': helpers.resource_to_preview_on_dataset_page,
            'active_search_link': helpers.active_search_link,
            'extract_wp_menu': helpers.extract_wp_menu,
            'get_menu_json': helpers.get_menu_json,
            'nav_html_parsing': helpers.nav_html_parsing,
            'odm_nav_ckan_url_for_site': helpers.ckan_url_for_site,
        }

    # IPackageController
    def before_create(self, context, resource):
        log.info('before_create')

    def after_create(self, context, pkg_dict):
        log.debug('after_create: %s', pkg_dict['name'])

    def after_update(self, context, pkg_dict):
        log.debug('after_update: %s', pkg_dict['name'])
