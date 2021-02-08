import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import logging
log = logging.getLogger(__name__)


class OdmNavMixinPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IRoutes, inherit=True)

    # IConfigurer
    def update_config(self, config):
        '''Update plugin config'''

        toolkit.add_template_directory(config, '../templates')
        toolkit.add_resource('../fanstatic', 'odm_nav')
        toolkit.add_public_directory(config, '../public')

    # IRoutes
    def before_map(self, m):
        m.redirect('/', '/dataset')

        m.connect('odm_nav_thumbnail',
                  '/dataset/{id}/resource/{resource_id}/thumbnail/{file_name}',
                  controller='ckanext.odm_nav.thumbnail:Controller', action='read', ckan_icon='table')

        # Donor report controller
        m.connect('donor_report', '/user/{id}/donor_report',
                  controller='ckanext.odm_nav.controller:DonorReport',
                  action='index')

        m.connect('odm_dataset_new_geoserver_resource', '/dataset/new_geoserver_resource/{id}',
                  controller='ckanext.odm_nav.controller:GeoserverNewWMSResource',
                  action='new_mws_resource'
                  )

        return m

    def get_actions_versions(self):
        """
        Core ckan actions for package activity has been changed for ckan 2.9.1
        :return:
        """
        return {
            'package_activity_list_html': auth.action_wrapper_html('package_activity_list_html', 'package_update'),
            'group_activity_list_html': auth.action_wrapper_html('group_activity_list_html', 'user_is_org_editor'),
            'organization_activity_list_html': auth.action_wrapper_html('organization_activity_list_html',
                                                                        'user_is_org_editor'),
            'recently_changed_packages_activity_list_html': auth.action_wrapper_html(
                'recently_changed_packages_activity_list_html', 'user_list'),
        }


