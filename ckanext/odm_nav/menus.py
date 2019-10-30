import requests
from bs4 import BeautifulSoup

# cache the rendered versions
rendered = {}

def extract_wp_menu(site):
    if site == 'odm':
        site_code = ''
    else:
        site_code = site + '.'

    url = 'https://{}odm-eu.staging.derilinx.com'.format(site_code)
    r = requests.get(url)
    html = r.content

    soup = BeautifulSoup(html, 'html.parser')

    menu = soup.find(id="mega-menu-wrap-header_menu")
    for div in menu.find_all("div", {'class': 'mega-search-wrap'}):
        div.decompose()

    return menu



