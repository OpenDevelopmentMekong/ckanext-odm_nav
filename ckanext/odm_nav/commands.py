from ckan.lib.cli import CkanCommand

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
    paster --plugin=ckanext-odm_nav odm_nav load_menus
"""

    summary = __doc__.split('\n')[0]
    usage = __doc__
    min_args = 0

    base_path = os.path.join(os.path.dirname(__file__), 'templates/home/snippets/')
    lang_map = {'odm':['en'], 'odc':['en','km'], 'odl':['en', 'lo'],
                'odt':['en', 'th'], 'odmy':['en', 'my'], 'odv':['en', 'vi']}

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
        elif cmd == "load_this_site_menu":
            self.load_this_site(*self.args[1:])

    def load_menus(self, *args):
        for site, langs in self.lang_map.items():
            self.load_site(site, langs)
        menus.rendered = {}

    def load_this_site(self):
        from ckan.common import config
        self.load_site(config.get('ckanext.odm.site_code'))

    def load_site(self, site, *args):
        print("Loading %s" % site)
        wp_url = helpers.wp_url_for_site(site)
        langs = self.lang_map[site]
        if args and args[0]:
            langs = args[0]

        for lang in langs:
            filename = '%s_%s_menu.html' % (site, lang)
            with open(os.path.join(self.base_path, filename), 'w') as f:
                f.write(menus.extract_wp_menu(wp_url, lang))
                print("Wrote: %s" % filename)
