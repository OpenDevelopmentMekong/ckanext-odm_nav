import requests
from bs4 import BeautifulSoup
import os
import re

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

    s_menu = str(menu).replace('href="/', 'href="%s/' % site_url)

    return s_menu
