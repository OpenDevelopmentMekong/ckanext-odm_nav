from ckan.lib.cli import CkanCommand
from ckanext.odm_nav import model as nav_model
import ckan.plugins.toolkit as toolkit
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

    if toolkit.check_ckan_version(min_version='2.9.0'):
        base_path = os.path.join(os.path.dirname(__file__), 'templates-2.9/home/snippets/')
    else:
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
        elif cmd == "initdb":
            nav_model.init_tables()
        elif cmd == "load_taxonomy":
            self.load_taxonomy()

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
            filename = 'menus/%s_%s_menu.html' % (site, lang)
            if not os.path.exists(os.path.join(self.base_path, 'menus')):
                os.makedir(os.path.join(self.base_path, 'menus'))
            with open(os.path.join(self.base_path, filename), 'w') as f:
                f.write(menus.extract_wp_menu(wp_url, lang))
                print("Wrote: %s" % os.path.join(self.base_path, filename))

    def _parse_taxonomy(self, tax, flatten=None):
        """
        Flatten the childrent elements from the json file
        :param tax: list
        :param flatten: list
        :return: list
        """
        if not flatten:
            flatten = []
        for _x in tax:
            if "children" in _x:
                flatten.append(_x.get('name'))
                self._parse_taxonomy(_x['children'], flatten)
            else:
                flatten.append(_x.get('name'))
        return flatten

    def load_taxonomy(self):
        """
        Load the postgres taxonomy table from json file. Only english taxonomy is loaded.
        Table Name: odm_taxonomy
        :return:
        """
        file_name = "taxonomy_en.json"
        dir_path = os.path.dirname(os.path.realpath(__file__))
        taxonomy_dir = "odm-taxonomy"
        file_full_path = "{}/{}/{}".format(dir_path, taxonomy_dir, file_name)
        print("File path: {}".format(file_full_path))

        try:
            with open(file_full_path, 'r') as tax:
                content = json.load(tax)
                tax.close()

            parent_taxonomy = dict()

            for x in content['children']:
                parent_taxonomy[x.get('name')] = []
            print("Total parent taxonomy: {}".format(len(parent_taxonomy)))

            if not parent_taxonomy:
                raise ValueError("No data found in taxonomy json file")

            for _tax in content.get('children'):
                ls = []
                _parent = _tax.get('name')
                parent_taxonomy[_parent] = self._parse_taxonomy(_tax['children'], ls)

            if parent_taxonomy:
                md = nav_model.Taxonomy
                md.load_table(parent_taxonomy)
        except Exception as e:
            print("Error")
            print(e)

