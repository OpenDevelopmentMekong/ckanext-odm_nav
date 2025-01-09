import click
from ckanext.odm_nav import model as nav_model
import os
import json

from . import menus
from . import helpers

BASE_PATH = os.path.join(os.path.dirname(__file__), 'templates/home/snippets/')

LANG_MAP = {'odm':['en'], 'odc':['en','km'], 'odl':['en', 'lo'],
            'odt':['en', 'th'], 'odmy':['en', 'my'], 'odv':['en', 'vi']}

@click.group()
def odm_nav():
    pass

@odm_nav.command()
def load_menus():
    """Load all of the menus for the WP sites"""
    for site, langs in LANG_MAP.items():
        load_site(site, langs)

@odm_nav.command()
@click.argument('sitecode')
def load_menu(sitecode):
    """Load the menu for a specific WP site"""
    load_site(sitecode)

@odm_nav.command()
def load_this_site_menu():
    from ckan.common import config
    load_site(config.get('ckanext.odm.site_code'))


@odm_nav.command()
def initdb():
    nav_model.init_tables()

@odm_nav.command()
def load_taxonomy():
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

    with open(file_full_path, 'r') as tax:
        content = json.load(tax)

    parent_taxonomy = dict()

    for x in content['children']:
        parent_taxonomy[x.get('name')] = []
    print("Total parent taxonomy: {}".format(len(parent_taxonomy)))

    if not parent_taxonomy:
        raise ValueError("No data found in taxonomy json file")

    for _tax in content.get('children'):
        ls = []
        _parent = _tax.get('name')
        parent_taxonomy[_parent] = _parse_taxonomy(_tax['children'], ls)

    if parent_taxonomy:
        md = nav_model.Taxonomy
        md.load_table(parent_taxonomy)



def load_site(site, langs=None):
    print("Loading %s" % site)
    wp_url = helpers.wp_url_for_site(site)
    langs = langs or LANG_MAP[site]

    for lang in langs:
        filename = 'menus/%s_%s_menu.html' % (site, lang)
        if not os.path.exists(os.path.join(BASE_PATH, 'menus')):
            os.mkdir(os.path.join(BASE_PATH, 'menus'))
        with open(os.path.join(BASE_PATH, filename), 'w') as f:
            f.write(menus.extract_wp_menu(wp_url, lang))
            print("Wrote: %s" % os.path.join(BASE_PATH, filename))


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
