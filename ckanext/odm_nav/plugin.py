import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

import collections

from . import helpers

import logging
log = logging.getLogger(__name__)


class OdmNavPlugin(plugins.SingletonPlugin):
    '''OD Mekong Nav plugin.'''

    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IFacets)


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
        m.redirect('/', '/dataset')

        m.connect('odm_nav_thumbnail',
                  '/dataset/{id}/resource/{resource_id}/thumbnail/{file_name}',
                  controller='ckanext.odm_nav.thumbnail:Controller', action='read', ckan_icon='table')
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
            'odm_nav_tag_for_topic': helpers.tag_for_topic,
            'odm_nav_sanitize_html': helpers.sanitize_html,
            'odm_nav_taxonomy_dictionary': helpers.get_taxonomy_dictionary,
            'odm_nav_localize_resource_url': helpers.localize_resource_url,
            'odm_nav_thumbnail_img': helpers.thumbnail_img_url,
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
            'nav_html_parsing': helpers.gen_odm_menu,
            'odm_nav_ckan_url_for_site': helpers.ckan_url_for_site,
            'odm_nav_wp_url_for_site': helpers.wp_url_for_site,
            'odm_nav_country_name_for_site': helpers.country_name_for_site,
            'odm_nav_menu': helpers.odm_nav_menu,
        }


