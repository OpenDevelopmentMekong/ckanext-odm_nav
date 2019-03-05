from ckan.lib.cli import CkanCommand
from ckan.plugins import toolkit

import os
import json

from . import menus
from . import helpers

class OdmNav(CkanCommand):

    """
    Usage::
        paster odm_nav load_menus
           - loads all of the menus for the wp sites.
        paster odm_nav load_menu sitecode
           - Loads the menu for the specific site
    """

    """
    paster --plugin=ckanext-odm_nav odmnav load_menus
    1  paster --plugin=ckanext-vectorstorer vectorstorer add_wms_for_layer post-office-2018 "ODCambodia:Cambodia_post_office"
    2  paster --plugin=ckanext-vectorstorer vectorstorer add_wms_for_layer post-office-2018 "ODCambodia:Cambodia_post_office_kh"
"""

    summary = __doc__.split('\n')[0]
    usage = __doc__
    min_args = 0
    
    base_path = os.path.join(os.path.dirname(__file__), 'public')

    def command(self):
        self._load_config()
        if not self.args or self.args[0] in ['--help', '-h', 'help']:
            print self.__doc__
            return

        cmd = self.args[0]
        if cmd == "load_menus":
            self.load_menus(*self.args[1:])
        elif cmd == "load_menu":
            self.load_site(*self.args[1:])

    def load_menus(self, *args):
        for site in ('odm', 'odc', 'odl', 'odt', 'odmy', 'odv'):
            self.load_site(site)
        menus.rendered = {}
            
    def load_site(self, site, *args):
        print("Loading %s" % site)
        wp_url = helpers.wp_url_for_site(site)
        filename = '%s_nav_items.json' % site
        with open(os.path.join(self.base_path, filename), 'w') as f:
            json.dump(menus.get_menu(wp_url), f, indent=2)
            print("Wrote: %s" % filename)
            


