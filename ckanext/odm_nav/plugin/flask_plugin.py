import ckan.plugins as plugins
from ckanext.odm_nav.views import odm_nav_views
import logging
log = logging.getLogger(__name__)


class OdmNavMixinPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IBlueprint)

    def get_blueprint(self):
        return [odm_nav_views]

    def get_actions_versions(self):
        """
        Core ckan actions for package activity has been changed for ckan 2.9.1
        :return:
        """
        return {}