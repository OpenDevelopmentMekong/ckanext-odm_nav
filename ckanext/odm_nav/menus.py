import requests
from bs4 import BeautifulSoup
import os
import re
from urlparse import urlparse, urlunparse

# cache the rendered versions
rendered = {}


def _replace_urls_language_specific(url, language):
    _lang_codes = {'th', 'en', 'my', 'lo', 'km', 'vi'}
    try:
        _url = urlparse(url)
        if _url.path:
            temp = list(_url)
            _path = temp[2].split("/")
            if set(_path).intersection(_lang_codes):
                _path[1] = language
            else:
                _path.insert(1, language)
            temp[2] = "/".join(_path)	
            return urlunparse(temp)
        return url
    except Exception as e:
        print(e)
        return url
    

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
    
    for a in menu.find_all('a', href=True):
        a['href'] = _replace_urls_language_specific(a['href'], language)

    s_menu = str(menu).replace('href="/', 'href="%s/' % site_url)

    return s_menu
