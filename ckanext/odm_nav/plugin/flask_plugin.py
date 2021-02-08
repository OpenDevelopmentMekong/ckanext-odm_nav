import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckanext.odm_nav.views import odm_nav_views
import logging
log = logging.getLogger(__name__)


class OdmNavMixinPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IBlueprint)

    # IConfigurer
    def update_config(self, config):
        '''Update plugin config'''

        toolkit.add_template_directory(config, '../templates-2.9')
        toolkit.add_resource('../fanstatic', 'odm_nav')
        toolkit.add_public_directory(config, '../public')

    def get_blueprint(self):
        return [odm_nav_views]

    def get_actions_versions(self):
        """
        Core ckan actions for package activity has been changed for ckan 2.9.1
        :return:
        """
        return {}