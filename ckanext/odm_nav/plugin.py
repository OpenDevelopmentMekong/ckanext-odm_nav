import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

import collections

from . import helpers, auth

import logging
log = logging.getLogger(__name__)

#
# monkey patch resource proxy to not proxy internal items
#

try:
    from ckanext import resourceproxy
    from ckan.common import config


    def _strip_lang(url):
        for lang in ('km', 'my', 'lo', 'th', 'vi', 'en'):
            fragment = '/%s/' % lang
            if fragment in url:
                return url.replace(fragment, '/')
        return url

    resourceproxy.plugin._get_proxified_resource_url = resourceproxy.plugin.get_proxified_resource_url
    def proxy_wrapper(data_dict, proxy_schemes=['http', 'https']):
        ckan_url = config.get('ckan.site_url', '')
        internal_domains = (config.get('ckanext.odm.odm_url',''),
                            config.get('ckanext.odm.odc_url',''),
                            config.get('ckanext.odm.odl_url',''),
                            config.get('ckanext.odm.odmy_url',''),
                            config.get('ckanext.odm.odt_url',''),
                            config.get('ckanext.odm.odv_url',''))
        resource_url = data_dict['resource']['url']
        for url in internal_domains:
            if url in resource_url:
                return _strip_lang(resource_url.replace(url, ckan_url))
        return resourceproxy.plugin._get_proxified_resource_url(data_dict, proxy_schemes)

    resourceproxy.plugin.get_proxified_resource_url = proxy_wrapper
except Exception as msg:
    log.error('Monkeypatching resource proxy failed -- %s' % msg)


class OdmNavPlugin(plugins.SingletonPlugin):
    '''OD Mekong Nav plugin.'''
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IFacets)
    plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.IActions)

    # IFacets
    def dataset_facets(self, facets_dict, package_type):

        """ Please enter a facet with a order"""

        ordered_facet = [("dataset_type", toolkit._('Search Result For')),
                         ("odm_spatial_range_list", toolkit._('Country')),
                         ("odm_language_list", toolkit._('Language')),
                         ('res_format', toolkit._('Formats')),
                         ('organization', toolkit._('Organizations')),
                         ('taxonomy', toolkit._('Topics')),
                         ('license_id', toolkit._('License')),
        ]

        # Three different document type fields.
        if package_type == 'laws_record':
            ordered_facet.append(('odm_document_type', toolkit._('Document Type')))
        if package_type == 'library_record':
            ordered_facet.append(('document_type', toolkit._('Document Type')))
        if package_type == 'laws_record':
            ordered_facet.append(('odm_agreement_document_type', toolkit._('Document Type')))

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
            'odm_nav_get_library_for_doctype': helpers.get_library_for_doctype,
            'resource_to_preview_on_dataset_page': helpers.resource_to_preview_on_dataset_page,
            'active_search_link': helpers.active_search_link,
            'nav_html_parsing': helpers.gen_odm_menu,
            'odm_nav_sitecode': helpers.sitecode,
            'odm_nav_ckan_url_for_site': helpers.ckan_url_for_site,
            'odm_nav_wp_url_for_site': helpers.wp_url_for_site,
            'odm_nav_megamenu_css_url_for_site': helpers.megamenu_css_url_for_site,
            'odm_nav_country_name_for_site': helpers.country_name_for_site,
            'odm_nav_twitter_for_site': helpers.twitter_for_site,
            'odm_nav_contact_for_site': helpers.contact_for_site,
            'odm_nav_facebook_for_site': helpers.facebook_for_site,
            'odm_nav_menu': helpers.odm_nav_menu,
            'odm_menu_path': helpers.odm_menu_path,
            'odm_nav_wms_download': helpers.odm_wms_download,
            'odm_nav_get_title_for_languages_facet': helpers.get_title_for_languages_facet,
            'odm_nav_get_icon_for_dataset_type': helpers.get_icon_for_dataset_type,
            'odm_nav_get_icon_dataset_type_for_facet': helpers.get_icon_dataset_type_for_facet,
            'odm_nav_get_active_url_for_search_result_facet': helpers.get_active_url_for_search_result_facet,
            'odm_nav_taxonomy_paths_from_tags': helpers.taxonomy_paths_from_tags,
            'odm_nav_taxonomy_path_to_name': helpers.taxonomy_path_to_name,
            'odm_nav_tag_list': helpers.get_tag_list,
            'odm_nav_lang_flags': helpers.get_lang_flags,
            'odm_nav_get_ga_tracking_id': helpers.get_ga_tracking_id,
            'odm_nav_convert_num_to_year': helpers.convert_num_to_year,
            'odm_nav_prepare_site_nav_mobile': helpers.prepare_site_nav_mobile,
            # core override
            'linked_user': helpers.linked_user,
        }

    # IAuthFunctions
    def get_auth_functions(self):
        return {
            'user_list': auth.user_list,
            'user_show': auth.user_show,
            'user_is_org_editor': auth.user_is_org_editor,
            }

    # IActions
    def get_actions(self):
        return {
            'package_activity_list': auth.action_wrapper('package_activity_list', 'package_update'),
            'package_activity_list_html': auth.action_wrapper_html('package_activity_list_html', 'package_update'),
            'group_activity_list': auth.action_wrapper('group_activity_list', 'user_is_org_editor'),
            'group_activity_list_html': auth.action_wrapper_html('group_activity_list_html', 'user_is_org_editor'),
            'organization_activity_list': auth.action_wrapper('organization_activity_list', 'user_is_org_editor'),
            'organization_activity_list_html': auth.action_wrapper_html('organization_activity_list_html', 'user_is_org_editor'),
            # shorthand for is_sysadmin
            'recently_changed_packages_activity_list': auth.action_wrapper('recently_changed_packages_activity_list', 'user_list'),
            'recently_changed_packages_activity_list_html': auth.action_wrapper_html('recently_changed_packages_activity_list_html', 'user_list'),
        }
