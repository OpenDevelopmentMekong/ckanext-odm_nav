import requests
from bs4 import BeautifulSoup
import os

# cache the rendered versions
rendered = {}

def extract_wp_menu(site_url, language=None):
    """
    :param wp_site_url: a url to the wordpress site
    :returns: nested array of menu item dicts.
    """

    if not language:
        language = 'en'

    url = os.path.join(site_url, language)

    r = requests.get(url)
    r.raise_for_status()

    html = r.content
    soup = BeautifulSoup(html, 'html.parser')

    menu = soup.find(id="mega-menu-wrap-header_menu")
    for div in menu.find_all("div", {'class': 'mega-search-wrap'}):
        div.decompose()

    return str(menu)

def extract_all_wp_menus():
    sites = [
        'odmy',
        'odc',
        'odt',
        'odv',
        'odl',
        'odm'
    ]

    for site in sites:
        if site == 'odm':
            site_url = 'odm'
        else:
            site_url = site

        current_path = os.path.dirname(os.path.abspath(__file__))
        with open(current_path + "/templates/snippets/{}_menu.html".format(site_url), "w") as file:
            file.write(str(extract_wp_menu(site)))



