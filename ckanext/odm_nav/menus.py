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



